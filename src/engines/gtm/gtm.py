import pandas as pd



def channel_performance(df=None):

    if df is None:
        from src.core.data_loader import load_pharma_data
        df = load_pharma_data()

    result = (
        df.groupby("Distribution Channel")
        .agg(
            Sales_Value=("Sales Value", "sum"),
            Sales_Units=("Sales Units", "sum"),
            Brands=("Brand Name", "nunique")
        )
        .reset_index()
    )

    return result.sort_values(
        "Sales_Value",
        ascending=False
    )


def market_category_performance(df=None):

    if df is None:
        from src.core.data_loader import load_pharma_data
        df = load_pharma_data()

    return (
        df.groupby("Market Category")
        .agg(
            Sales_Value=("Sales Value", "sum"),
            Sales_Units=("Sales Units", "sum"),
            Brands=("Brand Name", "nunique")
        )
        .reset_index()
        .sort_values(
            "Sales_Value",
            ascending=False
        )
    )