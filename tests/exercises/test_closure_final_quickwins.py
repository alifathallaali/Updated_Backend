import pandas as pd
import pytest
from src.exercises.runner import run_exact_bound_exercise
from src.exercises.types import ExerciseStatus


def sales_df():
    rows=[]
    for year in [2024, 2025]:
        for m in range(1,7):
            rows.append({"Year":year,"Month":pd.Timestamp(year,m,1),"Sales Units":100+m+(year-2024)*10,"Sales Value":1000+m*100+(year-2024)*200,"Brand Name":"Brand A" if m%2 else "Brand B","Therapeutic Class":"Class A" if m<=3 else "Class B","Manufacturer":"Maker A" if m%2 else "Maker B","Distribution Channel":"Retail" if m%2 else "Hospital","Market Category":"Rx" if m<=4 else "OTC","Product Launch":"2024-01-01","Pack Size":"10","Drug Strength":"10mg","Selling Price":10.0})
    return pd.DataFrame(rows)

APPROVED={"SAL-001","SAL-004","MKT-009","LCH-005","PRT-001","PRT-003","PRT-004","PRT-014","FIN-006","TRD-002","TRD-010","EXE-001","EXE-003","EXE-004"}
DICT_IDS={"FIN-006","EXE-003"}

@pytest.mark.parametrize("exercise_id", sorted(APPROVED))
def test_final_quickwin_executes_end_to_end(exercise_id):
    run=run_exact_bound_exercise(exercise_id=exercise_id,df=sales_df(),parameters={},data_snapshot="final-quickwin-fixture")
    assert run.status == ExerciseStatus.COMPLETED, run.error
    assert run.result is not None
    assert run.result.data_quality["status"] == "PASS"
    assert run.result.lineage["exercise_id"] == exercise_id
    assert run.result.metadata["adapter"] == "exact_binding"
    raw=run.result.metadata["raw_output"]
    if exercise_id in DICT_IDS:
        assert raw["keys"]
    else:
        assert raw["row_count"] > 0
        assert raw["columns"]
    assert run.result.metrics
    assert run.result.key_findings


def test_final_quickwin_scope_is_exactly_approved_fourteen():
    from src.exercises.catalog.binding_contracts import EXACT_BINDINGS, check_binding_contract
    assert len(APPROVED)==14
    assert all(i in EXACT_BINDINGS for i in APPROVED)
    assert all(check_binding_contract(EXACT_BINDINGS[i]).status == "VERIFIED" for i in APPROVED)
