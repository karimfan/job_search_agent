import datetime

import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://himalayas.app/jobs/api"
PAGE_SIZE = 20  # API hard cap per request
MAX_SCAN_JOBS = 2000  # Scan up to 2000 recent jobs (100 API calls max)


def scrape(config: Config) -> list[Job]:
    # Himalayas has no server-side search. We fetch recent jobs in bulk
    # and filter client-side. We scan once and match all keywords.
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []
    offset = 0

    keywords_lower = [kw.lower() for kw in config.search.keywords]

    while offset < MAX_SCAN_JOBS:
        try:
            resp = httpx.get(
                API_URL,
                params={"limit": PAGE_SIZE, "offset": offset},
                timeout=15,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"  Warning: Himalayas request failed at offset {offset}: {e}")
            break

        data = resp.json()
        jobs = data.get("jobs", [])
        if not jobs:
            break

        for hit in jobs:
            title = hit.get("title", "")
            title_lower = title.lower()

            if not any(kw in title_lower for kw in keywords_lower):
                continue

            job_url = hit.get("applicationLink") or hit.get("guid", "")
            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            locations = hit.get("locationRestrictions", [])
            location = ", ".join(locations) if locations else ""

            posted_ts = hit.get("pubDate")
            posted_date = None
            if posted_ts:
                try:
                    posted_date = datetime.datetime.fromtimestamp(
                        posted_ts, tz=datetime.timezone.utc
                    ).strftime("%Y-%m-%d")
                except (OSError, ValueError):
                    pass

            all_jobs.append(Job(
                title=title,
                company=hit.get("companyName", ""),
                location=location,
                url=job_url,
                source="himalayas",
                remote=hit.get("employmentType"),
                posted_date=posted_date,
            ))

        offset += PAGE_SIZE

    return all_jobs


def _matches_keyword(title: str, keyword: str) -> bool:
    """Check if the full keyword phrase appears in the title."""
    return keyword.lower() in title.lower()
