from src.exercises.adapters import binding_health


def test_gtm_channel_binding_imports_without_agent_dependency():
    health = binding_health("TRD-019")
    assert health["available"] is True
    assert health["callable"] == "channel_performance"
