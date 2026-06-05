import logging
import threading
from pymongo import MongoClient
from pymongo.collection import Collection
from config import MONGODB_URI, DATABASE_NAME

logger = logging.getLogger(__name__)

_client: MongoClient | None = None
_client_lock = threading.Lock()


def get_db():
    global _client
    if _client is None:
        with _client_lock:
            if _client is None:
                _client = MongoClient(
                    MONGODB_URI,
                    serverSelectionTimeoutMS=45000,
                    connectTimeoutMS=30000,
                    socketTimeoutMS=30000,
                    tls=True,
                    retryWrites=True,
                    retryReads=True,
                )
                logger.info("Connected to MongoDB at %s", MONGODB_URI)
    return _client[DATABASE_NAME]


def get_collection(name: str) -> Collection:
    return get_db()[name]


def close():
    global _client
    if _client:
        _client.close()
        _client = None
        logger.info("MongoDB connection closed")
