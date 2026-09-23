from __future__ import annotations
from datetime import datetime, timezone

def build_lineage(*, exercise_id: str, exercise_version: str, data_snapshot: str | None,
                  engines: dict[str, str], source: str = "canonical_data") -> dict:
    return {
        "source": source,
        "data_snapshot": data_snapshot,
        "exercise_id": exercise_id,
        "exercise_version": exercise_version,
        "engine_versions": dict(engines),
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }
