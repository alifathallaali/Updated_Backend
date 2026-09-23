from app.visualization.coverage_audit import audit_exercise_coverage

def test_all_registered_exercises_have_mvp_presentation_coverage():
    out=audit_exercise_coverage()
    assert out["exerciseCount"]==20
    assert out["coveredCount"]==20, [(x["exerciseId"],x["gaps"]) for x in out["exercises"] if not x["covered"]]
    assert out["coveragePct"]==100.0

def test_every_exercise_has_engine_layout_chart_contract_and_report_section():
    out=audit_exercise_coverage()
    for x in out["exercises"]:
        assert x["checks"]["engine"]
        assert x["checks"]["layout"]
        assert x["checks"]["chartPatterns"]
        assert x["checks"]["reportSection"]
