
import os
import random
import requests
from pathlib import Path
from dotenv import load_dotenv

# ==================================================
# 1. Load API Key
# ==================================================

ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(ENV_PATH)

API_KEY = os.getenv("SERPAPI_API_KEY")
BASE_URL = "https://serpapi.com/search.json"

if not API_KEY:
    raise ValueError(
        "SERPAPI_API_KEY is missing. Check your .env file."
    )

print("SERPAPI TEST STARTED")
print("API Key loaded successfully.")


# ==================================================
# 2. Search Google Jobs
# ==================================================

def test_serpapi(keyword):

    params = {
        "engine": "google_jobs",
        "q": f"{keyword} jobs in Darmstadt",
        "location": "Darmstadt, Hessen, Germany",
        "google_domain": "google.de",
        "gl": "de",
        "hl": "de",
        "api_key": API_KEY
    }

    print("\n" + "=" * 60)
    print("Search keyword:", keyword)
    print("Search location: Darmstadt, Germany")

    try:
        response = requests.get(
            BASE_URL,
            params=params,
            timeout=45
        )

        print("HTTP status:", response.status_code)

        response.raise_for_status()
        data = response.json()

    except requests.RequestException as error:
        print("HTTP/Network error:", error)
        return []

    except ValueError as error:
        print("Invalid JSON response:", error)
        return []

    # ==================================================
    # 3. API Diagnostics
    # ==================================================

    metadata = data.get("search_metadata", {})
    search_params = data.get("search_parameters", {})

    print("\n--- API Diagnostics ---")

    print("Search status:", metadata.get("status"))
    print("Search ID:", metadata.get("id"))
    print("Location used:", search_params.get("location_used"))
    print("Query used:", search_params.get("q"))

    if data.get("error"):
        print("API error:", data["error"])
        return []

    jobs = data.get("jobs_results", [])

    print("\n--- API Results ---")
    print("Retrieved jobs:", len(jobs))

    if not jobs:
        print("No jobs returned for this search.")
        return []

    # ==================================================
    # 4. Field Completeness Evaluation
    # ==================================================

    fields = {
        "title": lambda job: job.get("title"),

        "company": lambda job: job.get("company_name"),

        "location": lambda job: job.get("location"),

        "description": lambda job: job.get("description"),

        "application_link": lambda job: any(
            option.get("link")
            for option in (job.get("apply_options") or [])
        ),

        "posting_date": lambda job: (
            job.get("detected_extensions") or {}
        ).get("posted_at")
    }

    print("\n--- Field Availability ---")

    for field, getter in fields.items():

        count = sum(
            bool(getter(job))
            for job in jobs
        )

        completeness = (
            count / len(jobs) * 100
            if jobs else 0
        )

        print(
            f"{field}: {count}/{len(jobs)} "
            f"({completeness:.1f}%)"
        )

    # ==================================================
    # 5. Randomly Inspect 5 Job Listings
    # ==================================================

    random.seed(42)

    samples = random.sample(
        jobs,
        min(5, len(jobs))
    )

    print("\n--- Random Job Samples ---")

    for i, job in enumerate(samples, 1):

        print(f"\n--- Job {i} ---")

        print("Title:", job.get("title", "Missing"))

        print(
            "Company:",
            job.get("company_name", "Missing")
        )

        print(
            "Location:",
            job.get("location", "Missing")
        )

        print(
            "Source:",
            job.get("via", "Missing")
        )

        print(
            "Posting date:",
            (job.get("detected_extensions") or {})
            .get("posted_at", "Missing")
        )

        description = job.get("description") or ""

        print(
            "Description:",
            description[:500]
        )

        options = job.get("apply_options") or []

        application_link = next(
            (
                option.get("link")
                for option in options
                if option.get("link")
            ),
            None
        )

        print(
            "Application link:",
            application_link or "Missing"
        )

        print(
            "Google share link:",
            job.get("share_link", "Missing")
        )

    return jobs


# ==================================================
# 6. Run Tests
# ==================================================

if __name__ == "__main__":

    # Test one occupation first to save API credits
    keywords = [
        "Senior Data Scientist"
    ]

    # After successful testing, use:
    # keywords = ["Data Scientist", "Data Analyst"]

    total_jobs = 0

    for keyword in keywords:

        results = test_serpapi(keyword)

        total_jobs += len(results)

    print("\n" + "=" * 60)
    print("TOTAL RETRIEVED:", total_jobs)
    print("TEST FINISHED")
