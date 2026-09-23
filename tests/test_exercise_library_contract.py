from app.engines.exercise_manifest import list_exercise_manifests
def test_library_manifest_contract():
 items=list_exercise_manifests()
 assert items
 for x in items:
  assert x["id"] and x["name"] and x["domain"] and x["family"]
  assert isinstance(x["personas"], tuple) or isinstance(x["personas"], list)
  assert "requiredInputs" in x and "chartPatterns" in x and "reportSection" in x
  assert x["readiness"]["state"] in {"verified_subset","foundation_only","additional_inputs","planned"}
