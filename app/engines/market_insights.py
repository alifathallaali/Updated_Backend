import re
import time

from ._helpers import number_of, text_of


def _top_groups(rows: list[dict], keys: list[str], limit: int = 5) -> list[dict]:
    groups: dict[str, dict] = {}
    for row in rows:
        label = text_of(row, *keys)
        current = groups.setdefault(label, {"label": label, "salesValue": 0.0, "salesUnits": 0.0})
        current["salesValue"] += number_of(row, "sales_value", "lc_value", "salesValue", "value")
        current["salesUnits"] += number_of(row, "sales_units", "units", "salesUnits")
    return sorted(groups.values(), key=lambda g: g["salesValue"], reverse=True)[:limit]


def build_market_insights(rows: list[dict], source: dict) -> dict:
    total_sales_value = sum(number_of(r, "sales_value", "lc_value", "salesValue", "value") for r in rows)
    total_sales_units = sum(number_of(r, "sales_units", "units", "salesUnits") for r in rows)
    periods = sorted({p for p in (text_of(r, "period", "month", "calendar_month", "year") for r in rows) if p != "Unknown"})
    countries = list({c for c in (text_of(r, "country", "market", "country_name") for r in rows) if c != "Unknown"})
    is_egypt_specific = any(re.search(r"egypt|\u0645\u0635\u0631", c, re.IGNORECASE) for c in countries)
    companies = _top_groups(rows, ["corporation", "manufacturer", "company"])
    brands = _top_groups(rows, ["brand_name", "brand", "product"])
    categories = _top_groups(rows, ["therapeutic_class", "atc4", "market_category"])

    warnings = list(source.get("validationWarnings", []))
    if not rows:
        warnings.append("No governed rows were available for this file.")
    if not is_egypt_specific:
        warnings.append("The file does not identify Egypt in a country or market field; this view is not labeled as Egypt-specific.")

    recommendations = (
        [
            f"Review concentration: {companies[0]['label']} is the leading manufacturer by available sales value." if companies else "Add a manufacturer or corporation field to assess competitive concentration.",
            f"Prioritize the leading therapeutic segment, {categories[0]['label']}, for deeper portfolio review." if categories else "Add ATC4 or therapeutic class fields to support segment prioritization.",
            "Add more reporting periods before relying on trend or forecast recommendations." if len(periods) < 6 else "Use the period coverage to validate seasonality and investigate material changes before action.",
        ]
        if rows else ["Upload a governed market file to generate evidence-based recommendations."]
    )

    return {
        "source": {**source, "isEgyptSpecific": is_egypt_specific},
        "scope": "Egypt pharmaceutical market" if is_egypt_specific else "Uploaded pharmaceutical market",
        "generatedAt": int(time.time() * 1000),
        "metrics": {
            "totalSalesValue": total_sales_value, "totalSalesUnits": total_sales_units, "governedRows": len(rows),
            "rawRows": source.get("rawRowCount", 0), "periods": len(periods), "companies": len(companies),
            "brands": len(brands), "categories": len(categories),
        },
        "periods": periods[-24:],
        "countries": countries,
        "topCompanies": companies,
        "topBrands": brands,
        "topCategories": categories,
        "warnings": warnings,
        "recommendations": recommendations,
    }
