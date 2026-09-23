import pandas as pd

from .data_loader import load_pharma_data


def molecule_summary(df=None):

    if df is None:
        df = load_pharma_data()

    # Replace this with the exact molecule/
    # active ingredient column produced
    # by your Project 03 pipeline.

    return df