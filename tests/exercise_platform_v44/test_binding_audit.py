from src.exercises.binding_audit import audit_exercise, audit_str_004, available_engine_callables


def test_str_004_binding_audit_is_explicit_about_unbound_children():
    audit = {item.exercise_id: item for item in audit_str_004()}
    assert audit["MKT-003"].registered is True
    assert audit["MKT-003"].import_healthy is True
    assert audit["FIN-008"].registered is True
    assert audit["FIN-008"].import_healthy is True
    assert audit["EXE-018"].registered is False


def test_market_intelligence_callable_inventory_is_read_only():
    names = available_engine_callables("src.engines.market_intelligence.market_intelligence")
    assert "market_share_by_brand" in names
    assert "market_share_by_manufacturer" in names
