import unittest
from unittest import mock

import aiku.llm as llm
from aiku.config import Settings


class FakeResponse:
    def __init__(self, content):
        self._content = content

    def raise_for_status(self):
        pass

    def json(self):
        return {"choices": [{"message": {"content": self._content}}]}


class TestLLMRouter(unittest.TestCase):
    def test_provider_order_auto(self):
        s = Settings(llm_provider="auto", openrouter_api_key="k", groq_api_key="", openai_api_key="")
        with mock.patch.object(llm, "settings", s):
            self.assertEqual(llm._provider_order(), ["openrouter", "g4f"])

    def test_provider_order_forced(self):
        s = Settings(llm_provider="groq")
        with mock.patch.object(llm, "settings", s):
            self.assertEqual(llm._provider_order(), ["groq", "g4f"])

    def test_chat_uses_openai_compatible(self):
        s = Settings(llm_provider="openai", openai_api_key="sk-test")
        with mock.patch.object(llm, "settings", s), \
             mock.patch.object(llm.requests, "post", return_value=FakeResponse("hi there")) as post:
            out = llm.chat([{"role": "user", "content": "hello"}])
            self.assertEqual(out, "hi there")
            post.assert_called_once()

    def test_chat_falls_back_to_g4f(self):
        s = Settings(llm_provider="g4f")
        with mock.patch.object(llm, "settings", s), \
             mock.patch.object(llm, "_call_g4f", return_value="free answer") as g4f_call:
            out = llm.chat([{"role": "user", "content": "hi"}])
            self.assertEqual(out, "free answer")
            g4f_call.assert_called_once()

    def test_all_fail_returns_error(self):
        s = Settings(llm_provider="openai", openai_api_key="sk-test")
        with mock.patch.object(llm, "settings", s), \
             mock.patch.object(llm.requests, "post", side_effect=RuntimeError("boom")), \
             mock.patch.object(llm, "_call_g4f", side_effect=RuntimeError("no g4f")):
            out = llm.chat([{"role": "user", "content": "hi"}])
            self.assertIn("Critical Error", out)


if __name__ == "__main__":
    unittest.main()
