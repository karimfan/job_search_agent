import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://remotive.com/api/remote-jobs"


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        try:
            resp = httpx.get(
                API_URL,
                params={"search": keyword},
                timeout=15,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"  Warning: Remotive request failed for '{keyword}': {e}")
            continue

        for hit in resp.json().get("jobs", []):
            job_url = hit.get("url", "")
            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            pub_date = hit.get("publication_date", "")
            posted_date = pub_date[:10] if pub_date else None

            all_jobs.append(Job(
                title=hit.get("title", ""),
                company=hit.get("company_name", ""),
                location=hit.get("candidate_required_location", ""),
                url=job_url,
                source="remotive",
                remote=hit.get("job_type"),
                posted_date=posted_date,
            ))

    return all_jobs
