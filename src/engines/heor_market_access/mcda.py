"""
PharmaLens AI - Multi-Criteria Decision Analysis Engine
Path: PharmaLens AI V0.2/src/mcda.py

Generic MCDA calculation layer for HEOR, HTA, market access, formulary,
tender, product, and portfolio comparisons.

Supported methods:
- Weighted Sum Model (WSM)
- TOPSIS
- Weighted Product Model (WPM)
- AHP weight derivation
- One-way weight sensitivity analysis

Design:
- User/configuration-driven criteria and weights
- Explicit benefit/cost direction
- Transparent component scores
- No hidden "best action" recommendation
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional, Sequence
import math
import numpy as np
import pandas as pd


SUPPORTED_METHODS = {"WSM", "TOPSIS", "WPM"}


def _validate_frame(df: pd.DataFrame, criteria: Sequence[str]) -> None:
    if df.empty:
        raise ValueError("MCDA input dataframe is empty.")
    missing = [c for c in criteria if c not in df.columns]
    if missing:
        raise KeyError(f"Missing MCDA criteria columns: {missing}")


def _weights(
    criteria: Sequence[str],
    weights: Optional[Mapping[str, float]],
) -> Dict[str, float]:
    if not criteria:
        raise ValueError("At least one criterion is required.")

    if weights is None:
        raw = {c: 1.0 for c in criteria}
    else:
        missing = [c for c in criteria if c not in weights]
        if missing:
            raise KeyError(f"Missing weights for criteria: {missing}")
        raw = {c: float(weights[c]) for c in criteria}

    if any((not math.isfinite(v) or v < 0) for v in raw.values()):
        raise ValueError("MCDA weights must be finite and non-negative.")

    total = sum(raw.values())
    if total <= 0:
        raise ValueError("At least one MCDA weight must be greater than zero.")

    return {c: v / total for c, v in raw.items()}


def _directions(
    criteria: Sequence[str],
    directions: Optional[Mapping[str, str]],
) -> Dict[str, str]:
    out = {}
    for c in criteria:
        value = str((directions or {}).get(c, "benefit")).strip().lower()
        if value not in {"benefit", "cost"}:
            raise ValueError(
                f"Direction for {c!r} must be 'benefit' or 'cost'."
            )
        out[c] = value
    return out


def _numeric_matrix(
    df: pd.DataFrame,
    criteria: Sequence[str],
    missing_policy: str = "median",
) -> pd.DataFrame:
    x = df.loc[:, criteria].apply(pd.to_numeric, errors="coerce")

    policy = str(missing_policy).lower()
    if policy == "error":
        if x.isna().any().any():
            cols = x.columns[x.isna().any()].tolist()
            raise ValueError(f"Missing/non-numeric MCDA values in: {cols}")
    elif policy == "zero":
        x = x.fillna(0.0)
    elif policy == "median":
        for c in x.columns:
            median = x[c].median()
            x[c] = x[c].fillna(0.0 if pd.isna(median) else median)
    else:
        raise ValueError("missing_policy must be 'error', 'zero', or 'median'.")

    return x.astype(float)


def minmax_normalize(
    df: pd.DataFrame,
    criteria: Sequence[str],
    directions: Optional[Mapping[str, str]] = None,
    missing_policy: str = "median",
) -> pd.DataFrame:
    """Normalize criteria to 0..1, reversing cost criteria."""
    _validate_frame(df, criteria)
    dirs = _directions(criteria, directions)
    x = _numeric_matrix(df, criteria, missing_policy)
    out = pd.DataFrame(index=df.index)

    for c in criteria:
        lo, hi = float(x[c].min()), float(x[c].max())
        if np.isclose(hi, lo):
            out[c] = 0.5
        elif dirs[c] == "benefit":
            out[c] = (x[c] - lo) / (hi - lo)
        else:
            out[c] = (hi - x[c]) / (hi - lo)

    return out


def weighted_sum(
    df: pd.DataFrame,
    criteria: Sequence[str],
    weights: Optional[Mapping[str, float]] = None,
    directions: Optional[Mapping[str, str]] = None,
    *,
    id_column: Optional[str] = None,
    missing_policy: str = "median",
) -> pd.DataFrame:
    """Weighted Sum Model with transparent criterion contributions."""
    w = _weights(criteria, weights)
    norm = minmax_normalize(df, criteria, directions, missing_policy)

    result = pd.DataFrame(index=df.index)
    if id_column:
        if id_column not in df.columns:
            raise KeyError(f"id_column {id_column!r} not found.")
        result[id_column] = df[id_column]

    score = pd.Series(0.0, index=df.index)
    for c in criteria:
        result[f"{c}__normalized"] = norm[c]
        result[f"{c}__weighted"] = norm[c] * w[c]
        score = score + result[f"{c}__weighted"]

    result["MCDA_Score"] = score
    result["MCDA_Score_100"] = score * 100
    result["MCDA_Rank"] = score.rank(method="min", ascending=False).astype(int)
    return result.sort_values("MCDA_Score", ascending=False)


def topsis(
    df: pd.DataFrame,
    criteria: Sequence[str],
    weights: Optional[Mapping[str, float]] = None,
    directions: Optional[Mapping[str, str]] = None,
    *,
    id_column: Optional[str] = None,
    missing_policy: str = "median",
) -> pd.DataFrame:
    """Technique for Order Preference by Similarity to Ideal Solution."""
    _validate_frame(df, criteria)
    w = _weights(criteria, weights)
    dirs = _directions(criteria, directions)
    x = _numeric_matrix(df, criteria, missing_policy)

    denominator = np.sqrt((x ** 2).sum(axis=0)).replace(0, 1.0)
    normalized = x / denominator
    weighted = normalized.copy()

    for c in criteria:
        weighted[c] = normalized[c] * w[c]

    ideal_best = {}
    ideal_worst = {}
    for c in criteria:
        if dirs[c] == "benefit":
            ideal_best[c] = weighted[c].max()
            ideal_worst[c] = weighted[c].min()
        else:
            ideal_best[c] = weighted[c].min()
            ideal_worst[c] = weighted[c].max()

    best_vec = pd.Series(ideal_best)
    worst_vec = pd.Series(ideal_worst)
    distance_best = np.sqrt(((weighted - best_vec) ** 2).sum(axis=1))
    distance_worst = np.sqrt(((weighted - worst_vec) ** 2).sum(axis=1))
    denom = distance_best + distance_worst
    closeness = np.where(
        np.isclose(denom, 0.0),
        0.5,
        distance_worst / denom,
    )

    result = pd.DataFrame(index=df.index)
    if id_column:
        if id_column not in df.columns:
            raise KeyError(f"id_column {id_column!r} not found.")
        result[id_column] = df[id_column]

    result["Distance_to_Ideal"] = distance_best
    result["Distance_to_Anti_Ideal"] = distance_worst
    result["MCDA_Score"] = closeness
    result["MCDA_Score_100"] = result["MCDA_Score"] * 100
    result["MCDA_Rank"] = (
        result["MCDA_Score"].rank(method="min", ascending=False).astype(int)
    )
    return result.sort_values("MCDA_Score", ascending=False)


def weighted_product(
    df: pd.DataFrame,
    criteria: Sequence[str],
    weights: Optional[Mapping[str, float]] = None,
    directions: Optional[Mapping[str, str]] = None,
    *,
    id_column: Optional[str] = None,
    missing_policy: str = "median",
    epsilon: float = 1e-12,
) -> pd.DataFrame:
    """Weighted Product Model using 0..1 direction-adjusted normalization."""
    w = _weights(criteria, weights)
    norm = minmax_normalize(df, criteria, directions, missing_policy)
    adjusted = norm.clip(lower=epsilon)

    log_score = pd.Series(0.0, index=df.index)
    for c in criteria:
        log_score = log_score + w[c] * np.log(adjusted[c])

    raw_score = np.exp(log_score)
    total = float(raw_score.sum())
    score = raw_score / total if total > 0 else raw_score

    result = pd.DataFrame(index=df.index)
    if id_column:
        if id_column not in df.columns:
            raise KeyError(f"id_column {id_column!r} not found.")
        result[id_column] = df[id_column]

    result["MCDA_Score"] = score
    result["MCDA_Score_100"] = score * 100
    result["MCDA_Rank"] = score.rank(method="min", ascending=False).astype(int)
    return result.sort_values("MCDA_Score", ascending=False)


def ahp_weights(
    pairwise_matrix: Sequence[Sequence[float]],
    criteria: Sequence[str],
) -> Dict[str, Any]:
    """
    Derive AHP weights and consistency metrics from a reciprocal matrix.

    Consistency Ratio (CR) is reported when a Random Index is available.
    """
    matrix = np.asarray(pairwise_matrix, dtype=float)
    n = len(criteria)

    if matrix.shape != (n, n):
        raise ValueError(f"pairwise_matrix must have shape {(n, n)}.")
    if np.any(matrix <= 0) or not np.all(np.isfinite(matrix)):
        raise ValueError("AHP pairwise values must be finite and > 0.")

    if not np.allclose(np.diag(matrix), 1.0, atol=1e-6):
        raise ValueError("AHP pairwise matrix diagonal must equal 1.")

    if not np.allclose(matrix * matrix.T, 1.0, atol=1e-3):
        raise ValueError("AHP pairwise matrix must be reciprocal.")

    eigenvalues, eigenvectors = np.linalg.eig(matrix)
    idx = int(np.argmax(eigenvalues.real))
    lambda_max = float(eigenvalues[idx].real)
    vector = np.abs(eigenvectors[:, idx].real)
    vector = vector / vector.sum()

    ci = 0.0 if n <= 2 else (lambda_max - n) / (n - 1)
    random_index = {
        1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
        6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    }
    ri = random_index.get(n)
    cr = None if ri in (None, 0.0) else float(ci / ri)

    return {
        "weights": {c: float(v) for c, v in zip(criteria, vector)},
        "lambda_max": lambda_max,
        "consistency_index": float(ci),
        "consistency_ratio": cr,
        "consistency_interpretation": (
            "not_applicable"
            if cr is None
            else ("acceptable" if cr <= 0.10 else "review_pairwise_judgments")
        ),
    }


def run_mcda(
    df: pd.DataFrame,
    criteria: Sequence[str],
    weights: Optional[Mapping[str, float]] = None,
    directions: Optional[Mapping[str, str]] = None,
    *,
    method: str = "TOPSIS",
    id_column: Optional[str] = None,
    missing_policy: str = "median",
) -> Dict[str, Any]:
    """Unified MCDA entry point."""
    method = str(method).upper().strip()
    if method not in SUPPORTED_METHODS:
        raise ValueError(f"method must be one of {sorted(SUPPORTED_METHODS)}.")

    w = _weights(criteria, weights)
    dirs = _directions(criteria, directions)

    if method == "WSM":
        results = weighted_sum(
            df, criteria, w, dirs,
            id_column=id_column, missing_policy=missing_policy,
        )
    elif method == "TOPSIS":
        results = topsis(
            df, criteria, w, dirs,
            id_column=id_column, missing_policy=missing_policy,
        )
    else:
        results = weighted_product(
            df, criteria, w, dirs,
            id_column=id_column, missing_policy=missing_policy,
        )

    return {
        "status": "success",
        "method": method,
        "criteria": list(criteria),
        "weights": w,
        "directions": dirs,
        "missing_policy": missing_policy,
        "results": results,
    }


def weight_sensitivity(
    df: pd.DataFrame,
    criteria: Sequence[str],
    base_weights: Mapping[str, float],
    directions: Optional[Mapping[str, str]] = None,
    *,
    method: str = "TOPSIS",
    id_column: Optional[str] = None,
    variation_pct: float = 0.20,
    steps: int = 5,
    missing_policy: str = "median",
) -> pd.DataFrame:
    """
    One-way sensitivity analysis.

    Each criterion weight is varied around its base value while all other
    weights are proportionally re-normalized. Results expose score/rank
    stability rather than making an automatic decision.
    """
    if variation_pct < 0:
        raise ValueError("variation_pct cannot be negative.")
    if steps < 2:
        raise ValueError("steps must be >= 2.")

    base = _weights(criteria, base_weights)
    rows = []

    for varied in criteria:
        low = max(0.0, base[varied] * (1 - variation_pct))
        high = min(1.0, base[varied] * (1 + variation_pct))

        for new_weight in np.linspace(low, high, steps):
            other_criteria = [c for c in criteria if c != varied]
            scenario_weights = dict(base)
            scenario_weights[varied] = float(new_weight)

            remaining = 1.0 - float(new_weight)
            old_other_total = sum(base[c] for c in other_criteria)

            if other_criteria:
                if old_other_total <= 0:
                    equal = remaining / len(other_criteria)
                    for c in other_criteria:
                        scenario_weights[c] = equal
                else:
                    for c in other_criteria:
                        scenario_weights[c] = (
                            base[c] / old_other_total * remaining
                        )

            run = run_mcda(
                df,
                criteria,
                scenario_weights,
                directions,
                method=method,
                id_column=id_column,
                missing_policy=missing_policy,
            )
            result = run["results"]

            for idx, row in result.iterrows():
                rows.append(
                    {
                        "Varied_Criterion": varied,
                        "Varied_Weight": float(new_weight),
                        "Alternative": (
                            row[id_column] if id_column else str(idx)
                        ),
                        "MCDA_Score": float(row["MCDA_Score"]),
                        "MCDA_Rank": int(row["MCDA_Rank"]),
                    }
                )

    return pd.DataFrame(rows)


__all__ = [
    "SUPPORTED_METHODS",
    "minmax_normalize",
    "weighted_sum",
    "topsis",
    "weighted_product",
    "ahp_weights",
    "run_mcda",
    "weight_sensitivity",
]
