from .market_intelligence import MarketIntelligenceAdapter
from .forecasting import ForecastingAdapter
from .gtm import GTMAdapter

ADAPTER_REGISTRY = {
    "market_intelligence": MarketIntelligenceAdapter,
    "forecasting": ForecastingAdapter,
    "gtm": GTMAdapter,
}
