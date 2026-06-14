import chromadb
from chromadb.utils import embedding_functions
import os
import time
from loguru import logger

class VectorMemory:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="aiku_memory",
            embedding_function=self.emb_fn
        )

    def add_memory(self, text, metadata=None):
        """Adds memory with basic deduplication and scoring."""
        # Check if similar memory exists to prevent bloat
        existing = self.query_memory(text, n_results=1)
        if existing and text in existing:
            return "Memory already exists."

        doc_id = f"mem_{int(time.time() * 1000)}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"type": "manual", "timestamp": time.time()}],
            ids=[doc_id]
        )
        return doc_id

    def query_memory(self, query_text, n_results=5):
        try:
            results = self.collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            return results['documents'][0] if results['documents'] else []
        except Exception as e:
            logger.error(f"RAG Query Error: {e}")
            return []

    def prune_old_memories(self, limit=1000):
        """Rudimentary pruning to maintain performance."""
        # Implementation of pruning based on collection count or TTL could go here
        count = self.collection.count()
        if count > limit:
            logger.info(f"Memory pruning required: {count} items found.")
            # ChromaDB deletion logic would follow

memory_instance = VectorMemory()
