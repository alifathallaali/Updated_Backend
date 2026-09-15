"""Generalized auto-mapping engine: suggests which uploaded columns correspond to
PharmaLens unified data-model fields, with a confidence score per field, instead of
the pharma-sales-only mapping in canonical.py. This is deliberately broader (adds
HCP/HCO/territory/disease/population fields) since Dataset Registry uploads are not
limited to sales files."""
import re
from difflib import SequenceMatcher

UNIFIED_FIELDS: dict[str, list[str]] = {
    "product_name": ["product", "product name", "product_name", "drug name"],
    "brand_name": ["brand", "brand name", "brand_name"],
    "molecule": ["molecule", "active ingredient", "generic name", "inn"],
    "corporation": ["corporation", "manufacturer", "company", "company name"],
    "therapeutic_class": ["therapeutic class", "atc4", "class"],
    "pack": ["pack", "pack size"],
    "strength": ["strength", "drug strength"],
    "sales_value": ["sales value", "lc value", "value", "revenue"],
    "sales_units": ["units", "sales units"],
    "retail_price": ["retail price", "selling price", "price"],
    "currency": ["currency", "currency code", "iso currency"],
    "period": ["period", "month", "calendar month", "period month"],
    "calendar_year": ["year", "calendar year"],
    "country": ["country", "country name"],
    "region": ["region"],
    "territory_name": ["territory", "area", "district"],
    "hcp_name": ["doctor", "physician", "hcp", "hcp name"],
    "hco_name": ["hospital", "clinic", "hco", "facility", "hco name"],
    "disease": ["disease", "indication", "condition"],
    "population": ["population", "total population"],
    "date": ["date", "transaction date", "visit date"],
}


def _normalize(value: str) -> str:
    return re.sub(r"[\s_-]+", " ", value.strip().lower())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def suggest_mapping(columns: list[str]) -> dict:
    """Returns {field: {"column": str, "confidence": float}} for every unified
    field with at least one plausible match, plus a list of unmatched columns."""
    normalized_columns = {_normalize(c): c for c in columns}
    suggestions: dict[str, dict] = {}

    for field, aliases in UNIFIED_FIELDS.items():
        best_column = None
        best_score = 0.0
        for alias in aliases:
            norm_alias = _normalize(alias)
            if norm_alias in normalized_columns:
                best_column, best_score = normalized_columns[norm_alias], 1.0
                break
            for norm_col, original_col in normalized_columns.items():
                score = _similarity(norm_alias, norm_col)
                if score > best_score:
                    best_column, best_score = original_col, score
        if best_column and best_score >= 0.6:
            suggestions[field] = {"column": best_column, "confidence": round(best_score, 2)}

    mapped_columns = {s["column"] for s in suggestions.values()}
    unmatched_columns = [c for c in columns if c not in mapped_columns]

    warnings = []
    if not any(f in suggestions for f in ("sales_value", "sales_units")):
        warnings.append("No sales value or units field was detected; quantitative analysis may be limited.")
    low_confidence = [f for f, s in suggestions.items() if s["confidence"] < 0.8]
    if low_confidence:
        warnings.append(f"Low-confidence matches for: {', '.join(low_confidence)}. Please review before confirming.")

    return {
        "suggestions": suggestions,
        "unmatchedColumns": unmatched_columns,
        "coverage": len(suggestions) / len(UNIFIED_FIELDS),
        "warnings": warnings,
    }


def apply_confirmed_mapping(rows: list[dict], mapping: dict[str, str]) -> list[dict]:
    """mapping: {unified_field: source_column}. Renames/selects columns accordingly."""
    result = []
    for row in rows:
        mapped_row = {field: row.get(source_col) for field, source_col in mapping.items()}
        if row.get("source_sheet") is not None:
            mapped_row["source_sheet"] = row["source_sheet"]
        result.append(mapped_row)
    return result
