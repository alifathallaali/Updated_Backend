from src.core.contracts import EngineResult

def run_task(parameters):
    return EngineResult.failure(
        "brand_tool",
        "Worker adapter is not wired to the canonical engine yet."
    )
