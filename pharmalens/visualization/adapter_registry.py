from .adapters import ADAPTER_REGISTRY

def get_adapter(exercise_key: str):
    adapter = ADAPTER_REGISTRY.get(exercise_key)
    if adapter is None:
        raise KeyError(f"No visualization adapter registered for: {exercise_key}")
    return adapter()
