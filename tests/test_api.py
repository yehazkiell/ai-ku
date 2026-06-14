import unittest
from unittest import mock

import app as app_module


class TestAPI(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()
        self.headers = {"X-API-KEY": app_module.API_KEY}

    def test_health_no_auth(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("capabilities", resp.get_json())

    def test_metrics_no_auth(self):
        resp = self.client.get("/metrics")
        self.assertEqual(resp.status_code, 200)

    def test_chat_requires_auth(self):
        resp = self.client.post("/api/v1/chat", json={"message": "hi"})
        self.assertEqual(resp.status_code, 401)

    def test_chat_success(self):
        with mock.patch.object(app_module, "get_ai_response", return_value="pong"):
            resp = self.client.post("/api/v1/chat", json={"message": "ping"}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["response"], "pong")

    def test_chat_validation_error(self):
        resp = self.client.post("/api/v1/chat", json={"message": ""}, headers=self.headers)
        self.assertEqual(resp.status_code, 400)

    def test_image_success(self):
        with mock.patch.object(app_module, "generate_image", return_value="http://img"):
            resp = self.client.post("/api/v1/image", json={"prompt": "a cat"}, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()["url"], "http://img")

    def test_memory_post_and_get(self):
        with mock.patch.object(app_module, "save_data", return_value="mem_1") as save, \
             mock.patch.object(app_module, "recall_data", return_value=["fact"]) as recall:
            post = self.client.post("/api/v1/memory", json={"text": "remember this"}, headers=self.headers)
            self.assertEqual(post.status_code, 200)
            self.assertEqual(post.get_json()["id"], "mem_1")
            save.assert_called_once()

            get = self.client.get("/api/v1/memory?q=remember", headers=self.headers)
            self.assertEqual(get.status_code, 200)
            self.assertEqual(get.get_json()["results"], ["fact"])
            recall.assert_called_once()

    def test_memory_get_missing_query(self):
        resp = self.client.get("/api/v1/memory", headers=self.headers)
        self.assertEqual(resp.status_code, 400)


if __name__ == "__main__":
    unittest.main()
