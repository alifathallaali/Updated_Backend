"""
PharmaLens AI — External Data Intelligence
Reusable functions extracted from Project 11.
"""

from __future__ import annotations

import os
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
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


def fetch_json(url, headers=None, params=None, timeout=60):
    return api_get(
        url,
        headers=headers,
        params=params,
        timeout=timeout,
    ).json()


def normalize_column_name(column):
    column = str(column).strip()
    column = (
        column.replace(".", "_")
        .replace("-", "_")
        .replace("/", "_")
        .replace(" ", "_")
    )
    while "__" in column:
        column = column.replace("__", "_")
    return column.strip("_")


def normalize_dataframe_columns(df):
    df = df.copy()
    df.columns = [normalize_column_name(c) for c in df.columns]
    return df


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


def world_bank_indicator(
    country="EGY",
    indicator="SP.POP.TOTL",
    per_page=1000,
):
    url = (
        "https://api.worldbank.org/v2/"
        f"country/{country}/indicator/{indicator}"
    )

    payload = fetch_json(
        url,
        params={"format": "json", "per_page": per_page},
    )

    if not isinstance(payload, list) or len(payload) < 2:
        return pd.DataFrame()

    return normalize_dataframe_columns(
        pd.json_normalize(payload[1])
    )


def pubmed_search(term, retmax=20):
    url = (
        "https://eutils.ncbi.nlm.nih.gov/"
        "entrez/eutils/esearch.fcgi"
    )

    payload = fetch_json(
        url,
        params={
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retmax": retmax,
        },
    )

    ids = payload.get("esearchresult", {}).get("idlist", [])

    return pd.DataFrame({
        "PubMed_ID": ids,
        "Search_Term": term,
    })


def calculate_patient_flow(
    population,
    prevalence_rate,
    diagnosis_rate,
    treatment_rate,
    eligible_rate=1.0,
    access_rate=1.0,
):
    disease_population = float(population) * float(prevalence_rate)
    diagnosed = disease_population * float(diagnosis_rate)
    treated = diagnosed * float(treatment_rate)
    eligible = treated * float(eligible_rate)
    accessible = eligible * float(access_rate)

    return {
        "Population": float(population),
        "Disease_Population": disease_population,
        "Diagnosed_Patients": diagnosed,
        "Treated_Patients": treated,
        "Eligible_Patients": eligible,
        "Accessible_Patients": accessible,
    }


def add_source_metadata(
    df,
    source,
    category,
    retrieval_timestamp=None,
):
    df = df.copy()

    if retrieval_timestamp is None:
        retrieval_timestamp = datetime.now(
            timezone.utc
        ).isoformat()

    df["Data_Source"] = source
    df["Source_Category"] = category
    df["Retrieved_At_UTC"] = retrieval_timestamp

    return df
