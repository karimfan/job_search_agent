import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://jobs-api.underdog.io/api/jobs/search"
JOB_BASE_URL = "https://underdog.io/startup-job-board"


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        page = 1
        collected = 0

        while collected < config.results_per_board:
            try:
                resp = httpx.get(
                    API_URL,
                    params={"page": page, "perPage": 20, "title": keyword},
                    timeout=15,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  Warning: Underdog request failed for '{keyword}' page {page}: {e}")
                break

            data = resp.json()
            jobs = data.get("objJobs", [])
            if not jobs:
                break

            for hit in jobs:
                slug = hit.get("slug", "")
                job_id = hit.get("id", "")
                job_url = f"{JOB_BASE_URL}/{slug}" if slug else ""
                if not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                cities = hit.get("objCities", [])
                location = ", ".join(
                    f"{c.get('name', '')}, {c.get('state_abbreviation', '')}" for c in cities
                ) if cities else ""

                salary = ""
                min_sal = hit.get("min_salary")
                max_sal = hit.get("max_salary")
                if min_sal and max_sal:
                    salary = f"${min_sal:,} - ${max_sal:,}"

                posted_date = None
                created = hit.get("created_at", "")
                if created:
                    posted_date = created[:10]

                all_jobs.append(Job(
                    title=hit.get("title", ""),
                    company="",  # API doesn't return company name in search results
                    location=location,
                    url=job_url,
                    source="underdog",
                    posted_date=posted_date,
                ))
                collected += 1

            pagination = data.get("pagination", {})
            total_pages = pagination.get("pages", pagination.get("totalPages", 0))
            if page >= total_pages:
                break
            page += 1

    return all_jobs
