import requests
import streamlit as st


def get_adzuna_jobs(keyword, location="India"):

    app_id = st.secrets["ADZUNA_APP_ID"]
    app_key = st.secrets["ADZUNA_APP_KEY"]

    url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

    params = {
        "app_id": app_id,
        "app_key": app_key,
        "what": keyword,
        "where": location,
        "results_per_page": 5
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    jobs = []

    for job in data.get("results", []):

        jobs.append({
            "job_title": job.get("title", ""),
            "company": job.get("company", {}).get("display_name", ""),
            "location": job.get("location", {}).get("display_name", ""),
            "description": job.get("description", ""),
            "salary": job.get("salary_min", ""),
            "source": "Adzuna"
        })

    return jobs