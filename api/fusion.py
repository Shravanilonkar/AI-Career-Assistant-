import pandas as pd

from api.adzuna_api import search_adzuna_jobs
from api.muse_api import search_muse_jobs


def create_fusion_data(job_keyword, location):

    # Call Adzuna API
    adzuna_data = search_adzuna_jobs(
        job_keyword,
        location
    )

    # Call The Muse API
    muse_data = search_muse_jobs(
        job_keyword,
        location
    )

    # Convert API results into DataFrames

    if isinstance(adzuna_data, list):
        adzuna_df = pd.DataFrame(adzuna_data)
    else:
        adzuna_df = pd.DataFrame()

    if isinstance(muse_data, list):
        muse_df = pd.DataFrame(muse_data)
    else:
        muse_df = pd.DataFrame()

    # Combine both API results

    combined_df = pd.concat(
        [
            adzuna_df,
            muse_df
        ],
        ignore_index=True
    )

    # Remove duplicate jobs

    if not combined_df.empty:
        combined_df = combined_df.drop_duplicates()

    return combined_df