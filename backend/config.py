import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

# LLM provider — OpenRouter (OpenAI-compatible), used with a Google model
OPENROUTER_API_KEY: str | None = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "google/gemini-3-flash-preview")
OPENROUTER_BASE_URL: str = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "worldcup_2026")

if not OPENROUTER_API_KEY:
    logger.warning("OPENROUTER_API_KEY is not set. The agent will not function until it is configured.")
