import datetime

import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://himalayas.app/jobs/api"
PAGE_SIZE = 20  # API max per request


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        collected = 0
        offset = 0
        # Paginate through results, filtering client-side by keyword
        max_pages = (config.results_per_board // PAGE_SIZE) + 3

        for _ in range(max_pages):
            if collected >= config.results_per_board:
                break

            try:
                resp = httpx.get(
                    API_URL,
                    params={"limit": PAGE_SIZE, "offset": offset},
                    timeout=15,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  Warning: Himalayas request failed for '{keyword}': {e}")
                break

            data = resp.json()
            jobs = data.get("jobs", [])
            if not jobs:
                break

            for hit in jobs:
                title = hit.get("title", "")
                if not _matches_keyword(title, keyword):
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
                collected += 1

            offset += PAGE_SIZE

    return all_jobs


def _matches_keyword(title: str, keyword: str) -> bool:
    """Check if any word from the keyword phrase appears in the title."""
    title_lower = title.lower()
    words = keyword.lower().split()
    return any(word in title_lower for word in words)
