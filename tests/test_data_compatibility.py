from app.engines.data_compatibility import assess_exercise_compatibility,compatible_columns
def test_aliases_match_canonical_requirements():
 out=compatible_columns(["period","sales_value"],["Month","Sales Value"])
 assert not out["missing"]
def test_ready_market_dataset():
 out=assess_exercise_compatibility("product-01",["period","sales_value","brand_name"],dataset_status="ready")
 assert out["state"]=="ready" and out["canRun"]
def test_missing_required_blocks():
 out=assess_exercise_compatibility("product-06",["period","sales_value"],dataset_status="ready")
 assert out["state"]=="missing_data" and "sales_units" in out["missingRequired"] and not out["canRun"]
def test_additional_inputs_are_partial_not_fake_ready():
 out=assess_exercise_compatibility("product-12",["product","sales_units"],dataset_status="ready")
 assert out["state"]=="partial" and out["canRun"] and out["missingOptional"]
def test_unvalidated_dataset_is_blocked():
 out=assess_exercise_compatibility("product-01",["period","sales_value"],dataset_status="mapping")
 assert out["state"]=="blocked" and not out["canRun"]
