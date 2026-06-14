import os
import shutil
import unittest


class TestMemory(unittest.TestCase):
    def setUp(self):
        self.db_path = "./test_chroma"
        try:
            from aiku.memory.rag import VectorMemory
            self.mem = VectorMemory(db_path=self.db_path)
        except Exception as e:
            # chromadb / sentence-transformers may be unavailable or the
            # embedding model may fail to download in a sandboxed environment.
            self.skipTest(f"Vector memory backend unavailable: {e}")

    def tearDown(self):
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path, ignore_errors=True)

    def test_add_and_query(self):
        self.mem.add_memory("Unit test fact.")
        res = self.mem.query_memory("Unit test", n_results=1)
        self.assertIn("Unit test fact.", res)


if __name__ == "__main__":
    unittest.main()
