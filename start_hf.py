import os
import sys
import signal
import subprocess
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
logger = logging.getLogger("start_hf")

PORT = int(os.environ.get("PORT", 8000))
AGENT_PORT = 8001
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

processes = []


def cleanup(*args):
    logger.info("Shutting down all services...")
    for p in processes:
        if p.poll() is None:
            p.terminate()
    for p in processes:
        try:
            p.wait(timeout=5)
        except subprocess.TimeoutExpired:
            p.kill()
    logger.info("All services stopped")
    sys.exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)


def start_agent():
    env = os.environ.copy()
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "agent_server:app", "--host", "0.0.0.0", "--port", str(AGENT_PORT)],
        cwd=os.path.join(ROOT_DIR, "agent"),
        env=env,
    )
    processes.append(p)
    return p


def start_backend():
    env = os.environ.copy()
    env["PORT"] = str(PORT)
    p = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", str(PORT)],
        cwd=os.path.join(ROOT_DIR, "backend"),
        env=env,
    )
    processes.append(p)
    return p


def seed_database():
    logger.info("Seeding match data...")
    result = subprocess.run(
        [sys.executable, os.path.join(ROOT_DIR, "agent", "seed.py")],
        capture_output=True, text=True, timeout=30,
    )
    for line in result.stdout.strip().splitlines():
        if line.strip():
            logger.info("seed | %s", line.strip())
    if result.returncode != 0:
        logger.warning("Seed exited with code %d — may need manual seeding", result.returncode)


if __name__ == "__main__":
    seed_database()

    logger.info("Starting agent service on port %d...", AGENT_PORT)
    agent_proc = start_agent()

    logger.info("Starting backend service on port %d...", PORT)
    backend_proc = start_backend()

    try:
        while True:
            time.sleep(1)
            if agent_proc.poll() is not None:
                logger.error("Agent process exited (code %d), restarting...", agent_proc.returncode)
                agent_proc = start_agent()
            if backend_proc.poll() is not None:
                logger.error("Backend process exited (code %d), restarting...", backend_proc.returncode)
                backend_proc = start_backend()
    except KeyboardInterrupt:
        cleanup()
