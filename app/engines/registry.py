"""Compatibility shim; canonical registry is engine_registry.py."""
from .engine_registry import ENGINE_REGISTRY,list_registered_engines,run_product_engine
__all__=["ENGINE_REGISTRY","list_registered_engines","run_product_engine"]
