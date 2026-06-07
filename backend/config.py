import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# Provider: "vertex_ai" (default) or "ai_studio"
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "vertex_ai").lower()

# Vertex AI settings
VERTEX_AI_PROJECT: str | None = os.getenv("VERTEX_AI_PROJECT")
VERTEX_AI_LOCATION: str = os.getenv("VERTEX_AI_LOCATION", "us-central1")

# AI Studio fallback (used only when LLM_PROVIDER=ai_studio)
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")

GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")

MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "worldcup_2026")

if LLM_PROVIDER == "vertex_ai":
    if not VERTEX_AI_PROJECT:
        logger.warning("VERTEX_AI_PROJECT is not set. Vertex AI will use Application Default Credentials (ADC) project.")
else:
    if not GOOGLE_API_KEY:
        logger.warning("GOOGLE_API_KEY is not set. The agent will not function until it is configured.")
