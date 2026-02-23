// chat.js

let isChatOpen = false;
let isLiveAgent = false;

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// ✅ NEW: Safe Open Function (Won't close if already open)
function openChat() {
    if (isChatOpen) return; // Already open, do nothing
    
    const window = document.getElementById('chat-window');
    const badge = document.getElementById('chat-badge');
    
    isChatOpen = true;
    window.classList.remove('hidden');
    badge.classList.add('hidden');
    
    // Play a gentle notification sound (optional)
    // new Audio('/static/ping.mp3').play().catch(e => {}); 
}

function toggleChat() {
    const window = document.getElementById('chat-window');
    const badge = document.getElementById('chat-badge');
    
    isChatOpen = !isChatOpen;
    
    if (isChatOpen) {
        window.classList.remove('hidden');
        badge.classList.add('hidden');
        setTimeout(() => document.getElementById('chat-input').focus(), 100);
    } else {
        window.classList.add('hidden');
    }
}

async function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;

    appendMessage(message, 'user');
    input.value = '';

    try {
        const response = await fetch('/api/chat/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        if (data.escalation_required) {
            escalateChat();
        } else {
            appendMessage(data.reply, 'bot');
        }

    } catch (error) {
        console.error('Chat Error:', error);
        appendMessage("Sorry, I'm having trouble connecting.", 'system');
    }
}

function appendMessage(text, sender) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = "flex items-start gap-2 " + (sender === 'user' ? "flex-row-reverse" : "");

    let avatar = sender === 'user' ? '👤' : (isLiveAgent ? '👨‍💼' : '🤖');
    if (sender === 'system') avatar = '⚠️';

    const bubbleClass = sender === 'user'
        ? "bg-blue-600 text-white rounded-tr-none"
        : "bg-white text-gray-800 border border-gray-200 rounded-tl-none";

    const safeText = sender === 'user' ? escapeHtml(text) : text;

    div.innerHTML = `
        <div class="h-6 w-6 rounded-full bg-slate-200 flex items-center justify-center text-xs flex-shrink-0">${avatar}</div>
        <div class="${bubbleClass} p-2 rounded-lg shadow-sm max-w-[85%]">
            ${safeText}
        </div>
    `;
    
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

async function escalateChat() {
    isLiveAgent = true;
    document.getElementById('chat-title').innerText = "Live Support";
    document.getElementById('chat-subtitle').innerText = "Connecting to Agent...";
    document.getElementById('agent-status-dot').classList.replace('bg-green-400', 'bg-yellow-400');
    document.getElementById('escalation-banner').classList.add('hidden');
    
    appendMessage("Connecting you to a human agent...", 'system');

    try {
        await fetch('/api/chat/escalate', { method: 'POST' });
        
        setTimeout(() => {
            document.getElementById('chat-subtitle').innerText = "Agent Notified";
            document.getElementById('agent-status-dot').classList.replace('bg-yellow-400', 'bg-green-400');
            appendMessage("An agent has been notified via Telegram. They will reply shortly.", 'system');
            startPolling();
        }, 1500);
        
    } catch (error) {
        console.error("Escalation failed", error);
    }
}

let pollInterval;
let pollFailures = 0;
const MAX_POLL_FAILURES = 3;

function startPolling() {
    if (pollInterval) return;
    pollFailures = 0;

    console.log("Started listening for agent replies...");
    pollInterval = setInterval(async () => {
        try {
            const response = await fetch('/api/chat/updates');
            const data = await response.json();

            if (data.reply) {
                pollFailures = 0;
                appendMessage(data.reply, 'agent');
            } else {
                pollFailures++;
                if (pollFailures >= MAX_POLL_FAILURES) {
                    stopPolling();
                    appendMessage("The agent is currently busy. Please allow up to 30 minutes for a response. We appreciate your patience.", 'system');
                }
            }
        } catch (e) {
            pollFailures++;
            console.error(`Polling error (${pollFailures}/${MAX_POLL_FAILURES})`, e);
            if (pollFailures >= MAX_POLL_FAILURES) {
                stopPolling();
                appendMessage("The agent is currently busy. Please allow up to 30 minutes for a response. We appreciate your patience.", 'system');
            }
        }
    }, 3000);
}

function stopPolling() {
    if (pollInterval) {
        clearInterval(pollInterval);
        pollInterval = null;
    }
}

// --- SSE Listener (Original Method) ---
if (window.htmx) {
    document.body.addEventListener('htmx:sseMessage', (e) => {
        if (e.detail.type === 'chat-auto-open') {
            console.log("🤖 Chat Auto-Open Triggered (SSE)!");
            openChat();
            // Optional: Only show message if it's new
            const messages = document.getElementById('chat-messages');
            if (!messages.innerHTML.includes("trouble")) {
                 appendMessage("I noticed you might be having some trouble. Can I help you with that error?", 'bot');
            }
        }
    });
}