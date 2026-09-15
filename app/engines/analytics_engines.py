from ._helpers import build_output, evidence_for, grouped, number_of, text_of


def _period_of(row: dict) -> str:
    return text_of(row, "period", "month", "calendar_month", "year")


def run_market_intelligence(rows: list[dict], _input: dict) -> dict:
    total_value = sum(number_of(r, "sales_value", "lc_value", "salesValue", "value") for r in rows)
    total_units = sum(number_of(r, "sales_units", "units", "salesUnits") for r in rows)
    periods = {p for p in (_period_of(r) for r in rows) if p != "Unknown"}
    brands = grouped(rows, ["brand_name", "brand", "product"])
    companies = grouped(rows, ["corporation", "manufacturer", "company"])
    classes = grouped(rows, ["therapeutic_class", "atc4", "market_category"])

    def share(group):
        return (group["salesValue"] / total_value) * 100 if total_value > 0 and group else 0

    top = brands[0] if brands else None
    warnings = [] if rows else ["No canonical sales rows were available for market intelligence."]
    return build_output(
        "product-01",
        "Market summary and grouped market-share intelligence from the verified market_intelligence.py logic.",
        {
            "total_sales_value": total_value, "total_sales_units": total_units, "periods": len(periods),
            "manufacturers": len(companies), "brands": len(brands), "therapeutic_classes": len(classes),
            "top_brand": top["label"] if top else None, "top_brand_share_pct": share(top),
            "top_manufacturer": companies[0]["label"] if companies else None, "top_manufacturer_share_pct": share(companies[0] if companies else None),
            "top_therapeutic_class": classes[0]["label"] if classes else None, "top_therapeutic_class_share_pct": share(classes[0] if classes else None),
        },
        evidence_for("brand", top, "market_intelligence.py / canonical") if top else [],
        warnings,
    )


def run_company_intelligence(rows: list[dict], _input: dict) -> dict:
    companies = grouped(rows, ["corporation", "manufacturer", "company"])
    top = companies[0] if companies else None
    company_brands: dict[str, set] = {}
    company_classes: dict[str, set] = {}
    for row in rows:
        company = text_of(row, "corporation", "manufacturer", "company")
        company_brands.setdefault(company, set()).add(text_of(row, "brand_name", "brand", "product"))
        company_classes.setdefault(company, set()).add(text_of(row, "therapeutic_class", "atc4", "market_category"))
    warnings = [] if top else ["No corporation or manufacturer field was found."]
    return build_output(
        "product-02",
        "Manufacturer performance ranked with verified company aggregation logic from company.py.",
        {
            "company_count": len(companies), "top_company": top["label"] if top else None,
            "top_company_sales_value": top["salesValue"] if top else 0, "top_company_sales_units": top["salesUnits"] if top else 0,
            "top_company_brand_count": len(company_brands.get(top["label"], set())) if top else 0,
            "top_company_therapeutic_class_count": len(company_classes.get(top["label"], set())) if top else 0,
        },
        evidence_for("corporation", top, "company.py / canonical") if top else [],
        warnings,
    )


def run_brand_intelligence(rows: list[dict], _input: dict) -> dict:
    molecules = grouped(rows, ["molecule", "active_ingredient", "generic_name"])
    has_molecule = any(g["label"] != "Unknown" for g in molecules)
    if has_molecule:
        total_value = sum(g["salesValue"] for g in molecules)
        molecule_manufacturers: dict[str, dict[str, float]] = {}
        molecule_brands: dict[str, set] = {}
        molecule_classes: dict[str, set] = {}
        for row in rows:
            molecule = text_of(row, "molecule", "active_ingredient", "generic_name")
            if molecule == "Unknown":
                continue
            manufacturer = text_of(row, "corporation", "manufacturer", "company")
            sales = molecule_manufacturers.setdefault(molecule, {})
            sales[manufacturer] = sales.get(manufacturer, 0) + number_of(row, "sales_value", "lc_value", "salesValue", "value")
            molecule_brands.setdefault(molecule, set()).add(text_of(row, "brand_name", "brand", "product"))
            molecule_classes.setdefault(molecule, set()).add(text_of(row, "therapeutic_class", "atc4", "market_category"))
        top = molecules[0]
        manufacturer_sales = list(molecule_manufacturers.get(top["label"], {}).values())
        hhi = sum(((s / top["salesValue"]) * 100) ** 2 for s in manufacturer_sales) if top["salesValue"] > 0 else 0
        return build_output(
            "product-03",
            "Molecule market intelligence from active-ingredient aggregation, share, manufacturer concentration, and portfolio breadth.",
            {
                "intelligence_mode": "molecule", "molecule_count": len(molecules), "top_molecule": top["label"],
                "top_molecule_sales_value": top["salesValue"],
                "top_molecule_share_pct": (top["salesValue"] / total_value) * 100 if total_value > 0 else 0,
                "top_molecule_brand_count": len(molecule_brands.get(top["label"], set())),
                "top_molecule_manufacturer_count": len(molecule_manufacturers.get(top["label"], {})),
                "top_molecule_therapeutic_class_count": len(molecule_classes.get(top["label"], set())),
                "top_molecule_manufacturer_hhi": hhi,
            },
            evidence_for("molecule", top, "03_Molecule_Intelligence.ipynb / canonical"),
            [],
        )
    brands = grouped(rows, ["brand_name", "brand", "product"])
    top = brands[0] if brands else None
    return build_output(
        "product-03",
        "Brand performance baseline; molecule intelligence requires an active-ingredient field in the canonical dataset.",
        {"intelligence_mode": "brand_fallback", "brand_count": len(brands), "top_brand": top["label"] if top else None, "top_brand_sales_value": top["salesValue"] if top else 0},
        evidence_for("brand_name", top, "canonical") if top else [],
        ["No active-ingredient/molecule field was available; molecule-specific outputs were not calculated."],
    )


def run_product_performance(rows: list[dict], _input: dict) -> dict:
    products = grouped(rows, ["product", "brand_name"])
    prices = [number_of(r, "selling_price", "retail_price", "price") for r in rows]
    prices = [p for p in prices if p > 0]
    average_price = sum(prices) / len(prices) if prices else 0
    top = products[0] if products else None
    return build_output(
        "product-04",
        "Product, pack, strength, and price performance from canonical records.",
        {"product_count": len(products), "average_price": average_price, "top_product": top["label"] if top else None, "top_product_sales_value": top["salesValue"] if top else 0},
        evidence_for("product", top, "canonical") if top else [],
        [] if top else ["No product field was found."],
    )


def run_market_share_growth(rows: list[dict], _input: dict) -> dict:
    total_value = sum(number_of(r, "sales_value", "lc_value", "salesValue", "value") for r in rows)
    brands = grouped(rows, ["brand_name", "brand", "product"])
    manufacturers = grouped(rows, ["corporation", "manufacturer", "company"])
    classes = grouped(rows, ["therapeutic_class", "atc4", "market_category"])

    def share(group):
        return (group["salesValue"] / total_value) * 100 if total_value > 0 and group else 0

    leader = (brands[0] if brands else None) or (manufacturers[0] if manufacturers else None) or (classes[0] if classes else None)
    return build_output(
        "product-05",
        "Separate brand, manufacturer, and therapeutic-class share diagnostics from the verified market-intelligence grouping logic.",
        {
            "total_sales_value": total_value, "brand_group_count": len(brands), "manufacturer_group_count": len(manufacturers), "therapeutic_class_group_count": len(classes),
            "leading_brand": brands[0]["label"] if brands else None, "leading_brand_share_pct": share(brands[0] if brands else None),
            "leading_manufacturer": manufacturers[0]["label"] if manufacturers else None, "leading_manufacturer_share_pct": share(manufacturers[0] if manufacturers else None),
            "leading_therapeutic_class": classes[0]["label"] if classes else None, "leading_therapeutic_class_share_pct": share(classes[0] if classes else None),
        },
        evidence_for("market_share_leader", leader, "market_intelligence.py / canonical") if leader else [],
        [] if leader else ["No grouping field was found for share analysis."],
    )


ANALYTICS_ENGINES = {
    "product-01": run_market_intelligence,
    "product-02": run_company_intelligence,
    "product-03": run_brand_intelligence,
    "product-04": run_product_performance,
    "product-05": run_market_share_growth,
}
