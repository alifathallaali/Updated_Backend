from app.engines.engine_registry import ENGINE_REGISTRY
from app.visualization.exercise_catalog import EXERCISE_CATALOG,get_exercise_presentation
def test_presentation_catalog_matches_registry(): assert set(EXERCISE_CATALOG)==set(ENGINE_REGISTRY)
def test_each_presentation_has_required_metadata():
 for product_id in ENGINE_REGISTRY:
  item=get_exercise_presentation(product_id)
  assert item["exercise_id"]==product_id and item["family"] and item["report_section"] and item["chart_patterns"]
