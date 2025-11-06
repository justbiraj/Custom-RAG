import os
from dotenv import load_dotenv

load_dotenv()

POSTGRES_URL = os.getenv("POSTGRES_URL")
QDRANT_URL = os.getenv("QDRANT_URL")
REDIS_HOST = os.getenv("REDIS_HOST")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")