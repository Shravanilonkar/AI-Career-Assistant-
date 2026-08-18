import pandas as pd
from pathlib import Path


def create_fusion_data(adzuna_data=None, muse_data=None):

    dataframes = []

    # Adzuna data
    if adzuna_data:
        adzuna_df = pd.DataFrame(adzuna_data)
        dataframes.append(adzuna_df)

    # The Muse data
    if muse_data:
        muse_df = pd.DataFrame(muse_data)
        dataframes.append(muse_df)

    # If API data is available
    if dataframes:

        combined_df = pd.concat(
            dataframes,
            ignore_index=True
        )

        return combined_df.drop_duplicates()

    # Otherwise return empty DataFrame
    return pd.DataFrame()