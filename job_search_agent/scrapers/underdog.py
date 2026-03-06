import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://jobs-api.underdog.io/api/jobs/search"
JOB_BASE_URL = "https://underdog.io/startup-job-board"


def scrape(config: Config) -> list[Job]:
    # Underdog has ~83 total jobs and no working server-side search.
    # Fetch all jobs first, then filter client-side by keywords.
    all_raw: list[dict] = []
    page = 1

    while True:
        try:
            resp = httpx.get(
                API_URL,
                params={"page": page, "perPage": 50},
                timeout=15,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"  Warning: Underdog request failed page {page}: {e}")
            break

        data = resp.json()
        jobs = data.get("objJobs", [])
        if not jobs:
            break

        all_raw.extend(jobs)

        pagination = data.get("pagination", {})
        total_pages = pagination.get("pages", pagination.get("totalPages", 0))
        if page >= total_pages:
            break
        page += 1

    # Client-side keyword filtering
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for hit in all_raw:
        title = hit.get("title", "")
        if not any(kw.lower() in title.lower() for kw in config.search.keywords):
            continue

        slug = hit.get("slug", "")
        job_url = f"{JOB_BASE_URL}/{slug}" if slug else ""
        if not job_url or job_url in seen_urls:
            continue
        seen_urls.add(job_url)

        cities = hit.get("objCities", [])
        location = ", ".join(
            f"{c.get('name', '')}, {c.get('state_abbreviation', '')}" for c in cities
        ) if cities else ""

        posted_date = None
        created = hit.get("created_at", "")
        if created:
            posted_date = created[:10]

        all_jobs.append(Job(
            title=title,
            company="",
            location=location,
            url=job_url,
            source="underdog",
            posted_date=posted_date,
        ))

    return all_jobs
