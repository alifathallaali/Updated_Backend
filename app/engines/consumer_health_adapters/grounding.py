"""Consumer Health semantic grounding over canonical PharmaLens rows."""
from __future__ import annotations
from typing import Iterable

CONSUMER_HEALTH_ALIASES = {
    "category": {"category","market_category","consumer_health_category","category_name","therapeutic_class"},
    "subcategory": {"subcategory","sub_category","segment","subsegment","sub_category_name"},
    "sku": {"sku","sku_code","item_code","product_code","ean","barcode","product","product_name"},
    "pack": {"pack","pack_size","packsize","size","package_size","presentation"},
    "channel": {"channel","distribution_channel","sales_channel","trade_channel"},
    "retailer": {"retailer","retail_chain","chain","customer_name","account_name","outlet"},
    "price": {"price","selling_price","retail_price","unit_price","net_price","list_price"},
    "distribution": {"distribution","numeric_distribution","weighted_distribution","stores_listed","outlets_listed"},
    "promotion": {"promotion","promo","discount","promo_spend","promotion_spend","promo_flag"},
    "consumer_segment": {"consumer_segment","shopper_segment","consumer_group","target_consumer"},
    "ecommerce": {"ecommerce","e_commerce","online_sales","online_channel","marketplace"},
}

def norm(value: str) -> str:
    return str(value).strip().lower().replace(" ", "_").replace("-", "_")

def resolve_column(columns: Iterable[str], semantic: str) -> str | None:
    available={norm(c):str(c) for c in columns}
    for candidate in {semantic,*CONSUMER_HEALTH_ALIASES.get(semantic,set())}:
        hit=available.get(norm(candidate))
        if hit: return hit
    return None

def grounding_map(columns: Iterable[str]) -> dict[str,str]:
    return {s:c for s in CONSUMER_HEALTH_ALIASES if (c:=resolve_column(columns,s))}
