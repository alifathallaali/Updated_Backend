"""
PharmaLens AI — Corporate Data Ingestion
Shared ingestion utilities for Project 11A.
"""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests


def api_get(url, headers=None, params=None, timeout=60, retries=3):
    headers = headers or {}
    last_error = None

    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=timeout,
            )
            response.raise_for_status()
            return response
        except requests.RequestException as exc:
            last_error = exc
            if attempt < retries - 1:
                time.sleep(2 ** attempt)

    raise last_error


def json_to_dataframe(payload, records_key=None):
    if payload is None:
        return pd.DataFrame()

    if records_key and isinstance(payload, dict):
        payload = payload.get(records_key, [])

    if isinstance(payload, dict):
        for key in ["records", "data", "results", "items"]:
            if key in payload:
                payload = payload[key]
                break

    if isinstance(payload, list):
        return pd.json_normalize(payload)

    if isinstance(payload, dict):
        return pd.json_normalize([payload])

    return pd.DataFrame()


def normalize_column_name(column):
    column = str(column).strip()
    for old, new in [
        (".", "_"),
        ("-", "_"),
        ("/", "_"),
        (" ", "_"),
    ]:
        column = column.replace(old, new)

    while "__" in column:
        column = column.replace("__", "_")

    return column.strip("_")


def normalize_dataframe_columns(df):
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


def save_parquet(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    return path


def add_ingestion_metadata(df, source, dataset_type):
    df = df.copy()
    df["_data_source"] = source
    df["_dataset_type"] = dataset_type
    df["_ingested_at"] = datetime.utcnow().isoformat()
    return df
