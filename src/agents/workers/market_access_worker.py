from src.core.contracts import EngineResult

def run_task(parameters):
    return EngineResult.failure(
        "market_access_tool",
        "Worker adapter is not wired to the canonical engine yet."
    )
