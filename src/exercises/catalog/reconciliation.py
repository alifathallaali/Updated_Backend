from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from ..schemas import ExerciseDefinition

@dataclass(frozen=True)
class CatalogReconciliation:
    registered_count: int
    duplicate_ids: tuple[str, ...]
    domain_counts: dict[str, int]
    unresolved_target_gap: int
    status: str


def reconcile_catalog(definitions: Iterable[ExerciseDefinition], *, target: int = 250) -> CatalogReconciliation:
    items = list(definitions)
    ids = [d.id.upper() for d in items]
    duplicates = tuple(sorted({x for x in ids if ids.count(x) > 1}))
    counts: dict[str, int] = {}
    for d in items:
        counts[d.domain] = counts.get(d.domain, 0) + 1
    unique_count = len(set(ids))
    gap = max(target - unique_count, 0)
    status = "COMPLETE" if gap == 0 and not duplicates else "REVIEW_REQUIRED"
    return CatalogReconciliation(unique_count, duplicates, counts, gap, status)
