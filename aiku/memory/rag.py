"""Persistent vector memory (RAG) backed by ChromaDB.

The heavy dependencies (``chromadb`` + ``sentence-transformers``) are imported
lazily so that importing AI-KU — or running the API/CLI — does not download an
embedding model until memory is actually used.
"""
import time

from loguru import logger

from aiku.config import settings


class VectorMemory:
    def __init__(self, db_path=None):
        import chromadb
        from chromadb.utils import embedding_functions

        self.db_path = db_path or settings.memory_path
        self.client = chromadb.PersistentClient(path=self.db_path)
        self.emb_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        self.collection = self.client.get_or_create_collection(
            name="aiku_memory",
            embedding_function=self.emb_fn,
        )

    def add_memory(self, text, metadata=None):
        """Add a memory, skipping exact duplicates to prevent bloat."""
        if not text or not text.strip():
            return "Skipped empty memory."
        existing = self.query_memory(text, n_results=1)
        if existing and text in existing:
            return "Memory already exists."

        doc_id = f"mem_{int(time.time() * 1000)}"
        self.collection.add(
            documents=[text],
            metadatas=[metadata or {"type": "manual", "timestamp": time.time()}],
            ids=[doc_id],
        )
        return doc_id

    def query_memory(self, query_text, n_results=5):
        try:
            results = self.collection.query(query_texts=[query_text], n_results=n_results)
            docs = results.get("documents") or []
            return docs[0] if docs else []
        except Exception as e:
            logger.error(f"RAG Query Error: {e}")
            return []

    def count(self):
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"RAG count error: {e}")
            return 0

    def prune_old_memories(self, limit=1000):
        """Delete the oldest memories when the collection exceeds ``limit``."""
        count = self.count()
        if count <= limit:
            return f"No pruning needed ({count}/{limit})."
        try:
            data = self.collection.get(include=["metadatas"])
            ids = data.get("ids", [])
            metas = data.get("metadatas", []) or []
            ordered = sorted(
                zip(ids, metas),
                key=lambda pair: (pair[1] or {}).get("timestamp", 0),
            )
            to_delete = [doc_id for doc_id, _ in ordered[: count - limit]]
            if to_delete:
                self.collection.delete(ids=to_delete)
            return f"Pruned {len(to_delete)} memories."
        except Exception as e:
            logger.error(f"RAG prune error: {e}")
            return f"Prune error: {e}"


class _LazyMemory:
    """Proxy that instantiates :class:`VectorMemory` on first real use."""

    _instance = None

    def _get(self):
        if _LazyMemory._instance is None:
            _LazyMemory._instance = VectorMemory()
        return _LazyMemory._instance

    def __getattr__(self, name):
        return getattr(self._get(), name)


# Backwards-compatible singleton; safe to import without loading chromadb.
memory_instance = _LazyMemory()
