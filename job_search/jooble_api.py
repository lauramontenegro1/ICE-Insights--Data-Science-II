import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("JOOBLE_API_KEY")
BASE_URL = "https://de.jooble.org/api/"


def search_jobs(keywords, location="Germany", limit=10):

    if not API_KEY:
        raise ValueError("Jooble API Key is missing.")

    payload = {
        "keywords": keywords,
        "location": location,
        "page": 1,
        "ResultOnPage": limit
    }

    response = requests.post(
        BASE_URL + API_KEY,
        json=payload,
        timeout=15
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"API error: {response.status_code}"
        )

    data = response.json()

    jobs = []

    for job in data.get("jobs", [])[:limit]:
        jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "salary": job.get("salary", ""),
            "description": job.get("snippet", ""),
            "link": job.get("link", ""),
            "type": job.get("type", "")
        })

    return {
        "total_count": data.get("totalCount", 0),
        "jobs": jobs
    }


if __name__ == "__main__":

    result = search_jobs(
        keywords="Data Analyst",
        location="Frankfurt am Main",
        limit=10
    )

    print("Total jobs:", result["total_count"])

    for job in result["jobs"]:
        print(job["title"])
        print(job["company"])
        print(job["location"])
        print(job["link"])
        print("-" * 40)