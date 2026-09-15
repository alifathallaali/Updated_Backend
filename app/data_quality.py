"""Computes a 0-100 data quality score plus critical_errors/warnings/recommendations
for a mapped dataset. Deliberately transparent and rule-based (no invented scoring
weights presented as ML) so every number is explainable to a pharma user."""
from datetime import datetime


def _is_missing(value) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def assess_quality(rows: list[dict], mapping_confidence: dict[str, float]) -> dict:
    critical_errors: list[str] = []
    warnings: list[str] = []
    recommendations: list[str] = []

    if not rows:
        return {
            "qualityScore": 0,
            "criticalErrors": ["The dataset has no rows after mapping."],
            "warnings": [],
            "recommendations": ["Re-upload the file or check that the selected sheet/columns are correct."],
        }

    total = len(rows)
    fields = list(rows[0].keys())

    # Completeness
    completeness_scores = []
    for field in fields:
        missing = sum(1 for r in rows if _is_missing(r.get(field)))
        completeness = 1 - (missing / total)
        completeness_scores.append(completeness)
        if completeness < 0.5:
            critical_errors.append(f"'{field}' is missing in more than half of the rows ({missing}/{total}).")
        elif completeness < 0.9:
            warnings.append(f"'{field}' has {missing} missing value(s) out of {total} rows.")
    avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0

    # Duplicates
    seen = set()
    duplicate_count = 0
    for row in rows:
        key = "|".join(str(row.get(f, "")) for f in fields)
        if key in seen:
            duplicate_count += 1
        seen.add(key)
    duplicate_rate = duplicate_count / total
    if duplicate_rate > 0.1:
        critical_errors.append(f"{duplicate_count} duplicate rows detected ({round(duplicate_rate * 100)}% of the dataset).")
    elif duplicate_count > 0:
        warnings.append(f"{duplicate_count} possible duplicate row(s) detected.")

    # Numeric / negative-value checks
    numeric_fields = [f for f in fields if f in ("sales_value", "sales_units", "retail_price", "population")]
    invalid_numeric = 0
    negative_values = 0
    for field in numeric_fields:
        for row in rows:
            value = row.get(field)
            if _is_missing(value):
                continue
            try:
                numeric = float(value)
                if numeric < 0:
                    negative_values += 1
            except (TypeError, ValueError):
                invalid_numeric += 1
    if invalid_numeric:
        critical_errors.append(f"{invalid_numeric} value(s) in numeric fields could not be parsed as numbers.")
    if negative_values:
        warnings.append(f"{negative_values} negative value(s) found in fields that are normally non-negative.")

    # Date/period validity
    date_fields = [f for f in fields if f in ("period", "date")]
    invalid_dates = 0
    for field in date_fields:
        for row in rows:
            value = row.get(field)
            if _is_missing(value):
                continue
            text = str(value).strip()
            try:
                datetime.fromisoformat(text)
            except ValueError:
                if not __import__("re").match(r"^\d{4}(-\d{1,2}(-\d{1,2})?)?$", text):
                    invalid_dates += 1
    if invalid_dates:
        warnings.append(f"{invalid_dates} date/period value(s) could not be parsed.")

    # Mapping confidence contribution
    low_confidence_fields = [f for f, c in mapping_confidence.items() if c < 0.8]
    if low_confidence_fields:
        warnings.append(f"Column mapping confidence is low for: {', '.join(low_confidence_fields)}.")
    avg_mapping_confidence = (sum(mapping_confidence.values()) / len(mapping_confidence)) if mapping_confidence else 0.5

    score = round(
        100 * (
            0.4 * avg_completeness
            + 0.25 * (1 - min(duplicate_rate, 1))
            + 0.15 * (1 - min(invalid_numeric / max(total, 1), 1))
            + 0.2 * avg_mapping_confidence
        )
    )
    score = max(0, min(100, score))

    if score < 60:
        recommendations.append("Quality is low; review the critical errors above before running analytics on this dataset.")
    elif score < 85:
        recommendations.append("Quality is acceptable; review the warnings to improve confidence in downstream analytics.")
    else:
        recommendations.append("Quality is high; this dataset is ready for analytics and reporting.")
    if duplicate_count > 0:
        recommendations.append("Consider deduplicating the source file before re-uploading a new version.")

    return {
        "qualityScore": score,
        "criticalErrors": critical_errors,
        "warnings": warnings,
        "recommendations": recommendations,
    }
