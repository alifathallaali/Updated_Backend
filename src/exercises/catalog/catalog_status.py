from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from ..schemas import ExerciseDefinition


@dataclass(frozen=True)
class CatalogStatus:
    canonical_count: int
    target_count: int | None
    gap: int | None
    duplicate_ids: tuple[str, ...]
    domains: tuple[tuple[str, int], ...]
    closure_status: str
    target_provenance: str


def build_catalog_status(
    definitions: Iterable[ExerciseDefinition],
    *,
    target_count: int | None = 250,
    target_provenance: str = "UNVERIFIED_HISTORICAL_TARGET",
) -> CatalogStatus:
    items = list(definitions)
    ids = [item.id.upper() for item in items]
    duplicates = tuple(sorted({item_id for item_id in ids if ids.count(item_id) > 1}))

    counts: dict[str, int] = {}
    for item in items:
        counts[item.domain] = counts.get(item.domain, 0) + 1

    unique_count = len(set(ids))
    gap = None if target_count is None else max(target_count - unique_count, 0)

    # A historical target is not sufficient evidence that missing definitions exist.
    # Closure is allowed only when the target itself is backed by an authoritative source.
    authoritative_target = target_provenance.startswith("AUTHORITATIVE:")
    if duplicates:
        closure = "INVALID_DUPLICATES"
    elif target_count is None:
        closure = "SOURCE_REQUIRED"
    elif gap == 0 and authoritative_target:
        closure = "COMPLETE"
    elif not authoritative_target:
        closure = "TARGET_SOURCE_REQUIRED"
    else:
        closure = "GAP_REMAINS"

    return CatalogStatus(
        canonical_count=unique_count,
        target_count=target_count,
        gap=gap,
        duplicate_ids=duplicates,
        domains=tuple(sorted(counts.items())),
        closure_status=closure,
        target_provenance=target_provenance,
    )
