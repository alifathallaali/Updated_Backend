import pandas as pd

from src.core.data_loader import load_pharma_data


def company_performance(df=None):

    if df is None:
        df = load_pharma_data()

    result = (
        df.groupby("Manufacturer")
        .agg(
            Sales_Value=("Sales Value", "sum"),
            Sales_Units=("Sales Units", "sum"),
            Brands=("Brand Name", "nunique"),
            Therapeutic_Classes=(
                "Therapeutic Class",
                "nunique"
            )
        )
        .reset_index()
    )

    return result.sort_values(
        "Sales_Value",
        ascending=False
    )


def top_companies(df=None, n=20):

    return company_performance(df).head(n)