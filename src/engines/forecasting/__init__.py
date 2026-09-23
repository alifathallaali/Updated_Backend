"""Forecasting engine package.

Exports deterministic forecasting functions without importing the legacy agent
layer, which is not part of this engine package.
"""
from .forecasting import prepare_forecasting_data, calculate_market_growth, get_forecast_summary

__all__ = ["prepare_forecasting_data", "calculate_market_growth", "get_forecast_summary"]
