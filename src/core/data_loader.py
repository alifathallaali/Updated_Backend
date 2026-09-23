import os
import pandas as pd


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "processed",
    "cleaned_pharma_data.parquet"
)


def load_pharma_data():

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(
            f"Processed dataset not found at: {DATA_PATH}"
        )

    df = pd.read_parquet(DATA_PATH)

    df.columns = (
        df.columns
        .astype(str)
        .str.strip()
    )

    return df