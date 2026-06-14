import unittest
from aiku.memory.rag import VectorMemory
import os
import shutil

class TestMemory(unittest.TestCase):
    def setUp(self):
        self.db_path = "./test_chroma"
        self.mem = VectorMemory(db_path=self.db_path)
    def tearDown(self):
        if os.path.exists(self.db_path):
            shutil.rmtree(self.db_path)
    def test_add_and_query(self):
        self.mem.add_memory("Unit test fact.")
        res = self.mem.query_memory("Unit test", n_results=1)
        self.assertIn("Unit test fact.", res)
if __name__ == '__main__':
    unittest.main()
