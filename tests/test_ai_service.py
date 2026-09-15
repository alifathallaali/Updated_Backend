import unittest
from unittest.mock import AsyncMock, patch

from app.ai_service import AIUnavailable, SYSTEM_PROMPT, generate_ai_response

class AIServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_gemini_success(self):
        with patch("app.ai_service.settings.gemini_api_key", "key"), patch("app.ai_service._gemini", new=AsyncMock(return_value=("answer", "gemini-test"))):
            result = await generate_ai_response("What changed?", "Revenue=100")
        self.assertEqual(result.provider, "gemini")
        self.assertFalse(result.fallback_used)
        self.assertEqual(result.reply, "answer")

    async def test_gemini_failure_falls_back_to_groq(self):
        with patch("app.ai_service.settings.gemini_api_key", "key"), patch("app.ai_service.settings.groq_api_key", "key"), patch("app.ai_service._gemini", new=AsyncMock(side_effect=RuntimeError("down"))), patch("app.ai_service._openai_compatible", new=AsyncMock(return_value=("groq answer", "groq-test"))):
            result = await generate_ai_response("Analyze sales", "Actual=10; Target=12")
        self.assertEqual(result.provider, "groq")
        self.assertTrue(result.fallback_used)

    async def test_all_providers_fail_controlled(self):
        with patch("app.ai_service._gemini", new=AsyncMock(side_effect=RuntimeError("down"))), patch("app.ai_service._openai_compatible", new=AsyncMock(side_effect=RuntimeError("down"))):
            with self.assertRaises(AIUnavailable):
                await generate_ai_response("Analyze", "")

    def test_system_prompt_protects_against_data_injection(self):
        self.assertIn("untrusted DATA", SYSTEM_PROMPT)
        self.assertIn("system prompts", SYSTEM_PROMPT)
        self.assertIn("Insufficient data available", SYSTEM_PROMPT)

if __name__ == "__main__":
    unittest.main()
