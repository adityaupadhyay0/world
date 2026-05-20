import chromadb
import json
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class VectorStore:
    def __init__(self, collection_name: str = "episodic_memory"):
        self.client = chromadb.Client()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_memory(self, memory_id: str, text: str, metadata: Dict[str, Any]):
        embedding = self.model.encode(text).tolist()
        self.collection.add(
            ids=[memory_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )

    def query_memory(self, query_text: str, n_results: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self.model.encode(query_text).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        memories = []
        if results['ids']:
            for i in range(len(results['ids'][0])):
                memories.append({
                    "id": results['ids'][0][i],
                    "text": results['documents'][0][i],
                    "metadata": results['metadatas'][0][i],
                    "distance": results['distances'][0][i]
                })
        return memories

class MemoryManager:
    def __init__(self):
        self.vector_store = VectorStore()
        self.hot_state: List[Dict[str, Any]] = [] # Recent events/entities
        self.warm_limit = 20
        self.hot_limit = 5

    def add_to_hot(self, event: Dict[str, Any]):
        self.hot_state.append(event)
        if len(self.hot_state) > self.hot_limit:
            oldest = self.hot_state.pop(0)
            self._archive_to_cold(oldest)

    def _archive_to_cold(self, event: Dict[str, Any]):
        memory_id = f"mem_{event.get('id', datetime.now(timezone.utc).timestamp())}"
        text = f"Event: {event.get('event_type')} - {json.dumps(event.get('data'))}"
        self.vector_store.add_memory(memory_id, text, event)

    def get_context(self, query: str) -> Dict[str, Any]:
        """
        Retrieves relevant context from three tiers.
        """
        cold_memories = self.vector_store.query_memory(query, n_results=3)
        return {
            "hot": self.hot_state,
            "cold": cold_memories
        }
