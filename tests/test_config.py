import os
import unittest

from aiku.config import Settings, mask_secret, DEFAULT_API_KEY


class TestConfig(unittest.TestCase):
    def test_mask_secret(self):
        self.assertEqual(mask_secret(""), "<unset>")
        self.assertEqual(mask_secret(None), "<unset>")
        self.assertEqual(mask_secret("short"), "****")
        self.assertEqual(mask_secret("abcdefghij"), "abcd…ghij")

    def test_defaults(self):
        s = Settings(
            api_key=DEFAULT_API_KEY,
            env="development",
            openrouter_api_key="",
            groq_api_key="",
            openai_api_key="",
        )
        self.assertFalse(s.is_production)
        self.assertEqual(s.configured_providers(), [])

    def test_production_default_key_warns(self):
        s = Settings(api_key=DEFAULT_API_KEY, env="production")
        warnings = s.validate()
        self.assertTrue(any("default value in production" in w for w in warnings))

    def test_configured_providers(self):
        s = Settings(openrouter_api_key="k1", groq_api_key="", openai_api_key="k3")
        self.assertEqual(s.configured_providers(), ["openrouter", "openai"])

    def test_summary_masks_secrets(self):
        s = Settings(api_key="supersecretvalue", openai_api_key="another_secret_key")
        summary = s.summary()
        self.assertNotIn("supersecretvalue", summary)
        self.assertNotIn("another_secret_key", summary)


if __name__ == "__main__":
    unittest.main()
