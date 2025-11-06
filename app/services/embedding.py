import requests
from app.core.config import OLLAMA_EMBED_MODEL

def create_ollama_embedding(texts: list[str]) -> list[list[float]]:
    embeddings = []
    for txt in texts:
        resp = requests.post(
            "http://localhost:11434/api/embeddings",
            json={"model": OLLAMA_EMBED_MODEL, "prompt": txt},
            timeout=30
        )
        resp.raise_for_status()
        embeddings.append(resp.json()["embedding"])
    return embeddings