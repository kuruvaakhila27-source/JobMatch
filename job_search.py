import os
import requests
from dotenv import load_dotenv


load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")


def search_jobs(
    keyword,
    location="India",
    results_per_page=10
):

    if not APP_ID or not APP_KEY:
        raise ValueError(
            "Adzuna API credentials are missing. "
            "Check your .env file."
        )

    url = (
        "https://api.adzuna.com/v1/api/jobs/in/search/1"
    )

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results_per_page,
        "what": keyword,
        "where": location,
        "content-type": "application/json"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    jobs = []

    for item in data.get("results", []):

        jobs.append({
            "title": item.get(
                "title",
                "Unknown Job"
            ),

            "company": item.get(
                "company",
                {}
            ).get(
                "display_name",
                "Unknown Company"
            ),

            "location": item.get(
                "location",
                {}
            ).get(
                "display_name",
                location
            ),

            "description": item.get(
                "description",
                ""
            ),

            "url": item.get(
                "redirect_url",
                ""
            ),

            "salary_min": item.get(
                "salary_min"
            ),

            "salary_max": item.get(
                "salary_max"
            )
        })

    return jobs