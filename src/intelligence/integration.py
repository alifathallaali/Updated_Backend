# ============================================================
# PharmaLens AI
# Integration Layer
# ============================================================

from pathlib import Path
import pandas as pd


# ------------------------------------------------------------
# Project Path
# ------------------------------------------------------------

PROJECT_ROOT = Path.cwd()

OUTPUT_DIR = PROJECT_ROOT / "outputs"

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ------------------------------------------------------------
# Save Notebook Output
# ------------------------------------------------------------

def save_output(df, name):

    if df is None:
        raise ValueError(
            "The DataFrame is None."
        )

    if not isinstance(df, pd.DataFrame):
        raise TypeError(
            "The output must be a pandas DataFrame."
        )

    file_path = OUTPUT_DIR / f"{name}.parquet"

    df.to_parquet(
        file_path,
        index=False
    )

    print("Output saved successfully!")
    print(f"File: {file_path}")
    print(f"Shape: {df.shape}")

    return file_path


# ------------------------------------------------------------
# Load Notebook Output
# ------------------------------------------------------------

def load_output(name):

    file_path = OUTPUT_DIR / f"{name}.parquet"

    if not file_path.exists():

        raise FileNotFoundError(
            f"Output file not found: {file_path}"
        )

    df = pd.read_parquet(file_path)

    print(f"Loaded: {name}")
    print(f"Shape: {df.shape}")

    return df


# ------------------------------------------------------------
# Check Available Outputs
# ------------------------------------------------------------

def list_outputs():

    files = list(
        OUTPUT_DIR.glob("*.parquet")
    )

    if not files:

        print("No outputs found yet.")

        return pd.DataFrame(
            columns=[
                "File",
                "Size_MB"
            ]
        )

    results = []

    for file in files:

        results.append({
            "File": file.name,
            "Size_MB": round(
                file.stat().st_size / (1024 * 1024),
                2
            )
        })

    return pd.DataFrame(results)