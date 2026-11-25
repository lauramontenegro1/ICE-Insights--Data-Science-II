import requests
import os
import random
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).with_name(".env"))

API_KEY = os.getenv("JOOBLE_API_KEY")
BASE_URL = "https://de.jooble.org/api/"

if not API_KEY:
    raise ValueError("API Key is missing")


def test_jooble(keyword):

    payload = {
        "keywords": keyword,
        "location": "Germany",
        "page": 1,
        "ResultOnPage": 20
    }

    response = requests.post(
        BASE_URL + API_KEY,
        json=payload,
        timeout=15
    )

    print("\n" + "=" * 60)
    print("Search keyword:", keyword)
    print("HTTP status:", response.status_code)

    if response.status_code != 200:
        print("API request failed.")
        return

    data = response.json()
    jobs = data.get("jobs", [])

    print("Total job listings:", data.get("totalCount"))
    print("Retrieved jobs:", len(jobs))

    fields = [
        "title",
        "company",
        "salary",
        "snippet",
        "location",
        "link"
    ]

    # Check data availability
    print("\n--- Field Availability ---")

    for field in fields:
        count = sum(
            bool(job.get(field)) for job in jobs
        )
        print(f"{field}: {count}/{len(jobs)}")

    # Randomly select 5 job listings
    samples = random.sample(jobs, min(5, len(jobs)))

    for i, job in enumerate(samples, 1):

        print(f"\n--- Job {i} ---")

        for field in fields:
            print(f"{field}: {job.get(field) or 'Missing'}")


test_jooble("Data Scientist")
test_jooble("Data Analyst")