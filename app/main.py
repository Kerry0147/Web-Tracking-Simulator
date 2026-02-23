import json
import os
import uuid
import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Request, Form, HTTPException, Body, Depends, Response, BackgroundTasks
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette.middleware.sessions import SessionMiddleware
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

# --- Imports (Layers 4-7) ---
from app.engine.session_manager import session_manager
from app.engine.behavior_tracker import tracker
from app.skills.routing_skills import router
from app.engine.stream_manager import stream_manager
from app.models import Segment, Intent, Sentiment, NBAState
from app.skills.read_skills import get_customer_profile, get_customer_history

# --- Chat Imports (Layer 7) ---
from app.chat.handler import handle_message
from app.chat.telegram_bridge import send_escalation, check_for_replies

# Load Environment Variables (for Telegram/LLM)
load_dotenv()

# --- Lifespan & Data Loading ---
mock_db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        data_path = os.path.join("app", "data", "mock_data.json")
        with open(data_path, "r") as f:
            mock_db.update(json.load(f))
        print("✅ System Online: Mock data loaded successfully.")
    except Exception as e:
        print(f"❌ Failed to load mock data: {e}")
    yield
    mock_db.clear()

app = FastAPI(lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key="echo-poc-secret-key")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Core Helper Functions ---

def ensure_session_id(request: Request) -> str:
    """Ensures a session ID exists in the cookie and session manager."""
    session_id = request.session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        request.session["session_id"] = session_id
    
    # Ensure it exists in our internal RAM manager too
    session_manager.get_or_create(session_id)
    return session_id

def common_context(request: Request):
    """
    Base context for all templates. 
    Includes 'Session Repair' logic to fix Split-Brain login issues.
    """
    # 1. Ensure we have a session ID
    session_id = ensure_session_id(request)
    session = session_manager.get_or_create(session_id)
    
    # ✅ FIX: Reset the 'One-Shot' chat trigger whenever a full page loads.
    # This allows the demo to run multiple times without restarting the server.
    session.chat_triggered = False

    # 2. Check for Customer ID in Cookie (Primary) OR RAM (Fallback)
    customer_id = request.session.get("customer_id")
    
    if not customer_id and session.customer_id:
        # Repair: Found in RAM but not Cookie
        customer_id = session.customer_id
        request.session["customer_id"] = customer_id

    # 3. Load User Data & History
    user_profile = None
    history = None
    
    if customer_id:
        user_profile = get_customer_profile(customer_id, mock_db)
        history = get_customer_history(customer_id, mock_db)

    # 4. Run AI Classification
    classification, nba = router.execute_classification(session, mock_db)

    return {
        "request": request,
        "logged_in": user_profile is not None,
        "user": user_profile, 
        "session": session,
        "classification": classification,
        "nba": nba,
        "history": history
    }

# --- Dashboard Renderer (Layer 6) ---

def render_dashboard_partials(request: Request, session_id: str, classification=None, nba=None):
    """Renders all dashboard HTML partials based on current state for SSE."""
    session = session_manager.get_session(session_id)
    if not session:
        return {}

    # 1. Run Classification & NBA (skip if pre-computed results were passed in)
    if classification is None or nba is None:
        classification, nba = router.execute_classification(session, mock_db)

    # 2. Prepare Context (Must match common_context structure)
    ctx = {
        "request": request,
        "classification": classification,
        "nba": nba,
        "session": session,
        "user": None,
        "history": None
    }
    
    # Add user data if logged in
    if session.customer_id:
        ctx["user"] = get_customer_profile(session.customer_id, mock_db)
        ctx["history"] = get_customer_history(session.customer_id, mock_db)

    # 3. Render Templates
    return {
        "nba": templates.get_template("right/partials/nba_card.html").render(ctx),
        "vitals": templates.get_template("right/partials/vitals.html").render(ctx),
        "categorization": templates.get_template("right/partials/categorization.html").render(ctx),
        "timeline": templates.get_template("right/partials/timeline.html").render(ctx),
        "history": templates.get_template("right/partials/history.html").render(ctx)
    }

# --- SSE Endpoint (Layer 6) ---

@app.get("/api/dashboard-stream")
async def dashboard_stream(request: Request):
    """SSE endpoint that pushes real-time dashboard updates."""
    session_id = ensure_session_id(request)
    queue = await stream_manager.connect(session_id)
    
    # Send initial state immediately upon connection
    initial_partials = render_dashboard_partials(request, session_id)
    for event_type, html in initial_partials.items():
        await queue.put({"event": f"{event_type}-update", "data": html})

    async def event_generator():
        try:
            while True:
                message = await queue.get()
                yield message
        except asyncio.CancelledError:
            stream_manager.disconnect(session_id, queue)

    return EventSourceResponse(event_generator())

# --- Tracking Endpoint (Layer 4 + 6 + 7) ---

@app.post("/api/track-event")
async def track_event(request: Request, event_data: dict = Body(...)):
    """
    Receives event, processes logic, triggers SSE update, and checks for Chat Auto-Open.
    """
    session_id = ensure_session_id(request)
    session = session_manager.get_or_create(session_id)
    
    # 1. Update Session State (Layer 4)
    tracker.process_event(session, event_data)

    # 2. Classify ONCE (reused for dashboard render + chat trigger check)
    classification, nba = router.execute_classification(session, mock_db)

    # 3. Render Updated Dashboard (Layer 6) — pass pre-computed results
    updated_partials = render_dashboard_partials(request, session_id, classification, nba)

    # 4. Push to SSE Stream
    for event_type, html in updated_partials.items():
        await stream_manager.broadcast_to_session(session_id, {
            "event": f"{event_type}-update",
            "data": html
        })

    # 5. CHECK FOR AUTO-OPEN (Layer 7 Logic) — reuse same classification/nba
    if nba.should_trigger_chat and not getattr(session, 'chat_triggered', False):
        session.chat_triggered = True 
        await stream_manager.broadcast_to_session(session_id, {
            "event": "chat-auto-open",
            "data": "true"
        })
    
    return {"status": "ok"}

# --- Chat Routes (Layer 7) ---

@app.post("/api/chat/send")
async def chat_send(request: Request, body: dict = Body(...)):
    """Receives user message, runs handler, returns AI response."""
    message = body.get("message", "")
    ctx = common_context(request)
    
    response_data = handle_message(
        message, 
        ctx["session"], 
        ctx["user"]
    )
    return response_data

@app.post("/api/chat/escalate")
async def chat_escalate(request: Request, background_tasks: BackgroundTasks):
    """Triggers Telegram notification in background."""
    ctx = common_context(request)
    # Run in background to not block the UI
    background_tasks.add_task(send_escalation, ctx)
    return {"status": "escalated"}

@app.get("/api/chat/updates")
async def chat_updates():
    """Polls Telegram for operator replies and returns them to the frontend."""
    reply = await check_for_replies()
    if reply:
        return {"reply": reply}
    return {"reply": None}

# --- AI Mode Toggle (Phase 2) ---

@app.post("/api/toggle-mode")
async def toggle_mode(body: dict = Body(...)):
    """Switches AI_MODE at runtime without restarting the server."""
    from app import config as app_config
    new_mode = body.get("mode", "phase1")
    if new_mode not in ("phase1", "phase2"):
        return JSONResponse({"error": "Invalid mode"}, status_code=400)
    app_config.AI_MODE = new_mode
    print(f"AI_MODE switched to: {new_mode}")
    return {"mode": new_mode}

@app.get("/api/current-mode")
async def current_mode():
    """Returns the current AI_MODE."""
    from app import config as app_config
    return {"mode": app_config.AI_MODE}

# --- Authentication Routes (Layer 3 - Updated with HX-Redirect) ---

@app.post("/login")
async def login(request: Request, email: str = Form(...), password: str = Form(...)):
    """Validate credentials and use HX-Redirect to force a full page reload."""
    creds = mock_db.get("login_credentials", {})
    
    if email == creds.get("email") and password == creds.get("password"):
        customer_id = creds.get("customer_id")
        
        # 1. Set Session Cookie
        request.session["customer_id"] = customer_id
        
        # 2. Link Session in RAM
        session_id = ensure_session_id(request)
        session_manager.update_customer(session_id, customer_id)
        
        # 3. Trigger Dashboard Update via SSE
        partials = render_dashboard_partials(request, session_id)
        for event, html in partials.items():
            await stream_manager.broadcast_to_session(session_id, {"event": f"{event}-update", "data": html})

        # 4. Use HX-Redirect header to force browser reload (Fixes Split-Brain)
        response = Response()
        response.headers["HX-Redirect"] = "/"
        return response
    
    return HTMLResponse('<div class="text-red-500 text-sm mt-2">Invalid credentials</div>', status_code=401)

@app.post("/logout")
async def logout(request: Request):
    """Clear session and force reload via HX-Redirect."""
    session_id = request.session.get("session_id")
    if session_id:
        session_manager.remove_session(session_id)

    request.session.clear()
    
    response = Response()
    response.headers["HX-Redirect"] = "/"
    return response

# --- Content Routes (Layers 1-3) ---

@app.get("/")
async def home(request: Request):
    ctx = common_context(request)
    ctx.update({"page": "home", "products": mock_db.get("products", {})})
    return templates.TemplateResponse("left/home.html", ctx)

@app.get("/products/{category}")
async def product_category(request: Request, category: str):
    ctx = common_context(request)
    products = mock_db.get("products", {}).get(category, [])
    titles = {
        "gaming_laptops": "Gaming Laptops",
        "workstations": "Workstations",
        "office_laptops": "Office Laptops",
        "tablets": "Tablets"
    }
    ctx.update({
        "page": "products",
        "category_slug": category,
        "category_title": titles.get(category, "Products"),
        "products": products
    })
    return templates.TemplateResponse("left/product_detail.html", ctx)

@app.get("/troubleshooting")
async def troubleshooting(request: Request):
    ctx = common_context(request)
    ctx.update({"page": "troubleshooting"})
    return templates.TemplateResponse("left/troubleshooting.html", ctx)

@app.get("/troubleshooting/{category}")
async def troubleshooting_list(request: Request, category: str):
    ctx = common_context(request)
    ctx.update({
        "page": "troubleshooting",
        "category": category.title(),
        "articles": mock_db.get("kb_articles", {}).get(category.lower(), [])
    })
    return templates.TemplateResponse("left/troubleshooting_list.html", ctx)

@app.get("/troubleshooting/{category}/{article_id}")
async def kb_article(request: Request, category: str, article_id: str):
    ctx = common_context(request)
    articles = mock_db.get("kb_articles", {}).get(category.lower(), [])
    article = next((a for a in articles if a["id"] == article_id), None)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    ctx.update({
        "page": "troubleshooting",
        "category": category.title(),
        "article": article
    })
    return templates.TemplateResponse("left/kb_article.html", ctx)

@app.get("/warranty")
async def warranty(request: Request):
    ctx = common_context(request)
    ctx.update({"page": "warranty"})
    
    if ctx["logged_in"]:
        # Attach warranties to devices for the view
        # We copy dicts to avoid mutating the mock DB permanently in RAM
        customer_id = request.session["customer_id"]
        user_devices = [d.copy() for d in mock_db.get("devices", []) if d["customer_id"] == customer_id]
        
        for device in user_devices:
             w = next((w for w in mock_db.get("warranties", []) if w["device_id"] == device["id"]), None)
             device["warranty"] = w 
        ctx["devices"] = user_devices
            
    return templates.TemplateResponse("left/warranty.html", ctx)

@app.get("/case-status")
async def case_status(request: Request):
    ctx = common_context(request)
    ctx.update({"page": "case_status"})
    
    if ctx["logged_in"]:
        customer_id = request.session["customer_id"]
        user_cases = [c.copy() for c in mock_db.get("cases", []) if c["customer_id"] == customer_id]
        
        for case in user_cases:
            if case.get("linked_case_id"):
                    linked = next((c for c in mock_db.get("cases", []) if c["id"] == case["linked_case_id"]), None)
                    case["linked_case"] = linked
            
            d = next((d for d in mock_db.get("devices", []) if d["id"] == case.get("device_id")), None)
            case["device_name"] = d["product_name"] if d else "Unknown"
        
        ctx["cases"] = user_cases
            
    return templates.TemplateResponse("left/case_status.html", ctx)

# --- Mock API Endpoints ---
@app.post("/api/warranty-lookup")
async def warranty_lookup(request: Request):
    return HTMLResponse('<div class="p-4 bg-yellow-50 text-yellow-800 rounded-md border border-yellow-200">🔍 Mock Search: Device not found (Guest Mode)</div>')

@app.post("/api/case-lookup")
async def case_lookup(request: Request):
    return HTMLResponse('<div class="p-4 bg-yellow-50 text-yellow-800 rounded-md border border-yellow-200">🔍 Mock Search: Case not found (Guest Mode)</div>')