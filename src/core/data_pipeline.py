# ============================================================
# PharmaLens AI
# Central Data Pipeline
# ============================================================

from pathlib import Path
import pandas as pd
import numpy as np


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path.cwd().parent

RAW_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "IMS (2021-2025).xlsx"
)

PROCESSED_DATA_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "cleaned_pharma_data.parquet"
)


# ============================================================
# EXPECTED FINAL COLUMN NAMES
# ============================================================

EXPECTED_COLUMNS = [
    "Distribution Channel",
    "Therapeutic Class",
    "Manufacturer",
    "Brand Name",
    "Pack Size",
    "Product Launch",
    "Drug Strength",
    "Selling Price",
    "Market Category",
    "Month",
    "Year",
    "Sales Units",
    "Sales Value"
]


# ============================================================
# 1. LOAD RAW EXCEL DATA
# ============================================================

def load_raw_data():

    print("Loading raw IMS dataset...")

    df = pd.read_excel(
        RAW_DATA_PATH
    )

    print(
        f"Raw data loaded successfully: "
        f"{df.shape[0]:,} rows × {df.shape[1]} columns"
    )

    return df


# ============================================================
# 2. RENAME COLUMNS
# ============================================================

def rename_columns(df):

    df = df.rename(columns={

        "Sector": "Distribution Channel",

        "ATC4": "Therapeutic Class",

        "Corporation": "Manufacturer",

        "Product": "Brand Name",

        "Pack": "Pack Size",

        "Launch Date": "Product Launch",

        "Strength": "Drug Strength",

        "Retail Price": "Selling Price",

        "NFC3": "Market Category",

        "Period": "Month",

        "Calendar Year": "Year",

        "Units": "Sales Units",

        "LC Value": "Sales Value"

    })

    return df


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

def validate_columns(df):

    missing_columns = [
        column
        for column in EXPECTED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns after renaming:\n"
            + "\n".join(
                f"- {column}"
                for column in missing_columns
            )
        )

    print("Column validation passed.")

    return True


# ============================================================
# 4. CLEAN DATA
# ============================================================

def clean_data(df):

    df = df.copy()

    # --------------------------------------------------------
    # Remove duplicate rows
    # --------------------------------------------------------

    df = df.drop_duplicates()

    # --------------------------------------------------------
    # Text columns
    # --------------------------------------------------------

    text_columns = [
        "Distribution Channel",
        "Therapeutic Class",
        "Manufacturer",
        "Brand Name",
        "Pack Size",
        "Drug Strength",
        "Market Category"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------------
    # Date columns
    # --------------------------------------------------------

    df["Product Launch"] = pd.to_datetime(
        df["Product Launch"],
        errors="coerce",
    format="mixed"
    )

    df["Month"] = pd.to_datetime(
        df["Month"],
        errors="coerce",
    format="mixed"
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "Selling Price",
        "Year",
        "Sales Units",
        "Sales Value"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Remove impossible negative values
    # --------------------------------------------------------

    df.loc[
        df["Selling Price"] < 0,
        "Selling Price"
    ] = np.nan

    df.loc[
        df["Sales Units"] < 0,
        "Sales Units"
    ] = np.nan

    df.loc[
        df["Sales Value"] < 0,
        "Sales Value"
    ] = np.nan

    return df


# ============================================================
# 5. CREATE COMMON FEATURES
# ============================================================

def create_features(df):

    df = df.copy()

    # --------------------------------------------------------
    # Revenue per Unit
    # --------------------------------------------------------

    df["Revenue_per_Unit"] = np.where(

        df["Sales Units"] > 0,

        df["Sales Value"] /
        df["Sales Units"],

        np.nan
    )

    # --------------------------------------------------------
    # Launch Year
    # --------------------------------------------------------

    df["Launch_Year"] = (
        df["Product Launch"]
        .dt.year
    )

    # --------------------------------------------------------
    # Product Age
    # --------------------------------------------------------

    df["Product_Age_Years"] = (
        df["Year"] -
        df["Launch_Year"]
    )

    # --------------------------------------------------------
    # New Product Flag
    # --------------------------------------------------------

    df["New_Product_Flag"] = np.where(

        df["Product_Age_Years"] <= 2,

        1,

        0
    )

    # --------------------------------------------------------
    # Month Number
    # --------------------------------------------------------

    df["Month_Number"] = (
        df["Month"]
        .dt.month
    )

    return df


# ============================================================
# 6. BUILD CLEANED MASTER DATASET
# ============================================================

def build_cleaned_data():

    print("\nStarting PharmaLens AI data pipeline...")

    # Load
    df = load_raw_data()

    # Rename
    df = rename_columns(df)

    # Validate AFTER renaming
    validate_columns(df)

    # Clean
    df = clean_data(df)

    # Features
    df = create_features(df)

    print("\nData pipeline completed successfully.")

    print(
        f"Final dataset: "
        f"{df.shape[0]:,} rows × "
        f"{df.shape[1]} columns"
    )

    return df


# ============================================================
# 7. SAVE CLEANED DATA
# ============================================================

def save_cleaned_data(df):

    PROCESSED_DATA_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_parquet(
        PROCESSED_DATA_PATH,
        index=False
    )

    print(
        "\nCleaned dataset saved to:"
    )

    print(
        PROCESSED_DATA_PATH
    )


# ============================================================
# 8. LOAD CLEANED DATA
# ============================================================

def load_cleaned_data():

    if not PROCESSED_DATA_PATH.exists():

        print(
            "Cleaned dataset not found."
        )

        print(
            "Building it from the raw Excel file..."
        )

        df = build_cleaned_data()

        save_cleaned_data(df)

        return df

    print(
        "Loading existing cleaned dataset..."
    )

    df = pd.read_parquet(
        PROCESSED_DATA_PATH
    )

    print(
        f"Cleaned data loaded: "
        f"{df.shape[0]:,} rows × "
        f"{df.shape[1]} columns"
    )

    return df