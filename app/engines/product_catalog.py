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

"""
Product Catalog Definitions.
Defines metadata, status, required inputs, and dependencies for all Product Engines.
"""

PRODUCT_CATALOG = [
    # ... منتجاتك الحالية ...
    {
        "id": "product-15",
        "name": "Commercial Recommendations Engine",
        "domain": "decide",
        "description": "Evidence-based commercial recommendations generated directly from canonical datasets.",
        "requiredInputs": ["product", "sales_value", "period"],
        "dependencies": ["canonical_sales"],
        "status": "production",
    },
    {
        "id": "product-16",
        "name": "Go-To-Market (GTM) Analytics",
        "domain": "decide",
        "description": "Distribution channel and commercial coverage analysis.",
        "requiredInputs": ["product", "period", "sales_value"],
        "dependencies": ["canonical_sales"],
        "status": "production",
    },
    {
        "id": "product-17",
        "name": "Commercial Finance Engine",
        "domain": "decide",
        "description": "Budget variance, financial achievement, and ROI analytics.",
        "requiredInputs": ["period", "sales_value"],
        "dependencies": ["canonical_sales"],
        "status": "production",
    },
]


def get_product_by_id(product_id: str):
    return next((p for p in PRODUCT_CATALOG if p["id"] == product_id), None)
