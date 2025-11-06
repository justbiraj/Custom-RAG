import redis
import json
from app.core.config import REDIS_HOST

r = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def get_memory(session_id: str):
    data = r.get(session_id)
    return json.loads(data) if data else []

def save_memory(session_id: str, query: str, answer: str):
    history = get_memory(session_id)
    history.append({"query": query, "answer": answer})
    r.set(session_id, json.dumps(history))
