# ============================================================
# PHARMALENS AI
# src/launch.py
#
# Launch Success Intelligence
# Production Module
# ============================================================

import pandas as pd
import numpy as np


# ============================================================
# 1. REQUIRED COLUMNS
# ============================================================

REQUIRED_COLUMNS = [
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
# 2. LOAD DATA
# ============================================================

def load_launch_data(
    data_path="../data/processed/cleaned_pharma_data.parquet"
):
    """
    Load cleaned pharmaceutical sales data.
    """

    df = pd.read_parquet(data_path)

    return df


# ============================================================
# 3. VALIDATE DATA
# ============================================================

def validate_launch_data(df):
    """
    Validate that all required columns exist.
    """

    missing_columns = [
        col
        for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    return True


# ============================================================
# 4. PREPARE DATA
# ============================================================

def prepare_launch_data(df):
    """
    Prepare dates, numeric variables and Product_ID.
    """

    df = df.copy()

    # --------------------------------------------------------
    # Dates
    # --------------------------------------------------------

    df["Product Launch"] = pd.to_datetime(
        df["Product Launch"],
        errors="coerce"
    )

    df["Month"] = pd.to_datetime(
        df["Month"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "Year",
        "Sales Units",
        "Sales Value",
        "Selling Price"
    ]

    for col in numeric_columns:

        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Product ID
    # --------------------------------------------------------

    df["Product_ID"] = (
        df["Manufacturer"].fillna("").astype(str).str.strip()
        + " | "
        + df["Brand Name"].fillna("").astype(str).str.strip()
        + " | "
        + df["Drug Strength"].fillna("").astype(str).str.strip()
        + " | "
        + df["Pack Size"].fillna("").astype(str).str.strip()
    )

    return df


# ============================================================
# 5. IDENTIFY NEW PRODUCTS
# ============================================================

def identify_new_products(df):

    df = df.copy()

    df["Is_New_Product"] = (
        df["Product Launch"].notna()
    )

    return df


# ============================================================
# 6. CREATE LAUNCH FEATURES
# ============================================================

def create_launch_features(df):

    df = df.copy()

    df["Launch_Year"] = (
        df["Product Launch"].dt.year
    )

    df["Launch_Month"] = (
        df["Product Launch"].dt.month
    )

    df["Launch_Quarter"] = (
        df["Product Launch"].dt.quarter
    )

    df["Product_Age_Months"] = (
        (
            df["Month"].dt.year
            - df["Product Launch"].dt.year
        ) * 12
        +
        (
            df["Month"].dt.month
            - df["Product Launch"].dt.month
        )
    )

    df["Product_Age_Months"] = (
        df["Product_Age_Months"]
        .clip(lower=0)
    )

    return df


# ============================================================
# 7. CREATE PRODUCT LAUNCH TABLE
# ============================================================

def create_product_launch_table(df):

    launch_df = df[
        df["Is_New_Product"]
    ]

    product_launch = (
        launch_df
        .groupby("Product_ID")
        .agg(
            Manufacturer=(
                "Manufacturer",
                "first"
            ),

            Brand_Name=(
                "Brand Name",
                "first"
            ),

            Therapeutic_Class=(
                "Therapeutic Class",
                "first"
            ),

            Market_Category=(
                "Market Category",
                "first"
            ),

            Product_Launch=(
                "Product Launch",
                "first"
            ),

            Launch_Year=(
                "Launch_Year",
                "first"
            ),

            Launch_Quarter=(
                "Launch_Quarter",
                "first"
            ),

            Drug_Strength=(
                "Drug Strength",
                "first"
            ),

            Pack_Size=(
                "Pack Size",
                "first"
            ),

            Selling_Price=(
                "Selling Price",
                "first"
            )
        )
        .reset_index()
    )

    return product_launch


# ============================================================
# 8. FIRST 3 MONTHS
# ============================================================

def calculate_first_3_months(df):

    result = (
        df.loc[
            (df["Is_New_Product"]) &
            (df["Product_Age_Months"] <= 2),
            [
                "Product_ID",
                "Sales Units",
                "Sales Value",
                "Selling Price"
            ]
        ]
        .groupby("Product_ID")
        .agg(
            First_3M_Units=(
                "Sales Units",
                "sum"
            ),

            First_3M_Value=(
                "Sales Value",
                "sum"
            ),

            First_3M_Avg_Price=(
                "Selling Price",
                "mean"
            )
        )
        .reset_index()
    )

    return result


# ============================================================
# 9. FIRST 6 MONTHS
# ============================================================

def calculate_first_6_months(df):

    result = (
        df.loc[
            (df["Is_New_Product"]) &
            (df["Product_Age_Months"] <= 5),
            [
                "Product_ID",
                "Sales Units",
                "Sales Value"
            ]
        ]
        .groupby("Product_ID")
        .agg(
            First_6M_Units=(
                "Sales Units",
                "sum"
            ),

            First_6M_Value=(
                "Sales Value",
                "sum"
            )
        )
        .reset_index()
    )

    return result


# ============================================================
# 10. FIRST 12 MONTHS
# ============================================================

def calculate_first_12_months(df):

    result = (
        df.loc[
            (df["Is_New_Product"]) &
            (df["Product_Age_Months"] <= 11),
            [
                "Product_ID",
                "Sales Units",
                "Sales Value"
            ]
        ]
        .groupby("Product_ID")
        .agg(
            First_12M_Units=(
                "Sales Units",
                "sum"
            ),

            First_12M_Value=(
                "Sales Value",
                "sum"
            )
        )
        .reset_index()
    )

    return result


# ============================================================
# 11. PEAK PERFORMANCE
# ============================================================

def calculate_peak_performance(df):

    result = (
        df[
            df["Is_New_Product"]
        ]
        .groupby("Product_ID")
        .agg(
            Peak_Monthly_Units=(
                "Sales Units",
                "max"
            ),

            Peak_Monthly_Value=(
                "Sales Value",
                "max"
            )
        )
        .reset_index()
    )

    return result


# ============================================================
# 12. TIME TO PEAK
# ============================================================

def calculate_time_to_peak(df):

    peak_data = df.loc[
        df["Is_New_Product"],
        [
            "Product_ID",
            "Product_Age_Months",
            "Sales Value"
        ]
    ].dropna(
        subset=[
            "Product_ID",
            "Product_Age_Months",
            "Sales Value"
        ]
    )

    peak_idx = (
        peak_data
        .groupby("Product_ID")[
            "Sales Value"
        ]
        .idxmax()
    )

    result = (
        peak_data.loc[
            peak_idx,
            [
                "Product_ID",
                "Product_Age_Months"
            ]
        ]
        .rename(
            columns={
                "Product_Age_Months":
                    "Time_to_Peak_Months"
            }
        )
        .reset_index(drop=True)
    )

    return result


# ============================================================
# 13. LAUNCH GROWTH
# ============================================================

def calculate_launch_growth(df):

    growth_data = df.loc[
        df["Is_New_Product"],
        [
            "Product_ID",
            "Product_Age_Months",
            "Sales Value",
            "Sales Units"
        ]
    ].dropna(
        subset=[
            "Product_ID",
            "Product_Age_Months"
        ]
    )

    growth_data = growth_data.sort_values(
        [
            "Product_ID",
            "Product_Age_Months"
        ]
    )

    growth = (
        growth_data
        .groupby("Product_ID")
        .agg(
            First_Month_Value=(
                "Sales Value",
                "first"
            ),

            Latest_Value=(
                "Sales Value",
                "last"
            ),

            First_Month_Units=(
                "Sales Units",
                "first"
            ),

            Latest_Units=(
                "Sales Units",
                "last"
            )
        )
        .reset_index()
    )

    growth["Value_Growth_%"] = np.where(

        growth["First_Month_Value"] > 0,

        (
            (
                growth["Latest_Value"]
                /
                growth["First_Month_Value"]
            ) - 1
        ) * 100,

        np.nan
    )

    growth["Unit_Growth_%"] = np.where(

        growth["First_Month_Units"] > 0,

        (
            (
                growth["Latest_Units"]
                /
                growth["First_Month_Units"]
            ) - 1
        ) * 100,

        np.nan
    )

    return growth[
        [
            "Product_ID",
            "Value_Growth_%",
            "Unit_Growth_%"
        ]
    ]


# ============================================================
# 14. BUILD LAUNCH INTELLIGENCE
# ============================================================

def build_launch_intelligence(df):

    product_launch = (
        create_product_launch_table(df)
    )

    performance_tables = [
        calculate_first_3_months(df),
        calculate_first_6_months(df),
        calculate_first_12_months(df),
        calculate_peak_performance(df),
        calculate_time_to_peak(df),
        calculate_launch_growth(df)
    ]

    for table in performance_tables:

        product_launch = product_launch.merge(
            table,
            on="Product_ID",
            how="left",
            validate="one_to_one"
        )

    return product_launch


# ============================================================
# 15. BENCHMARK
# ============================================================

def calculate_launch_benchmark(
    product_launch
):

    metrics = [
        "First_3M_Value",
        "First_6M_Value",
        "First_12M_Value",
        "Peak_Monthly_Value"
    ]

    for col in metrics:

        product_launch[col] = pd.to_numeric(
            product_launch[col],
            errors="coerce"
        )

    benchmark = {

        "First_3M_Value_Median":
            product_launch[
                "First_3M_Value"
            ].median(),

        "First_6M_Value_Median":
            product_launch[
                "First_6M_Value"
            ].median(),

        "First_12M_Value_Median":
            product_launch[
                "First_12M_Value"
            ].median(),

        "Peak_Value_Median":
            product_launch[
                "Peak_Monthly_Value"
            ].median()
    }

    return benchmark


# ============================================================
# 16. LAUNCH SUCCESS SCORE
# ============================================================

def calculate_launch_success(
    product_launch,
    benchmark
):

    product_launch = product_launch.copy()

    product_launch["Score_3M"] = (
        product_launch["First_3M_Value"]
        >= benchmark[
            "First_3M_Value_Median"
        ]
    ).astype(int)

    product_launch["Score_6M"] = (
        product_launch["First_6M_Value"]
        >= benchmark[
            "First_6M_Value_Median"
        ]
    ).astype(int)

    product_launch["Score_12M"] = (
        product_launch["First_12M_Value"]
        >= benchmark[
            "First_12M_Value_Median"
        ]
    ).astype(int)

    product_launch["Score_Peak"] = (
        product_launch["Peak_Monthly_Value"]
        >= benchmark[
            "Peak_Value_Median"
        ]
    ).astype(int)

    product_launch[
        "Launch_Success_Score"
    ] = product_launch[
        [
            "Score_3M",
            "Score_6M",
            "Score_12M",
            "Score_Peak"
        ]
    ].sum(axis=1)

    return product_launch


# ============================================================
# 17. SUCCESS CATEGORY
# ============================================================

def classify_launch_success(score):

    if pd.isna(score):
        return "Unknown"

    if score == 4:
        return "Highly Successful"

    if score == 3:
        return "Successful"

    if score == 2:
        return "Moderate"

    if score == 1:
        return "Weak"

    return "Unsuccessful"


def add_success_categories(
    product_launch
):

    product_launch = product_launch.copy()

    product_launch[
        "Launch_Success_Category"
    ] = product_launch[
        "Launch_Success_Score"
    ].apply(
        classify_launch_success
    )

    return product_launch


# ============================================================
# 18. SUCCESS RATE
# ============================================================

def calculate_success_rate(
    product_launch
):

    successful = product_launch[
        "Launch_Success_Category"
    ].isin(
        [
            "Highly Successful",
            "Successful"
        ]
    )

    return successful.mean() * 100


# ============================================================
# 19. LAUNCH RISK
# ============================================================

def calculate_launch_risk(
    product_launch,
    benchmark
):

    product_launch = product_launch.copy()

    product_launch["Risk_3M"] = (
        product_launch["First_3M_Value"]
        < benchmark[
            "First_3M_Value_Median"
        ]
    ).astype(int)

    product_launch["Risk_6M"] = (
        product_launch["First_6M_Value"]
        < benchmark[
            "First_6M_Value_Median"
        ]
    ).astype(int)

    median_time_to_peak = (
        product_launch[
            "Time_to_Peak_Months"
        ].median()
    )

    product_launch["Risk_Peak"] = (
        product_launch[
            "Time_to_Peak_Months"
        ]
        > median_time_to_peak
    ).astype(int)

    product_launch["Risk_Growth"] = (
        product_launch[
            "Value_Growth_%"
        ] < 0
    ).astype(int)

    product_launch[
        "Launch_Risk_Score"
    ] = product_launch[
        [
            "Risk_3M",
            "Risk_6M",
            "Risk_Peak",
            "Risk_Growth"
        ]
    ].sum(axis=1)

    return product_launch


# ============================================================
# 20. RISK CATEGORY
# ============================================================

def classify_launch_risk(score):

    if pd.isna(score):
        return "Unknown"

    if score >= 3:
        return "High Risk"

    if score == 2:
        return "Medium Risk"

    if score == 1:
        return "Low Risk"

    return "Minimal Risk"


def add_risk_categories(
    product_launch
):

    product_launch = product_launch.copy()

    product_launch[
        "Launch_Risk_Category"
    ] = product_launch[
        "Launch_Risk_Score"
    ].apply(
        classify_launch_risk
    )

    return product_launch


# ============================================================
# 21. STRATEGIC SEGMENT
# ============================================================

def classify_strategic_launch(row):

    success = row[
        "Launch_Success_Category"
    ]

    risk = row[
        "Launch_Risk_Category"
    ]

    if (
        success == "Highly Successful"
        and risk in [
            "Minimal Risk",
            "Low Risk"
        ]
    ):
        return "Scale / Accelerate"

    if (
        success == "Successful"
        and risk in [
            "Minimal Risk",
            "Low Risk"
        ]
    ):
        return "Invest / Expand"

    if (
        success in [
            "Successful",
            "Moderate"
        ]
        and risk == "Medium Risk"
    ):
        return "Optimize"

    if success == "Moderate":
        return "Monitor"

    if risk == "High Risk":
        return "Intervention Required"

    return "Review / Deprioritize"


def add_strategic_launch_segments(
    product_launch
):

    product_launch = product_launch.copy()

    product_launch[
        "Strategic_Launch_Segment"
    ] = product_launch.apply(
        classify_strategic_launch,
        axis=1
    )

    return product_launch


# ============================================================
# 22. TOP SUCCESSFUL LAUNCHES
# ============================================================

def get_top_successful_launches(
    product_launch,
    n=50
):

    columns = [
        "Product_ID",
        "Manufacturer",
        "Brand_Name",
        "Therapeutic_Class",
        "Launch_Year",
        "First_3M_Value",
        "First_6M_Value",
        "First_12M_Value",
        "Peak_Monthly_Value",
        "Time_to_Peak_Months",
        "Launch_Success_Score",
        "Launch_Success_Category"
    ]

    available_columns = [
        col
        for col in columns
        if col in product_launch.columns
    ]

    return (
        product_launch
        .sort_values(
            [
                "Launch_Success_Score",
                "First_12M_Value"
            ],
            ascending=False
        )
        [available_columns]
        .head(n)
        .copy()
    )


# ============================================================
# 23. HIGH-RISK LAUNCHES
# ============================================================

def get_high_risk_launches(
    product_launch,
    n=50
):

    columns = [
        "Product_ID",
        "Manufacturer",
        "Brand_Name",
        "Therapeutic_Class",
        "Launch_Year",
        "Launch_Success_Score",
        "Launch_Success_Category",
        "Launch_Risk_Score",
        "Launch_Risk_Category",
        "Value_Growth_%",
        "Time_to_Peak_Months",
        "Strategic_Launch_Segment"
    ]

    available_columns = [
        col
        for col in columns
        if col in product_launch.columns
    ]

    return (
        product_launch[
            product_launch[
                "Launch_Risk_Category"
            ] == "High Risk"
        ]
        .sort_values(
            "Launch_Risk_Score",
            ascending=False
        )
        [available_columns]
        .head(n)
        .copy()
    )


# ============================================================
# 24. COMPLETE PIPELINE
# ============================================================

def run_launch_intelligence(
    data_path="../data/processed/cleaned_pharma_data.parquet"
):

    # --------------------------------------------------------
    # Load
    # --------------------------------------------------------

    df = load_launch_data(
        data_path
    )

    # --------------------------------------------------------
    # Validate
    # --------------------------------------------------------

    validate_launch_data(df)

    # --------------------------------------------------------
    # Prepare
    # --------------------------------------------------------

    df = prepare_launch_data(df)

    df = identify_new_products(df)

    df = create_launch_features(df)

    # --------------------------------------------------------
    # Build launch intelligence
    # --------------------------------------------------------

    product_launch = (
        build_launch_intelligence(df)
    )

    # --------------------------------------------------------
    # Benchmark
    # --------------------------------------------------------

    benchmark = (
        calculate_launch_benchmark(
            product_launch
        )
    )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    product_launch = (
        calculate_launch_success(
            product_launch,
            benchmark
        )
    )

    product_launch = (
        add_success_categories(
            product_launch
        )
    )

    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    product_launch = (
        calculate_launch_risk(
            product_launch,
            benchmark
        )
    )

    product_launch = (
        add_risk_categories(
            product_launch
        )
    )

    # --------------------------------------------------------
    # Strategy
    # --------------------------------------------------------

    product_launch = (
        add_strategic_launch_segments(
            product_launch
        )
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    success_rate = (
        calculate_success_rate(
            product_launch
        )
    )

    top_successful = (
        get_top_successful_launches(
            product_launch
        )
    )

    high_risk = (
        get_high_risk_launches(
            product_launch
        )
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "data": df,
        "product_launch": product_launch,
        "benchmark": benchmark,
        "success_rate": success_rate,
        "top_successful_launches": top_successful,
        "high_risk_launches": high_risk
    }


# ============================================================
# 25. DIRECT TEST
# ============================================================

if __name__ == "__main__":

    results = run_launch_intelligence()

    print("=" * 70)
    print("PHARMALENS AI — LAUNCH INTELLIGENCE")
    print("=" * 70)

    print(
        f"\nObservations: "
        f"{len(results['data']):,}"
    )

    print(
        f"Unique Products: "
        f"{results['data']['Product_ID'].nunique():,}"
    )

    print(
        f"Launches Analyzed: "
        f"{len(results['product_launch']):,}"
    )

    print(
        f"Launch Success Rate: "
        f"{results['success_rate']:.2f}%"
    )

    print("\nBenchmark:")

    for key, value in results[
        "benchmark"
    ].items():

        print(
            f"  {key}: {value:,.2f}"
        )

    print("\n✓ Launch Intelligence completed successfully.")