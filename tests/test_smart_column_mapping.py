from app.mapping_engine import suggest_mapping,apply_confirmed_mapping
def test_exact_and_business_aliases():
 out=suggest_mapping(["MAT Month","Sales","Brand Name","Manufacturer"])
 assert out["suggestions"]["period"]["column"]=="MAT Month"
 assert out["suggestions"]["sales_value"]["column"]=="Sales"
 assert out["suggestions"]["brand_name"]["column"]=="Brand Name"
def test_source_column_is_not_double_mapped():
 out=suggest_mapping(["Product","Month","Units"])
 cols=[x["column"] for x in out["suggestions"].values()]
 assert len(cols)==len(set(cols))
def test_confidence_metadata_is_reviewable():
 out=suggest_mapping(["Sale Valu","Mth"])
 for s in out["suggestions"].values():
  assert "confidenceBand" in s and "requiresConfirmation" in s and "matchedAlias" in s
def test_unmatched_columns_preserved():
 out=suggest_mapping(["Month","Sales Value","Mystery Code"])
 assert "Mystery Code" in out["unmatchedColumns"]
def test_apply_only_confirmed_fields():
 rows=[{"My Sales":10,"My Month":"Jan","Ignore":"x"}]
 out=apply_confirmed_mapping(rows,{"sales_value":"My Sales","period":"My Month"})
 assert out==[{"sales_value":10,"period":"Jan"}]
