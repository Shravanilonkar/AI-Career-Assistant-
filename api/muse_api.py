import requests


def get_muse_jobs(keyword):

    url = "https://www.themuse.com/api/public/jobs"

    params = {
        "category": keyword,
        "page": 0
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    jobs = []

    for job in data.get("results", [])[:5]:

        company = job.get("company", {})
        location_list = job.get("locations", [])

        location = ""

        if location_list:
            location = location_list[0].get("name", "")

        jobs.append({
            "job_title": job.get("name", ""),
            "company": company.get("name", ""),
            "location": location,
            "description": job.get("contents", ""),
            "salary": "",
            "source": "The Muse"
        })

    return jobs