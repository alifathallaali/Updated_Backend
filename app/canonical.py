import re
from datetime import datetime
from typing import Any

CANONICAL_FIELDS = [
    "sector", "atc4", "corporation", "product", "pack", "launch_date", "strength",
    "retail_price", "market_category", "period", "calendar_year", "sales_units",
    "sales_value", "currency",
]

ALIASES: dict[str, list[str]] = {
    "sector": ["sector", "distribution channel"],
    "atc4": ["atc4", "therapeutic class"],
    "corporation": ["corporation", "manufacturer", "company", "company name"],
    "product": ["product", "brand name", "brand_name"],
    "pack": ["pack", "pack size", "pack_size"],
    "launch_date": ["launch date", "product launch", "product launch date", "product_launch", "product_launch_date"],
    "strength": ["strength", "drug strength", "drug_strength"],
    "retail_price": ["retail price", "selling price", "selling_price", "price"],
    "market_category": ["market category", "market_category", "nfc3"],
    "period": ["period", "period month", "month", "calendar month", "calendar_month", "period_month"],
    "calendar_year": ["calendar year", "year", "calendar_year"],
    "sales_units": ["units", "sales units", "sales_units"],
    "sales_value": ["lc value", "sales value", "sales_value", "value", "revenue"],
    "currency": ["currency", "currency code", "currency_code", "iso currency", "iso_currency"],
}

NUMERIC_FIELDS = {"retail_price", "calendar_year", "sales_units", "sales_value"}


def _normalize(value: str) -> str:
    return re.sub(r"[\s-]+", "_", value.strip().lower())


def detect_schema(columns: list[str]) -> dict:
    normalized_columns = {_normalize(c): c for c in columns}
    mapping: dict[str, str] = {}
    for field in CANONICAL_FIELDS:
        for alias in ALIASES[field]:
            if _normalize(alias) in normalized_columns:
                mapping[field] = normalized_columns[_normalize(alias)]
                break
    mapped = len(mapping)
    return {
        "mapping": mapping,
        "mappedFields": mapped,
        "coverage": mapped / len(CANONICAL_FIELDS),
        "missingFields": [field for field in CANONICAL_FIELDS if field not in mapping],
    }


def _coerce(value: Any, field: str):
    if value is None or value == "":
        return None
    if field in NUMERIC_FIELDS:
        try:
            return float(str(value).replace(",", ""))
        except ValueError:
            return None
    return str(value).strip()


def map_rows(rows: list[dict], mapping: dict[str, str]) -> list[dict]:
    result = []
    for row in rows:
        mapped_row = {}
        for field in CANONICAL_FIELDS:
            source_col = mapping.get(field)
            mapped_row[field] = _coerce(row.get(source_col) if source_col else None, field)
        result.append(mapped_row)
    return result


def _outlier_count(values: list[float]) -> int:
    if len(values) < 4:
        return 0
    sorted_values = sorted(values)

    def quantile(q: float) -> float:
        idx = min(len(sorted_values) - 1, int((len(sorted_values) - 1) * q))
        return sorted_values[idx]

    q1, q3 = quantile(0.25), quantile(0.75)
    iqr = q3 - q1
    if iqr == 0:
        return 0
    lower, upper = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    return sum(1 for v in values if v < lower or v > upper)


def _normalize_currency_code(value: Any):
    if not isinstance(value, str):
        return None
    code = value.strip().upper()
    if re.match(r"^[A-Z]{3}$", code):
        return code
    return code or None


def _stable_row_key(row: dict) -> str:
    return "|".join(f"{field}:{row.get(field, '')}" for field in CANONICAL_FIELDS)


def govern_rows(rows: list[dict]) -> dict:
    """Deterministic, auditable governance: dedupe exact rows, normalize currency codes.
    No FX conversion is attempted without an explicit user-provided rate table."""
    seen: set[str] = set()
    governed_rows: list[dict] = []
    duplicate_rows_removed = 0
    normalized_currency_rows = 0

    for source_row in rows:
        row = dict(source_row)
        original_currency = row.get("currency")
        currency = _normalize_currency_code(original_currency)
        if currency != original_currency and currency is not None:
            row["currency"] = currency
            normalized_currency_rows += 1
        key = _stable_row_key(row)
        if key in seen:
            duplicate_rows_removed += 1
            continue
        seen.add(key)
        governed_rows.append(row)

    currencies = sorted({_normalize_currency_code(r.get("currency")) for r in governed_rows if _normalize_currency_code(r.get("currency"))})
    requires_fx_normalization = len(currencies) > 1
    outliers = {
        "salesValue": _outlier_count([r["sales_value"] for r in governed_rows if isinstance(r.get("sales_value"), (int, float)) and r["sales_value"] >= 0]),
        "salesUnits": _outlier_count([r["sales_units"] for r in governed_rows if isinstance(r.get("sales_units"), (int, float)) and r["sales_units"] >= 0]),
    }
    warnings = []
    if duplicate_rows_removed > 0:
        warnings.append(f"{duplicate_rows_removed} exact duplicate row(s) removed during governance.")
    if normalized_currency_rows > 0:
        warnings.append(f"{normalized_currency_rows} currency value(s) normalized to uppercase codes.")
    if requires_fx_normalization:
        warnings.append(f"Multiple currencies detected ({', '.join(currencies)}); monetary comparisons require an explicit FX rate table.")
    if outliers["salesValue"] > 0 or outliers["salesUnits"] > 0:
        warnings.append(f"{outliers['salesValue'] + outliers['salesUnits']} outlier value(s) flagged for review; no observations were removed.")

    return {
        "rows": governed_rows,
        "duplicateRowsRemoved": duplicate_rows_removed,
        "normalizedCurrencyRows": normalized_currency_rows,
        "currencies": currencies,
        "requiresFxNormalization": requires_fx_normalization,
        "outliers": outliers,
        "warnings": warnings,
    }


def validate_rows(rows: list[dict]) -> dict:
    issues: list[str] = []
    warnings: list[str] = []
    if not rows:
        issues.append("Dataset is empty.")
    required = ["product", "period", "sales_units", "sales_value"]
    for field in required:
        missing = sum(1 for r in rows if r.get(field) is None)
        if missing:
            issues.append(f"{field} is missing in {missing} row(s).")
    negative = sum(1 for r in rows if isinstance(r.get("sales_units"), (int, float)) and r["sales_units"] < 0)
    if negative:
        issues.append(f"sales_units is negative in {negative} row(s).")
    has_monetary_values = any(isinstance(r.get("sales_value"), (int, float)) for r in rows)
    has_currency = any(isinstance(r.get("currency"), str) and r["currency"].strip() for r in rows)
    if has_monetary_values and not has_currency:
        warnings.append("Currency is not specified; monetary metrics retain the source units.")

    invalid_periods = 0
    for r in rows:
        period = r.get("period")
        if period is None or str(period).strip() == "":
            continue
        text = str(period).strip()
        if not re.match(r"^\d{4}(-\d{1,2}(-\d{1,2})?)?$", text):
            try:
                datetime.fromisoformat(text)
            except ValueError:
                invalid_periods += 1
    if invalid_periods > 0:
        warnings.append(f"{invalid_periods} period value(s) need date validation.")

    keys = ["|".join(str(r.get(f)) for f in ["product", "period", "sales_units", "sales_value"]) for r in rows]
    duplicate_rows = len(keys) - len(set(keys))
    if duplicate_rows > 0:
        warnings.append(f"{duplicate_rows} possible duplicate row(s) detected.")

    sales_value_outliers = _outlier_count([r["sales_value"] for r in rows if isinstance(r.get("sales_value"), (int, float)) and r["sales_value"] >= 0])
    sales_units_outliers = _outlier_count([r["sales_units"] for r in rows if isinstance(r.get("sales_units"), (int, float)) and r["sales_units"] >= 0])
    if sales_value_outliers > 0:
        warnings.append(f"{sales_value_outliers} sales value outlier(s) need review.")
    if sales_units_outliers > 0:
        warnings.append(f"{sales_units_outliers} units outlier(s) need review.")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "rowCount": len(rows),
        "outliers": {"salesValue": sales_value_outliers, "salesUnits": sales_units_outliers},
        "duplicateRows": duplicate_rows,
    }


def profile_rows(rows: list[dict]) -> dict:
    return {
        "rowCount": len(rows),
        "fields": [
            {
                "field": field,
                "nonNull": sum(1 for r in rows if r.get(field) not in (None, "")),
                "distinct": len({r.get(field) for r in rows}),
            }
            for field in CANONICAL_FIELDS
        ],
    }
