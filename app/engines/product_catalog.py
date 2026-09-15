PRODUCT_READINESS_SUMMARY = {
    "product-01": {"state": "verified_subset", "source": "market_intelligence.py"},
    "product-02": {"state": "verified_subset", "source": "company.py"},
    "product-03": {"state": "verified_subset", "source": "03_Molecule_Intelligence.ipynb; requires active ingredient"},
    "product-04": {"state": "foundation_only", "source": "No complete product-specific routine mapped"},
    "product-05": {"state": "verified_subset", "source": "market_intelligence.py"},
    "product-06": {"state": "verified_subset", "source": "02_Advanced_pharmaceutical_Forecasting.ipynb; descriptive diagnostics only"},
    "product-07": {"state": "verified_subset", "source": "launch.py"},
    "product-08": {"state": "verified_subset", "source": "scenario.py"},
    "product-09": {"state": "foundation_only", "source": "recommendation.py is a placeholder"},
    "product-10": {"state": "foundation_only", "source": "No complete demand-planning routine mapped"},
    "product-11": {"state": "foundation_only", "source": "No complete supply-planning routine mapped"},
    "product-12": {"state": "additional_inputs", "source": "Requires inventory, lead-time, and service-level evidence"},
    "product-13": {"state": "additional_inputs", "source": "Requires activity, rep, and territory evidence"},
    "product-14": {"state": "foundation_only", "source": "Project 14 archive contains enterprise wrappers, not analytics"},
}

PRODUCT_CATALOG = [
    {"id": "product-01", "name": "Market Intelligence", "domain": "explore", "description": "Market structure, size, growth, and competitive signals.", "requiredInputs": ["period", "sales_value", "sales_units"], "dependencies": ["canonical_sales", "period_dimension"], "status": "foundation"},
    {"id": "product-02", "name": "Company Intelligence", "domain": "explore", "description": "Manufacturer and corporation performance intelligence.", "requiredInputs": ["corporation", "sales_value", "period"], "dependencies": ["canonical_sales", "corporation_dimension"], "status": "foundation"},
    {"id": "product-03", "name": "Brand Intelligence", "domain": "analyze", "description": "Brand performance, contribution, and movement.", "requiredInputs": ["brand_name", "sales_value", "sales_units", "period"], "dependencies": ["canonical_sales", "brand_dimension", "period_dimension"], "status": "foundation"},
    {"id": "product-04", "name": "Product Performance", "domain": "analyze", "description": "Product, pack, strength, and price performance.", "requiredInputs": ["product", "pack", "strength", "sales_value"], "dependencies": ["canonical_sales", "product_dimension", "price_dimension"], "status": "foundation"},
    {"id": "product-05", "name": "Market Share & Growth", "domain": "analyze", "description": "Share, growth, and contribution diagnostics.", "requiredInputs": ["market_category", "sales_value", "period"], "dependencies": ["canonical_sales", "market_definition", "period_dimension"], "status": "foundation"},
    {"id": "product-06", "name": "Forecasting", "domain": "strategize", "description": "Evidence-based demand and sales forecasting.", "requiredInputs": ["period", "sales_value", "sales_units"], "dependencies": ["canonical_sales", "period_dimension", "product-01"], "status": "foundation"},
    {"id": "product-07", "name": "Launch Success", "domain": "strategize", "description": "Launch tracking and early performance signals.", "requiredInputs": ["product_launch", "sales_value", "period"], "dependencies": ["canonical_sales", "launch_dimension", "period_dimension", "product-04"], "status": "foundation"},
    {"id": "product-08", "name": "Scenario Planning", "domain": "strategize", "description": "Comparable what-if scenarios and decision evidence.", "requiredInputs": ["period", "sales_value", "sales_units"], "dependencies": ["canonical_sales", "scenario_assumptions", "product-06"], "status": "foundation"},
    {"id": "product-09", "name": "Portfolio Strategy", "domain": "strategize", "description": "Portfolio prioritization and strategic opportunity mapping.", "requiredInputs": ["product", "sales_value", "growth"], "dependencies": ["canonical_sales", "product_dimension", "product-05", "product-06"], "status": "foundation"},
    {"id": "product-10", "name": "Demand Planning", "domain": "plan", "description": "Demand signals and planning assumptions.", "requiredInputs": ["period", "sales_units", "product"], "dependencies": ["canonical_sales", "period_dimension", "product-06"], "status": "foundation"},
    {"id": "product-11", "name": "Supply Planning", "domain": "plan", "description": "Supply requirements and service-level planning.", "requiredInputs": ["period", "sales_units", "product"], "dependencies": ["canonical_sales", "supply_constraints", "product-10"], "status": "foundation"},
    {"id": "product-12", "name": "Inventory Optimization", "domain": "plan", "description": "Inventory balance, risk, and working-capital decisions.", "requiredInputs": ["inventory", "demand", "service_level"], "dependencies": ["inventory_snapshot", "service_level_targets", "product-10", "product-11"], "status": "in_progress"},
    {"id": "product-13", "name": "Sales Force Effectiveness", "domain": "execute", "description": "Sales activity, coverage, and effectiveness planning.", "requiredInputs": ["sales_rep", "territory", "activity"], "dependencies": ["sales_activity", "territory_dimension", "product-02", "product-03"], "status": "in_progress"},
    {"id": "product-14", "name": "Business Review & Action Plan", "domain": "execute", "description": "Management review, actions, owners, and follow-up.", "requiredInputs": ["metric", "period", "owner"], "dependencies": ["canonical_sales", "action_register", "product-01", "product-05", "product-09"], "status": "foundation"},
]


def get_product_by_id(product_id: str):
    return next((p for p in PRODUCT_CATALOG if p["id"] == product_id), None)
