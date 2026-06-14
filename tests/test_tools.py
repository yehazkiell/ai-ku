import os
import shutil
import tempfile
import unittest

from aiku.tools.files import write_file, read_file, list_project_files
from aiku.tools.image import generate_image
from aiku.tools.sandbox import execute_python


class TestFiles(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.dir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.dir, ignore_errors=True)

    def test_write_relative_path_no_dir(self):
        # Regression: previously raised because dirname("") -> makedirs("").
        result = write_file("note.txt", "hello")
        self.assertIn("Successfully", result)
        self.assertEqual(read_file("note.txt"), "hello")

    def test_write_nested_path(self):
        write_file("a/b/c.txt", "nested")
        self.assertEqual(read_file("a/b/c.txt"), "nested")

    def test_read_missing(self):
        self.assertIn("Error", read_file("missing.txt"))

    def test_list_excludes_noise(self):
        os.makedirs("__pycache__", exist_ok=True)
        write_file("__pycache__/x.pyc", "x")
        write_file("real.txt", "y")
        files = list_project_files(".")
        self.assertTrue(any("real.txt" in f for f in files))
        self.assertFalse(any("__pycache__" in f for f in files))

    def test_list_limit(self):
        for i in range(10):
            write_file(f"f{i}.txt", "z")
        self.assertEqual(len(list_project_files(".", limit=5)), 5)


class TestImage(unittest.TestCase):
    def test_generate_image_url(self):
        url = generate_image("a cat", width=512, height=512)
        self.assertTrue(url.startswith("https://image.pollinations.ai/prompt/"))
        self.assertIn("width=512", url)

    def test_empty_prompt(self):
        self.assertIn("Error", generate_image(""))


class TestSandbox(unittest.TestCase):
    def test_basic_math(self):
        self.assertEqual(execute_python("result = sum([1, 2, 3])"), 6)

    def test_forbidden(self):
        self.assertIn("Security violation", execute_python("import os"))


if __name__ == "__main__":
    unittest.main()
