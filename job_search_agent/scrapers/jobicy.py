import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

API_URL = "https://jobicy.com/api/v2/remote-jobs"

# Map location strings to Jobicy geo codes
GEO_CODES = {
    "united states": "usa",
    "usa": "usa",
    "us": "usa",
    "canada": "canada",
    "united kingdom": "uk",
    "uk": "uk",
    "europe": "europe",
    "germany": "europe",
    "france": "europe",
}

# Stop words to strip when extracting search tags from keyword phrases
_STOP_WORDS = {"of", "the", "a", "an", "and", "or", "in", "for", "to", "at", "by", "head"}


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    geo = GEO_CODES.get(config.search.location.lower().strip(), "")
    tags = _extract_tags(config.search.keywords)
    keywords_lower = [kw.lower() for kw in config.search.keywords]

    for tag in tags:
        # Fetch with tag only (no industry filter — too restrictive combined with tag)
        params: dict = {"count": 50, "tag": tag}
        if geo:
            params["geo"] = geo

        try:
            resp = httpx.get(API_URL, params=params, timeout=15)
            resp.raise_for_status()
        except httpx.HTTPError as e:
            print(f"  Warning: Jobicy request failed for tag '{tag}': {e}")
            continue

        data = resp.json()
        for hit in data.get("jobs", []):
            title = hit.get("jobTitle", "")
            title_lower = title.lower()

            # Client-side: match if any keyword phrase appears in title
            if not any(kw in title_lower for kw in keywords_lower):
                continue

            job_url = hit.get("url", "")
            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            all_jobs.append(Job(
                title=title,
                company=hit.get("companyName", ""),
                location=hit.get("jobGeo", ""),
                url=job_url,
                source="jobicy",
                remote="remote",
                posted_date=hit.get("pubDate", "")[:10] if hit.get("pubDate") else None,
            ))

    # Also fetch the HR industry broadly and filter client-side
    params = {"count": 50, "industry": "hr"}
    if geo:
        params["geo"] = geo
    try:
        resp = httpx.get(API_URL, params=params, timeout=15)
        resp.raise_for_status()
        for hit in resp.json().get("jobs", []):
            title = hit.get("jobTitle", "")
            title_lower = title.lower()
            if not any(kw in title_lower for kw in keywords_lower):
                continue
            job_url = hit.get("url", "")
            if not job_url or job_url in seen_urls:
                continue
            seen_urls.add(job_url)
            all_jobs.append(Job(
                title=title,
                company=hit.get("companyName", ""),
                location=hit.get("jobGeo", ""),
                url=job_url,
                source="jobicy",
                remote="remote",
                posted_date=hit.get("pubDate", "")[:10] if hit.get("pubDate") else None,
            ))
    except httpx.HTTPError:
        pass

    return all_jobs


def _extract_tags(keywords: list[str]) -> list[str]:
    """Extract unique root terms from keyword phrases for tag-based APIs."""
    tags: set[str] = set()
    for kw in keywords:
        for word in kw.lower().split():
            if word not in _STOP_WORDS and len(word) > 2:
                tags.add(word)
    return sorted(tags)
