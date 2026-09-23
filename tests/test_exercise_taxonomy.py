from app.engines.exercise_taxonomy import EXERCISE_PACKS
from app.engines.exercise_manifest import MANIFEST_BY_ID
def test_pack_ids_unique():
 assert len({p["id"] for p in EXERCISE_PACKS})==len(EXERCISE_PACKS)
def test_current_pack_members_are_executable_manifests():
 for p in EXERCISE_PACKS:
  assert set(p["current"]) <= set(MANIFEST_BY_ID)
def test_planned_exercises_are_not_silently_executable():
 planned={x for p in EXERCISE_PACKS for x in p["planned"]}
 assert planned.isdisjoint(MANIFEST_BY_ID)
def test_taxonomy_has_major_pharma_functions():
 ids={p["id"] for p in EXERCISE_PACKS}
 assert {"market_commercial","forecast_planning","sales_sfe","commercial_finance","market_access_heor","medical_affairs","supply_procurement","tender","quality","retail_category","launch_gtm"} <= ids
