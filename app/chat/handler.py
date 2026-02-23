import json
from typing import Dict, Any

import anthropic

from app import config as app_config
from app.skills.read_skills import get_customer_profile, check_warranty_status, get_customer_history
from app.engine.llm_client import build_session_context


# --- Phase 1 Handler (preserved intact, renamed) ---

def _phase1_handle_message(message: str, session_state: Any, customer_data: Any) -> Dict[str, Any]:
    """
    Analyzes user message and returns a hardcoded response or escalation trigger.
    """
    msg = message.lower()

    # 1. Escalation Keywords
    if any(k in msg for k in ["agent", "human", "person", "representative", "transfer"]):
        return {
            "reply": "<Hard Code> I can certainly transfer you to a human agent.",
            "escalation_required": True
        }

    # 2. Contextual Responses (Hardcoded Phase 1)
    if "warranty" in msg or "expired" in msg:
        return {
            "reply": "<Hard Code> I can see you're asking about warranty coverage. Let me look into your account details. It looks like your GX-7500 warranty expired on 2026-01-15.",
            "escalation_required": False
        }

    if "flickering" in msg or "monitor" in msg or "screen" in msg:
        return {
            "reply": "<Hard Code> I understand you're experiencing display issues. Based on your activity, I see you've been looking at article KB-MON-002. Did those steps help?",
            "escalation_required": False
        }

    if "price" in msg or "cost" in msg or "buy" in msg:
         return {
            "reply": "<Hard Code> I can help with product pricing. The ProBook GX-7500 is currently listed at $2,499. Would you like to check stock?",
            "escalation_required": False
        }

    # 3. Default Fallback
    return {
        "reply": "<Hard Code> Thank you for reaching out. I am the ProBook AI. How can I assist you today?",
        "escalation_required": False
    }


# --- Phase 2 LLM Chat Handler ---

CHAT_SYSTEM_PROMPT = """You are the ProBook AI Assistant, a helpful customer support agent for ProBook Electronics (laptops and tablets).

CONTEXT PROVIDED:
- Customer profile (if logged in): name, tier, devices, warranty status
- Current session: pages visited, behavioral analysis, sentiment
- Support history: past cases, interaction logs

RULES:
- Be helpful, concise, and professional
- Reference specific customer data when relevant (e.g., "I can see your GX-7500's warranty expired on...")
- If the customer mentions wanting a human agent, set escalation_required to true
- Do NOT prefix responses with "<Hard Code>"
- Keep responses under 3 sentences unless the customer asks for detail
- You have access to tools to look up customer data - use them when relevant

Respond with JSON:
{
  "reply": "<your response text>",
  "escalation_required": false
}"""

CHAT_TOOLS = [
    {
        "name": "get_customer_profile",
        "description": "Returns customer name, tier, LTV, and registered devices with warranty status.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up"
                }
            },
            "required": ["customer_id"]
        }
    },
    {
        "name": "check_warranty_status",
        "description": "Returns warranty records for a customer or specific device serial number.",
        "input_schema": {
            "type": "object",
            "properties": {
                "identifier": {
                    "type": "string",
                    "description": "Customer ID or device serial number"
                },
                "is_serial": {
                    "type": "boolean",
                    "description": "True if identifier is a serial number, false if customer ID"
                }
            },
            "required": ["identifier"]
        }
    },
    {
        "name": "get_customer_history",
        "description": "Returns historical sessions and support cases for a customer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "The customer ID to look up"
                }
            },
            "required": ["customer_id"]
        }
    }
]


def _execute_tool(tool_name: str, tool_input: dict) -> str:
    """Executes a read_skills function and returns the result as a JSON string."""
    # Lazy import to avoid circular dependency
    from app.main import mock_db

    if tool_name == "get_customer_profile":
        result = get_customer_profile(tool_input["customer_id"], mock_db)
        if result:
            customer = result["customer"]
            devices = result["devices"]
            return json.dumps({
                "customer": {"name": customer.name, "email": customer.email, "tier": customer.tier, "lifetime_value": customer.lifetime_value},
                "devices": [{"product_name": d.product_name, "serial_number": d.serial_number, "purchase_date": d.purchase_date} for d in devices]
            })
        return json.dumps({"error": "Customer not found"})

    elif tool_name == "check_warranty_status":
        is_serial = tool_input.get("is_serial", False)
        warranties = check_warranty_status(tool_input["identifier"], mock_db, is_serial=is_serial)
        return json.dumps([
            {"id": w.id, "device_id": w.device_id, "status": w.status, "start_date": w.start_date, "end_date": w.end_date, "type": w.type}
            for w in warranties
        ])

    elif tool_name == "get_customer_history":
        result = get_customer_history(tool_input["customer_id"], mock_db)
        sessions = result.get("sessions", [])
        cases = result.get("cases", [])
        return json.dumps({
            "sessions": [{"date": s.date, "primary_intent": s.primary_intent.value, "sentiment": s.sentiment.value, "outcome": s.outcome} for s in sessions],
            "cases": [{"id": c.id, "subject": c.subject, "status": c.status, "creation_date": c.creation_date} for c in cases]
        })

    return json.dumps({"error": f"Unknown tool: {tool_name}"})


def _build_customer_context_for_chat(customer_data: Any, session_state: Any) -> str:
    """Builds customer context string to include in the chat system prompt."""
    if not customer_data:
        return "\nCustomer: Anonymous visitor (not logged in)."

    lines = []
    customer = customer_data.get("customer")
    if customer:
        lines.append(f"\nCustomer: {customer.name} (Tier: {customer.tier}, LTV: ${customer.lifetime_value:,.2f})")

    devices = customer_data.get("devices", [])
    if devices:
        lines.append("Registered devices:")
        for d in devices:
            warranty_info = ""
            if d.warranty:
                warranty_info = f" | Warranty: {d.warranty.get('status', 'Unknown')} (expires {d.warranty.get('end_date', 'N/A')})"
            elif hasattr(d, 'warranty') and d.warranty:
                warranty_info = f" | Warranty: {d.warranty}"
            lines.append(f"  - {d.product_name} (SN: {d.serial_number}){warranty_info}")

    # Session context
    if session_state:
        context = build_session_context(session_state, None)
        lines.append(f"\nCurrent session behavioral data:\n{context}")

    return "\n".join(lines)


def _llm_handle_message(message: str, session_state: Any, customer_data: Any) -> Dict[str, Any]:
    """Handles chat message using Claude with tool use."""
    client = anthropic.Anthropic(api_key=app_config.ANTHROPIC_API_KEY, timeout=app_config.LLM_TIMEOUT)

    # Build enriched system prompt with customer context
    system_prompt = CHAT_SYSTEM_PROMPT
    customer_context = _build_customer_context_for_chat(customer_data, session_state)
    if customer_context:
        system_prompt += f"\n\nCURRENT CUSTOMER CONTEXT:{customer_context}"

    # Determine customer_id for tool hints
    customer_id = None
    if session_state and hasattr(session_state, 'customer_id'):
        customer_id = session_state.customer_id

    messages = [{"role": "user", "content": message}]

    # Agentic loop: handle tool_use responses
    max_iterations = 5
    for _ in range(max_iterations):
        response = client.messages.create(
            model=app_config.LLM_MODEL,
            max_tokens=app_config.LLM_MAX_TOKENS,
            system=system_prompt,
            messages=messages,
            tools=CHAT_TOOLS
        )

        # Check if the model wants to use tools
        if response.stop_reason == "tool_use":
            # Process all tool use blocks
            assistant_content = response.content
            tool_results = []

            for block in assistant_content:
                if block.type == "tool_use":
                    tool_result = _execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result
                    })

            # Add assistant response and tool results to conversation
            messages.append({"role": "assistant", "content": assistant_content})
            messages.append({"role": "user", "content": tool_results})
            continue

        # Final text response — parse as JSON
        for block in response.content:
            if hasattr(block, 'text'):
                raw_text = block.text.strip()

                # Handle markdown code blocks
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("```")[1]
                    if raw_text.startswith("json"):
                        raw_text = raw_text[4:]
                    raw_text = raw_text.strip()

                try:
                    data = json.loads(raw_text)
                    return {
                        "reply": data.get("reply", raw_text),
                        "escalation_required": bool(data.get("escalation_required", False))
                    }
                except json.JSONDecodeError:
                    # If Claude didn't return JSON, use the raw text
                    return {
                        "reply": raw_text,
                        "escalation_required": False
                    }

        # If we got here with no text block, return a default
        break

    return {
        "reply": "I apologize, I'm having trouble processing your request. Let me connect you with a team member.",
        "escalation_required": False
    }


# --- Public API (AI_MODE toggle) ---

def handle_message(message: str, session_state: Any, customer_data: Any) -> Dict[str, Any]:
    """Routes to Phase 1 or Phase 2 handler based on AI_MODE."""
    if app_config.AI_MODE != "phase2":
        return _phase1_handle_message(message, session_state, customer_data)

    try:
        return _llm_handle_message(message, session_state, customer_data)
    except Exception as e:
        print(f"[WARNING] Chat LLM fallback: {e}")
        return _phase1_handle_message(message, session_state, customer_data)
