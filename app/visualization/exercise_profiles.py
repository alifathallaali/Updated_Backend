"""Scalable exercise-to-visual profile registry.

Profiles describe presentation intent, not analytical calculations.  Exact product
profiles override the generic resolver; future exercises can opt into a family
without requiring a new renderer.
"""
from __future__ import annotations

EXERCISE_PROFILES = {
    "market": {"patterns": ["trend", "brand_ranking", "company_ranking"], "role": "market"},
    "company": {"patterns": ["metrics", "trend", "brand_ranking"], "role": "market"},
    "molecule": {"patterns": ["metrics", "trend"], "role": "brand"},
    "product": {"patterns": ["metrics", "trend", "brand_ranking"], "role": "brand"},
    "forecast": {"patterns": ["trend", "metrics"], "role": "forecast"},
    "scenario": {"patterns": ["metrics", "trend"], "role": "forecast"},
    "launch": {"patterns": ["metrics", "trend"], "role": "opportunity"},
    "sales": {"patterns": ["metrics", "trend", "company_ranking"], "role": "opportunity"},
    "finance": {"patterns": ["metrics", "trend"], "role": "actual"},
    "supply": {"patterns": ["metrics", "unit_trend"], "role": "target"},
    "inventory": {"patterns": ["metrics", "unit_trend"], "role": "target"},
    "market_access": {"patterns": ["metrics", "company_ranking"], "role": "opportunity"},
    "medical": {"patterns": ["metrics", "trend"], "role": "actual"},
    "quality": {"patterns": ["metrics", "trend"], "role": "risk"},
    "generic": {"patterns": ["metrics", "trend", "brand_ranking"], "role": "actual"},
}

PRODUCT_PROFILE = {
    "product-01": "market", "product-02": "company", "product-03": "molecule",
    "product-04": "product", "product-05": "market", "product-06": "forecast",
    "product-07": "launch", "product-08": "scenario", "product-09": "product",
    "product-10": "supply", "product-11": "supply", "product-12": "inventory",
    "product-13": "sales", "product-14": "sales", "product-15": "sales",
    "product-16": "market_access", "product-17": "finance",
}

KEYWORDS = (
    (("forecast", "projection", "demand"), "forecast"),
    (("scenario", "what if", "simulation"), "scenario"),
    (("launch",), "launch"),
    (("inventory", "stock", "service level"), "inventory"),
    (("supply", "procurement", "tender"), "supply"),
    (("finance", "budget", "roi", "roci", "variance"), "finance"),
    (("access", "payer", "reimbursement", "heor"), "market_access"),
    (("medical", "kol", "scientific"), "medical"),
    (("quality", "capa", "deviation"), "quality"),
    (("sales", "territory", "rep", "target"), "sales"),
    (("company", "manufacturer"), "company"),
    (("molecule", "ingredient"), "molecule"),
    (("product", "brand"), "product"),
    (("market", "share", "growth"), "market"),
)

def resolve_profile(exercise_id: str, *, name: str = "", domain: str = "") -> tuple[str, dict]:
    family = PRODUCT_PROFILE.get(exercise_id)
    if not family:
        haystack = f"{exercise_id} {name} {domain}".lower()
        family = next((value for words, value in KEYWORDS if any(word in haystack for word in words)), "generic")
    return family, EXERCISE_PROFILES[family]
