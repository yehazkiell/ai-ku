import unittest
from unittest import mock

import app as app_module
from aiku.channels import handler, whatsapp


class TestHandler(unittest.TestCase):
    def setUp(self):
        handler.reset("s1")

    def test_control_commands(self):
        self.assertIn("AI-KU", handler.reply_to("/start", "s1"))
        self.assertIn("cleared", handler.reply_to("/reset", "s1").lower())

    def test_empty_message(self):
        self.assertEqual(handler.reply_to("   ", "s1"), "Please send a text message.")

    def test_reply_and_history(self):
        with mock.patch("core.get_ai_response", return_value="answer") as g:
            out = handler.reply_to("hello", "s1")
            self.assertEqual(out, "answer")
            # second turn must pass the prior turn as history
            handler.reply_to("again", "s1")
            history_arg = g.call_args.kwargs["history"]
            self.assertEqual(history_arg[0], {"role": "user", "content": "hello"})
            self.assertEqual(history_arg[1], {"role": "assistant", "content": "answer"})

    def test_reply_survives_model_error(self):
        with mock.patch("core.get_ai_response", side_effect=RuntimeError("boom")):
            out = handler.reply_to("hello", "s1")
            self.assertIn("error", out.lower())


class TestWhatsAppLogic(unittest.TestCase):
    def test_twiml_escapes(self):
        xml = whatsapp.twiml_reply("a & b < c")
        self.assertIn("<Message>a &amp; b &lt; c</Message>", xml)
        self.assertTrue(xml.startswith("<?xml"))

    def test_parse_twilio(self):
        sender, body = whatsapp.parse_twilio({"From": "whatsapp:+62", "Body": " hi "})
        self.assertEqual(sender, "whatsapp:+62")
        self.assertEqual(body, "hi")

    def test_meta_verify(self):
        from aiku.config import settings
        good = whatsapp.meta_verify("subscribe", settings.whatsapp_verify_token, "123")
        self.assertEqual(good, "123")
        self.assertIsNone(whatsapp.meta_verify("subscribe", "wrong", "123"))

    def test_parse_meta(self):
        payload = {"entry": [{"changes": [{"value": {"messages": [
            {"type": "text", "from": "62", "text": {"body": "hey"}}
        ]}}]}]}
        self.assertEqual(whatsapp.parse_meta(payload), [("62", "hey")])


class TestChannelRoutes(unittest.TestCase):
    def setUp(self):
        app_module.app.config["TESTING"] = True
        self.client = app_module.app.test_client()

    def test_web_index_public(self):
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"AI-KU", resp.data)

    def test_twilio_webhook_returns_twiml(self):
        with mock.patch.object(app_module, "reply_to", return_value="pong"):
            resp = self.client.post("/webhook/twilio", data={"From": "whatsapp:+1", "Body": "ping"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"<Message>pong</Message>", resp.data)

    def test_whatsapp_verify(self):
        from aiku.config import settings
        resp = self.client.get(
            f"/webhook/whatsapp?hub.mode=subscribe&hub.verify_token={settings.whatsapp_verify_token}&hub.challenge=xyz"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, b"xyz")

    def test_whatsapp_verify_rejects_bad_token(self):
        resp = self.client.get(
            "/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=nope&hub.challenge=xyz"
        )
        self.assertEqual(resp.status_code, 403)

    def test_whatsapp_post_replies(self):
        payload = {"entry": [{"changes": [{"value": {"messages": [
            {"type": "text", "from": "62", "text": {"body": "hi"}}
        ]}}]}]}
        with mock.patch.object(app_module, "reply_to", return_value="yo") as r, \
             mock.patch.object(app_module.whatsapp, "meta_send", return_value=True) as send:
            resp = self.client.post("/webhook/whatsapp", json=payload)
        self.assertEqual(resp.status_code, 200)
        r.assert_called_once()
        send.assert_called_once_with("62", "yo")


if __name__ == "__main__":
    unittest.main()
