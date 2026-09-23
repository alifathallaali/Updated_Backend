from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..schemas import ExerciseDefinition


@dataclass(frozen=True)
class SemanticCollision:
    exercise_id: str
    canonical_name: str
    legacy_name: str
    canonical_domain: str
    legacy_domain: str


@dataclass(frozen=True)
class CanonicalCatalogAudit:
    canonical_count: int
    runtime_count: int
    legacy_only_ids: tuple[str, ...]
    semantic_collisions: tuple[SemanticCollision, ...]
    duplicate_canonical_ids: tuple[str, ...]
    target_gap: int
    status: str


def audit_canonical_catalog(
    canonical_definitions: Iterable[ExerciseDefinition],
    runtime_definitions: Iterable[ExerciseDefinition],
    legacy_definitions: Iterable[ExerciseDefinition],
    *,
    target: int = 250,
) -> CanonicalCatalogAudit:
    canonical = list(canonical_definitions)
    runtime = list(runtime_definitions)
    legacy = list(legacy_definitions)

    canonical_ids = [d.id.upper() for d in canonical]
    duplicate_ids = tuple(sorted({x for x in canonical_ids if canonical_ids.count(x) > 1}))
    canonical_by_id = {d.id.upper(): d for d in canonical}
    legacy_by_id = {d.id.upper(): d for d in legacy}
    runtime_ids = {d.id.upper() for d in runtime}

    legacy_only = tuple(sorted(set(legacy_by_id) - set(canonical_by_id)))
    collisions: list[SemanticCollision] = []
    for exercise_id in sorted(set(canonical_by_id) & set(legacy_by_id)):
        c = canonical_by_id[exercise_id]
        l = legacy_by_id[exercise_id]
        if c.name != l.name or c.domain != l.domain:
            collisions.append(
                SemanticCollision(
                    exercise_id=exercise_id,
                    canonical_name=c.name,
                    legacy_name=l.name,
                    canonical_domain=c.domain,
                    legacy_domain=l.domain,
                )
            )

    canonical_count = len(set(canonical_ids))
    gap = max(target - canonical_count, 0)
    status = "REVIEW_REQUIRED" if duplicate_ids or legacy_only or collisions or gap else "COMPLETE"
    return CanonicalCatalogAudit(
        canonical_count=canonical_count,
        runtime_count=len(runtime_ids),
        legacy_only_ids=legacy_only,
        semantic_collisions=tuple(collisions),
        duplicate_canonical_ids=duplicate_ids,
        target_gap=gap,
        status=status,
    )
