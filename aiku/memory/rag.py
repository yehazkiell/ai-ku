import chromadb
from chromadb.utils import embedding_functions
import os
import time

class VectorMemory:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using a lightweight local embedding function
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(
            name="aiku_memory",
            embedding_function=self.emb_fn
        )

    def add_memory(self, text, metadata=None):
        doc_id = f"mem_{int(time.time() * 1000)}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"type": "manual"}],
            ids=[doc_id]
        )
        return doc_id

    def query_memory(self, query_text, n_results=5):
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results['documents'][0] if results['documents'] else []

memory_instance = VectorMemory()
