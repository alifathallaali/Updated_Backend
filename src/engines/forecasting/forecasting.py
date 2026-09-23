import pandas as pd

from src.core.data_loader import load_pharma_data


def prepare_forecasting_data(df=None):

    if df is None:
        df = load_pharma_data()

    data = df.copy()

    data["Month"] = pd.to_datetime(
        data["Month"]
    )

    monthly_market = (
        data.groupby("Month")["Sales Value"]
        .sum()
        .reset_index()
        .sort_values("Month")
    )

    return monthly_market


def calculate_market_growth(df=None):

    monthly_market = prepare_forecasting_data(df)

    monthly_market["Growth"] = (
        monthly_market["Sales Value"]
        .pct_change()
        * 100
    )

    return monthly_market


def get_forecast_summary(df=None):

    monthly_market = prepare_forecasting_data(df)

    return {
        "historical_periods": len(monthly_market),
        "latest_sales": monthly_market[
            "Sales Value"
        ].iloc[-1]
    }