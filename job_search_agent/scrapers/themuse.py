import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://www.themuse.com/api/public/jobs"
MAX_PAGES = 50  # Scan up to 1000 remote jobs for client-side keyword matching


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        page = 1
        collected = 0

        while collected < config.results_per_board and page <= MAX_PAGES:
            params: dict = {"page": page, "descending": "true"}

            # Use server-side location filter for remote jobs
            if config.search.remote:
                params["location"] = "Flexible / Remote"

            try:
                resp = httpx.get(
                    API_URL,
                    params=params,
                    timeout=15,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  Warning: The Muse request failed for '{keyword}' page {page}: {e}")
                break

            data = resp.json()
            results = data.get("results", [])
            if not results:
                break

            for hit in results:
                title = hit.get("name", "")
                if not _matches_keyword(title, keyword):
                    continue

                refs = hit.get("refs", {})
                job_url = refs.get("landing_page", "")
                if not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                locations = hit.get("locations", [])
                location = ", ".join(loc.get("name", "") for loc in locations)

                company = hit.get("company", {})

                pub_date = hit.get("publication_date", "")
                posted_date = pub_date[:10] if pub_date else None

                all_jobs.append(Job(
                    title=title,
                    company=company.get("name", ""),
                    location=location,
                    url=job_url,
                    source="themuse",
                    posted_date=posted_date,
                ))
                collected += 1

            page_count = data.get("page_count", 0)
            if page >= page_count:
                break
            page += 1

    return all_jobs


def _matches_keyword(title: str, keyword: str) -> bool:
    return keyword.lower() in title.lower()
