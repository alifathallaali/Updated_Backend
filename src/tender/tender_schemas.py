from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TenderLineItem:
    line_id: str
    product_name: Optional[str] = None
    molecule: Optional[str] = None
    strength: Optional[str] = None
    dosage_form: Optional[str] = None
    pack_size: Optional[str] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    target_price: Optional[float] = None
    raw: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Tender:
    tender_id: Optional[str] = None
    issuer: Optional[str] = None
    country: Optional[str] = None
    issue_date: Optional[str] = None
    submission_deadline: Optional[str] = None
    currency: Optional[str] = None
    line_items: List[TenderLineItem] = field(default_factory=list)
    eligibility_requirements: List[str] = field(default_factory=list)
    commercial_terms: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)
