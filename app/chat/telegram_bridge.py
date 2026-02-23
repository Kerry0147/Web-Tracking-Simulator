import os
import httpx
from typing import Any, Optional

# API URLs
TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage"
TELEGRAM_UPDATES_URL = "https://api.telegram.org/bot{}/getUpdates"

# Track the last processed update ID so we only return new replies
_last_update_id: int = 0

# Force IPv4 — IPv6 connections to Telegram are blocked on some networks
_ipv4_transport = httpx.AsyncHTTPTransport(local_address="0.0.0.0")

async def send_escalation(context: Any):
    """
    Formats the session state and sends a formatted alert to Telegram.
    """
    # 1. READ & CLEAN CREDENTIALS
    raw_token = os.getenv("TELEGRAM_BOT_TOKEN", "")
    raw_chat_id = os.getenv("TELEGRAM_CHAT_ID", "")
    token = raw_token.strip()
    chat_id = raw_chat_id.strip()

    if not token or not chat_id:
        print("ERROR: Missing Telegram credentials in .env")
        return

    # 2. PREPARE DATA
    try:
        user_name = "Anonymous"
        user_tier = "Guest"

        user_context = context.get("user")
        if user_context:
            customer_obj = user_context.get("customer")
            if customer_obj:
                if hasattr(customer_obj, "name"):
                    user_name = customer_obj.name
                    user_tier = customer_obj.tier
                elif isinstance(customer_obj, dict):
                    user_name = customer_obj.get("name", "Anonymous")
                    user_tier = customer_obj.get("tier", "Guest")

        session = context.get("session")
        visit_count = len(session.events) if session else 0
        classification = context.get("classification")
        sentiment = "Unknown"
        if classification and hasattr(classification, "sentiment"):
             sentiment = classification.sentiment.value

        text = (
            f"🚨 <b>ESCALATION REQUEST</b>\n\n"
            f"👤 <b>User:</b> {user_name} ({user_tier})\n"
            f"😤 <b>Sentiment:</b> {sentiment}\n"
            f"📊 <b>Activity:</b> {visit_count} events\n"
            f"<i>User requested human agent.</i>"
        )
    except Exception as e:
        print(f"Error preparing message: {e}")
        return

    # 3. SEND REQUEST (forced IPv4)
    print(f"Connecting to Telegram API (IPv4, Timeout: 30s)...")

    async with httpx.AsyncClient(timeout=30.0, transport=_ipv4_transport, trust_env=True) as client:
        try:
            url = TELEGRAM_API_URL.format(token)
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML"
            }

            response = await client.post(url, json=payload)

            if response.status_code == 200:
                print("Telegram Notification Sent Successfully!")
            else:
                print(f"Telegram API Error: {response.status_code} - {response.text}")

        except httpx.ConnectTimeout:
            print(f"TIMEOUT: Could not reach Telegram within 30 seconds.")
        except httpx.ConnectError as e:
            print(f"CONNECTION ERROR: {e}")
        except Exception as e:
            print(f"Unexpected Error: {e}")


async def check_for_replies() -> Optional[str]:
    """
    Polls the Telegram Bot API for new messages from the operator.
    Returns the latest reply text, or None if no new messages.
    """
    global _last_update_id

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = os.getenv("TELEGRAM_CHAT_ID", "").strip()

    if not token or not chat_id:
        return None

    async with httpx.AsyncClient(timeout=10.0, transport=_ipv4_transport, trust_env=True) as client:
        try:
            params = {"offset": _last_update_id + 1, "timeout": 0}
            response = await client.get(TELEGRAM_UPDATES_URL.format(token), params=params)

            if response.status_code != 200:
                return None

            data = response.json()
            results = data.get("result", [])

            latest_reply = None
            for update in results:
                update_id = update.get("update_id", 0)
                if update_id > _last_update_id:
                    _last_update_id = update_id

                msg = update.get("message", {})
                # Only accept replies from the operator's chat
                if str(msg.get("chat", {}).get("id")) == chat_id:
                    text = msg.get("text", "")
                    if text:
                        latest_reply = text

            return latest_reply

        except Exception as e:
            print(f"Telegram poll error: {e}")
            return None
