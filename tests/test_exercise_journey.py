from app.engines.exercise_journey import NEXT_EXERCISES,next_exercises
from app.engines.exercise_manifest import MANIFEST_BY_ID
def test_journey_targets_exist():
 for source,targets in NEXT_EXERCISES.items():
  assert source in MANIFEST_BY_ID
  assert set(targets)<=set(MANIFEST_BY_ID)
def test_next_exercises_are_bounded_and_descriptive():
 out=next_exercises('product-01')
 assert 1<=len(out)<=3
 assert all(x['exerciseId'] and x['name'] and x['readiness'] for x in out)
