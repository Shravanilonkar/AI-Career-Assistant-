import pandas as pd

from api.adzuna_api import get_adzuna_jobs
from api.muse_api import get_muse_jobs


def create_fusion_data(keyword, location="India"):

    adzuna_jobs = get_adzuna_jobs(
        keyword,
        location
    )

    muse_jobs = get_muse_jobs(
        keyword
    )

    all_jobs = adzuna_jobs + muse_jobs

    df = pd.DataFrame(all_jobs)

    return df