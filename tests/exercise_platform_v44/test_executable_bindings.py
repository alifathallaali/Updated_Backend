import pandas as pd
import pytest

from src.exercises.executable_bindings import execute_exact_binding, BindingExecutionError


def sales_df():
    return pd.DataFrame({
        "Year": [2025, 2025, 2026],
        "Sales Units": [10, 20, 40],
        "Sales Value": [100.0, 200.0, 440.0],
        "Brand Name": ["A", "B", "A"],
        "Therapeutic Class": ["X", "X", "X"],
    })


def test_target_baseline_executes_existing_engine():
    out = execute_exact_binding("TGT-001", df=sales_df(), parameters={"base_year": 2025})
    assert out.result.data_quality["binding_status"] == "VERIFIED"
    values = {m["id"]: m["value"] for m in out.result.metrics}
    assert values["units"] == 30.0
    assert values["value"] == 300.0


def test_market_access_scalar_requires_parameters_and_executes():
    out = execute_exact_binding("MAX-004", parameters={"formulary_status": "not listed"})
    assert any(m["value"] == "Formulary / Listing Barrier" for m in out.result.metrics)


def test_finance_reforecast_executes_existing_engine():
    out = execute_exact_binding("FIN-013", parameters={"ytd_actual": 600.0, "months_elapsed": 6, "annual_target": 1500.0})
    assert out.raw_output_type in {"dict", "float"}
    assert out.result.lineage["engine_callable"].endswith("reforecast_ytd")


def test_dataframe_market_access_executes():
    df = pd.DataFrame({"Tender_Timing_Score": [80], "Historical_Demand_Score": [70], "Contract_Expiry_Score": [60], "Product_Fit_Score": [90], "Competitive_Gap_Score": [50], "Win_Rate_Score": [60], "Price_Competitiveness_Score": [70]})
    out = execute_exact_binding("MAX-009", df=df)
    assert out.result.metrics[0]["value"] == 1


def test_missing_required_parameter_fails_closed():
    with pytest.raises(BindingExecutionError, match="Missing execution parameters"):
        execute_exact_binding("FIN-014", parameters={"foreign_sales": 100})
