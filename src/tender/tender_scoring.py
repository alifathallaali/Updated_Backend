def normalize_weights(weights):
    if not weights:
        raise ValueError("At least one MCDA criterion is required.")
    cleaned = {k: float(v) for k, v in weights.items()}
    if any(v < 0 for v in cleaned.values()):
        raise ValueError("MCDA weights cannot be negative.")
    total = sum(cleaned.values())
    if total <= 0:
        raise ValueError("MCDA weights must sum to a positive value.")
    return {k: v / total for k, v in cleaned.items()}

def mcda_score(criteria_scores, weights):
    normalized = normalize_weights(weights)
    missing = set(normalized) - set(criteria_scores)
    if missing:
        raise ValueError(f"Missing MCDA criterion scores: {sorted(missing)}")
    score = sum(float(criteria_scores[k]) * normalized[k] for k in normalized)
    return {
        "score": score,
        "normalized_weights": normalized,
        "criteria_scores": dict(criteria_scores),
    }

def classify_score(score):
    if score < 0.25:
        return "low"
    if score < 0.50:
        return "moderate"
    if score < 0.75:
        return "high"
    return "very_high"
