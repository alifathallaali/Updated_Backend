"""Backward-compatible facade for the centralized AI service."""
from .ai_service import AIResponse, AIUnavailable, generate_ai_response

async def ask_copilot(history: list[dict], data_context: str = "") -> str:
    latest = next((item.get("content", "") for item in reversed(history) if item.get("role") == "user"), "")
    result: AIResponse = await generate_ai_response(latest, data_context=data_context)
    return result.reply
