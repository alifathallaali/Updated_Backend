from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LegacyExerciseAlias:
    legacy_id: str
    replacement_id: str
    reason: str
    kind: str = "INTERNAL_COMPATIBILITY"


# These aliases isolate pre-catalog STR-004 semantics from canonical public IDs.
# They are intentionally NOT registered as public catalog exercises.
STR004_LEGACY_ALIASES: tuple[LegacyExerciseAlias, ...] = (
    LegacyExerciseAlias(
        legacy_id="MKT-004",
        replacement_id="STR004-CAP-MARKET-SUMMARY",
        reason="Legacy STR-004 MKT-004 meant Market Summary; canonical MKT-004 is Brand Performance.",
    ),
    LegacyExerciseAlias(
        legacy_id="MKT-010",
        replacement_id="STR004-CAP-MANUFACTURER-SHARE",
        reason="Legacy STR-004 MKT-010 meant Manufacturer Share; canonical MKT-010 is Competitive Gap.",
    ),
    LegacyExerciseAlias(
        legacy_id="TRD-019",
        replacement_id="STR004-CAP-CHANNEL-PERFORMANCE",
        reason="TRD-019 predates the canonical Trade catalog and remains an internal validated capability node.",
    ),
    LegacyExerciseAlias(
        legacy_id="EXE-018",
        replacement_id="STR004-SYNTHESIS-EXECUTIVE-BRIEF",
        reason="EXE-018 predates the canonical Executive catalog and is an internal synthesis node, not a public exercise.",
    ),
)

_ALIAS_BY_ID = {item.legacy_id: item for item in STR004_LEGACY_ALIASES}


def compatibility_alias(exercise_id: str) -> LegacyExerciseAlias | None:
    return _ALIAS_BY_ID.get(exercise_id.upper())


def public_catalog_id(exercise_id: str) -> str | None:
    """Return None when a legacy ID must not be exposed as a canonical public exercise."""
    return None if exercise_id.upper() in {"TRD-019", "EXE-018"} else exercise_id.upper()
