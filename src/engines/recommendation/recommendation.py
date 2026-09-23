import pandas as pd

from .data_loader import load_pharma_data


def opportunity_analysis(df=None):

    if df is None:
        df = load_pharma_data()

    # Move your existing Project 06
    # opportunity calculation here.

    return df


def top_opportunities(df=None, n=20):

    result = opportunity_analysis(df)

    if "Commercial_Opportunity_Score" in result.columns:

        return (
            result
            .sort_values(
                "Commercial_Opportunity_Score",
                ascending=False
            )
            .head(n)
        )

    return result.head(n)