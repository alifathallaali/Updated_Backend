"""Company intelligence engine package.

Keep package import side-effect free so canonical bindings can import the
existing company capability without depending on removed legacy agent/tools.
"""

from .company import company_performance, top_companies

__all__ = ["company_performance", "top_companies"]
