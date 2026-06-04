import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY")
MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "worldcup_2026")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY is not set. Agent will not function until it is configured.")
