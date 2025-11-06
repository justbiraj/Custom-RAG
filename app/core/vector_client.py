from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.core.config import QDRANT_URL

class VectorDB:
    def __init__(self, session_id:str):
        self.client = QdrantClient(url=QDRANT_URL)
        self.collection = f"rag_document_{session_id}" 
        self._init_collection()

    def _init_collection(self):
        existing = [col.name for col in self.client.get_collections().collections]
        if self.collection not in existing:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=768, distance=Distance.COSINE)
            )
    
    def upsert(self, chunks: list[str], embeddings: list[list[float]]):
        points = [
            PointStruct(id=i, vector=embeddings[i], payload={"text": chunks[i]})
            for i in range(len(chunks))
        ]
        self.client.upsert(collection_name=self.collection, points=points)

    def search(self, embedding: list[float], top_k: int = 5):
        results = self.client.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=top_k,
        )
        return [r.payload["text"] for r in results]        

# vector_db = VectorDB()
