from io import BytesIO

import pandas as pd
import requests

from . import canonical
from .storage import storage_get_signed_url

MAX_CANONICAL_ROWS = 25_000


def is_supported_canonical_file(file_name: str) -> bool:
    lower = file_name.lower()
    return lower.endswith((".csv", ".xlsx", ".xls", ".parquet"))


def load_raw_dataframe(file_name: str, storage_key: str) -> pd.DataFrame:
    """Loads a file from R2 as-is (no pharma-sales canonical mapping applied) — used by
    the general-purpose Dataset Registry, which accepts any tabular unified-model file."""
    lower = file_name.lower()
    if not is_supported_canonical_file(file_name) and not lower.endswith(".json"):
        raise ValueError("Supported formats: CSV, Excel, Parquet, JSON")

    signed_url = storage_get_signed_url(storage_key)
    response = requests.get(signed_url, timeout=60)
    if not response.ok:
        raise ValueError(f"Source download failed ({response.status_code})")
    data = BytesIO(response.content)

    if lower.endswith(".csv"):
        return pd.read_csv(data)
    if lower.endswith(".parquet"):
        return pd.read_parquet(data)
    if lower.endswith(".json"):
        return pd.read_json(data)
    sheets = pd.read_excel(data, sheet_name=None)
    frames = []
    for sheet_name, sheet_df in sheets.items():
        if sheet_df is not None and not sheet_df.empty:
            sheet_df = sheet_df.copy()
            sheet_df["source_sheet"] = str(sheet_name)
            frames.append(sheet_df)
    if not frames:
        raise ValueError("The Excel workbook has no non-empty sheets")
    return pd.concat(frames, ignore_index=True, sort=False)


def load_canonical_file(file) -> dict:
    """file: an UploadedFile ORM row (needs .file_name and .storage_key)."""
    lower = file.file_name.lower()
    if not is_supported_canonical_file(file.file_name):
        raise ValueError("Canonical processing currently supports CSV, Excel, and Parquet files")

    signed_url = storage_get_signed_url(file.storage_key)
    response = requests.get(signed_url, timeout=60)
    if not response.ok:
        raise ValueError(f"Source download failed ({response.status_code})")
    data = BytesIO(response.content)

    if lower.endswith(".csv"):
        df = pd.read_csv(data)
    elif lower.endswith(".parquet"):
        df = pd.read_parquet(data)
    else:
        sheets = pd.read_excel(data, sheet_name=None)
        frames = []
        for sheet_name, sheet_df in sheets.items():
            if sheet_df is not None and not sheet_df.empty:
                sheet_df = sheet_df.copy()
                sheet_df["source_sheet"] = str(sheet_name)
                frames.append(sheet_df)
        if not frames:
            raise ValueError("The Excel workbook has no non-empty sheets")
        df = pd.concat(frames, ignore_index=True, sort=False)

    raw_row_count = len(df)
    df = df.head(MAX_CANONICAL_ROWS)
    raw_rows = df.where(pd.notnull(df), None).to_dict(orient="records")

    schema = canonical.detect_schema(list(df.columns) if raw_rows else [])
    mapped_rows = canonical.map_rows(raw_rows, schema["mapping"])
    governance = canonical.govern_rows(mapped_rows)
    validation = canonical.validate_rows(governance["rows"])

    return {
        "file": file,
        "rawRowCount": raw_row_count,
        "schema": schema,
        "rows": governance["rows"],
        "validation": {
            **validation,
            "warnings": [*governance["warnings"], *validation["warnings"]],
        },
        "profile": canonical.profile_rows(governance["rows"]),
        "governance": {
            "duplicateRowsRemoved": governance["duplicateRowsRemoved"],
            "normalizedCurrencyRows": governance["normalizedCurrencyRows"],
            "currencies": governance["currencies"],
            "requiresFxNormalization": governance["requiresFxNormalization"],
            "outliers": governance["outliers"],
        },
    }


def load_canonical_dataset_version(version) -> dict:
    """Load a governed DatasetVersion directly, without converting it to UploadedFile.

    The curated object is preferred when available; it is the output of the existing
    mapping and quality pipeline. Raw storage remains the fallback for versions that
    have not completed curation yet.
    """
    storage_key = version.curated_storage_key or version.raw_storage_key
    df = load_raw_dataframe(version.file_name, storage_key)
    raw_row_count = len(df)
    df = df.head(MAX_CANONICAL_ROWS)
    raw_rows = df.where(pd.notnull(df), None).to_dict(orient="records")
    schema = canonical.detect_schema(list(df.columns) if raw_rows else [])
    mapped_rows = canonical.map_rows(raw_rows, schema["mapping"])
    governance = canonical.govern_rows(mapped_rows)
    validation = canonical.validate_rows(governance["rows"])
    return {
        "version": version,
        "rawRowCount": raw_row_count,
        "schema": schema,
        "rows": governance["rows"],
        "validation": {**validation, "warnings": [*governance["warnings"], *validation["warnings"]]},
        "profile": canonical.profile_rows(governance["rows"]),
        "governance": {
            "duplicateRowsRemoved": governance["duplicateRowsRemoved"],
            "normalizedCurrencyRows": governance["normalizedCurrencyRows"],
            "currencies": governance["currencies"],
            "requiresFxNormalization": governance["requiresFxNormalization"],
            "outliers": governance["outliers"],
        },
        "source": {
            "datasetVersionId": version.id,
            "datasetId": version.dataset_id,
            "fileName": version.file_name,
            "storageLayer": "curated" if version.curated_storage_key else "raw",
            "versionNumber": version.version_number,
            "processingStatus": version.status.value if hasattr(version.status, "value") else version.status,
        },
    }
