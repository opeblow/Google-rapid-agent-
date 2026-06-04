import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME: str = os.getenv("DATABASE_NAME", "worldcup_2026")
AGENT_SERVICE_URL: str = os.getenv("AGENT_SERVICE_URL", "http://localhost:8001")
