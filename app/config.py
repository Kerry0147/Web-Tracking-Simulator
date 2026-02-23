import os
from dotenv import load_dotenv

load_dotenv()

AI_MODE = os.getenv("AI_MODE", "phase1")          # Default: safe hardcoded mode
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MODEL = "claude-haiku-4-5-20251001"
LLM_TIMEOUT = 10                                    # seconds — fail fast for SSE responsiveness
LLM_MAX_TOKENS = 1024
