import pandas as pd



def _load_default_data():
    from src.core.data_loader import load_pharma_data
    return load_pharma_data()


def market_summary(df=None):

    if df is None:
        df = _load_default_data()

    total_sales = df["Sales Value"].sum()
    total_units = df["Sales Units"].sum()

    manufacturers = df["Manufacturer"].nunique()
    brands = df["Brand Name"].nunique()
    therapeutic_classes = df["Therapeutic Class"].nunique()

    return {
        "total_sales": total_sales,
        "total_units": total_units,
        "manufacturers": manufacturers,
        "brands": brands,
        "therapeutic_classes": therapeutic_classes
    }


def market_share_by_brand(df=None):

    if df is None:
        df = _load_default_data()

    brand_sales = (
        df.groupby("Brand Name")["Sales Value"]
        .sum()
        .reset_index()
    )

    total_market = brand_sales["Sales Value"].sum()

    brand_sales["Market Share"] = (
        brand_sales["Sales Value"] /
        total_market
    ) * 100

    return brand_sales.sort_values(
        "Market Share",
        ascending=False
    )


def market_share_by_manufacturer(df=None):

    if df is None:
        df = _load_default_data()

    result = (
        df.groupby("Manufacturer")["Sales Value"]
        .sum()
        .reset_index()
    )

    total_market = result["Sales Value"].sum()

    result["Market Share"] = (
        result["Sales Value"] /
        total_market
    ) * 100

    return result.sort_values(
        "Market Share",
        ascending=False
    )


def market_share_by_therapeutic_class(df=None):

    if df is None:
        df = _load_default_data()

    result = (
        df.groupby("Therapeutic Class")["Sales Value"]
        .sum()
        .reset_index()
    )

    total_market = result["Sales Value"].sum()

    result["Market Share"] = (
        result["Sales Value"] /
        total_market
    ) * 100

    return result.sort_values(
        "Market Share",
        ascending=False
    )


def top_brands(df=None, n=20):

    result = market_share_by_brand(df)

    return result.head(n)


def top_manufacturers(df=None, n=20):

    result = market_share_by_manufacturer(df)

    return result.head(n)