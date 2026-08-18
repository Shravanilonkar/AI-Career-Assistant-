"""
Synthetic Fusion API for AI Career Assistant
---------------------------------------------
This is a DEMO/local API wrapper. It does not call a real service.
It combines job records from the local synthetic dataset.
"""

import pandas as pd
from pathlib import Path

DATASET_PATH = Path(__file__).parent / "job_market_fusion_dataset.csv"


def load_dataset():
    return pd.read_csv(DATASET_PATH)


def search_jobs(keyword="", location=""):
    df = load_dataset()

    keyword = keyword.lower().strip()
    location = location.lower().strip()

    if keyword:
        mask = (
            df["job_title"].str.lower().str.contains(keyword, na=False)
            | df["skills"].str.lower().str.contains(keyword, na=False)
            | df["description"].str.lower().str.contains(keyword, na=False)
        )
        df = df[mask]

    if location:
        df = df[df["location"].str.lower().str.contains(location, na=False)]

    return df.reset_index(drop=True)


def fuse_job_data(adzuna_data, muse_data):
    """
    Combine records from two API-style sources into one DataFrame.
    Expected inputs: lists of dictionaries.
    """
    adzuna_df = pd.DataFrame(adzuna_data)
    muse_df = pd.DataFrame(muse_data)

    combined = pd.concat(
        [adzuna_df, muse_df],
        ignore_index=True
    )

    return combined.drop_duplicates().reset_index(drop=True)