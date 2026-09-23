from app.engines.dataset_intelligence import infer_column_roles,inspect_unknown_dataset
def test_role_inference_uses_schema_only():
 roles=infer_column_roles(["Month","Sales Value","Brand Name"])
 assert "time" in roles[0]["roles"] and "value" in roles[1]["roles"] and "product" in roles[2]["roles"]
def test_market_like_dataset_suggests_compatible_exercise():
 out=inspect_unknown_dataset(["period","sales_value","brand_name","manufacturer"])
 assert out["schemaConfidence"]>0
 assert any(x["state"]=="ready" for x in out["suggestedExercises"])
 assert out["privacy"]["rawRowsSentToLLM"] is False
def test_unknown_schema_requests_clarification():
 out=inspect_unknown_dataset(["foo_code","bar_flag","misc_text"])
 assert out["needsUserClarification"] is True
 assert out["likelyDatasetTypes"]==["unclassified"]
def test_sales_force_shape_detected():
 out=inspect_unknown_dataset(["sales_rep","territory","calls","target"])
 assert "field_force_or_hcp" in out["likelyDatasetTypes"]
