import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger("start_hf")

PORT = int(os.environ.get("PORT", 8000))
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")


def seed_database():
    logger.info("Seeding match data...")
    try:
        result = subprocess.run(
            [sys.executable, os.path.join(BACKEND_DIR, "seed.py")],
            capture_output=True, text=True, timeout=60,
        )
        for line in result.stdout.strip().splitlines():
            if line.strip():
                logger.info("seed | %s", line.strip())
        if result.returncode != 0:
            logger.warning("Seed exited with code %d — may need manual seeding", result.returncode)
    except subprocess.TimeoutExpired:
        logger.warning("Seed timed out — will retry on next restart")


if __name__ == "__main__":
    seed_database()
    logger.info("Starting World Cup 2026 app on port %d...", PORT)
    subprocess.run(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=BACKEND_DIR,
    )
