import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://remoteok.com/api"

# Stop words to strip when extracting search tags
_STOP_WORDS = {"of", "the", "a", "an", "and", "or", "in", "for", "to", "at", "by", "head"}


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    # Extract root terms from keywords + add common HR tags
    tags = _extract_tags(config.search.keywords) | {"hr", "recruiting", "recruiter"}
    keywords_lower = [kw.lower() for kw in config.search.keywords]

    fetched_ids: set[str] = set()
    fetched_jobs: list[dict] = []

    for tag in sorted(tags):
        try:
            resp = httpx.get(
                API_URL,
                params={"tag": tag},
                headers={"User-Agent": "JobSearchAgent/1.0"},
                timeout=15,
            )
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"  Warning: RemoteOK request failed for tag '{tag}': {e}")
            continue

        data = resp.json()
        for item in data:
            if isinstance(item, dict) and item.get("id"):
                item_id = str(item["id"])
                if item_id not in fetched_ids:
                    fetched_ids.add(item_id)
                    fetched_jobs.append(item)

    # Client-side keyword filtering on title
    for hit in fetched_jobs:
        title = hit.get("position", "")
        title_lower = title.lower()

        if not any(kw in title_lower for kw in keywords_lower):
            continue

        job_url = hit.get("apply_url") or hit.get("url", "")
        if not job_url or job_url in seen_urls:
            continue
        seen_urls.add(job_url)

        all_jobs.append(Job(
            title=title,
            company=hit.get("company", ""),
            location=hit.get("location", ""),
            url=job_url,
            source="remoteok",
            remote="remote",
            posted_date=hit.get("date", "")[:10] if hit.get("date") else None,
        ))

    return all_jobs


def _extract_tags(keywords: list[str]) -> set[str]:
    """Extract unique root terms from keyword phrases for tag-based APIs."""
    tags: set[str] = set()
    for kw in keywords:
        for word in kw.lower().split():
            if word not in _STOP_WORDS and len(word) > 2:
                tags.add(word)
    return tags
