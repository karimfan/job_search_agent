import json

import httpx
from bs4 import BeautifulSoup

from job_search_agent.config import Config
from job_search_agent.models import Job

BASE_URL = "https://builtin.com"
SEARCH_URL = f"{BASE_URL}/jobs/remote"

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def scrape(config: Config) -> list[Job]:
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        page = 1
        collected = 0

        while collected < config.results_per_board:
            params = {"search": keyword, "page": page}

            try:
                resp = httpx.get(
                    SEARCH_URL,
                    params=params,
                    headers=headers,
                    timeout=15,
                    follow_redirects=True,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  Warning: BuiltIn request failed for '{keyword}' page {page}: {e}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            page_jobs = _extract_jobs(soup)

            if not page_jobs:
                break

            for title, company, location, url in page_jobs:
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                all_jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    url=url,
                    source="builtin",
                ))
                collected += 1

            page += 1

    return all_jobs


def _extract_jobs(soup: BeautifulSoup) -> list[tuple[str, str, str, str]]:
    """Extract jobs using data-id selectors, with JSON-LD fallback."""
    jobs = _extract_from_html(soup)
    if not jobs:
        jobs = _extract_from_jsonld(soup)
    return jobs


def _extract_from_html(soup: BeautifulSoup) -> list[tuple[str, str, str, str]]:
    jobs: list[tuple[str, str, str, str]] = []

    job_links = soup.find_all("a", attrs={"data-id": "job-card-title"})
    for link in job_links:
        title = link.get_text(strip=True)
        href = link.get("href", "")
        if not title or not href:
            continue

        url = href if href.startswith("http") else BASE_URL + href

        # Find the job card container (3 levels up from the job link)
        card = link
        for _ in range(3):
            if card.parent:
                card = card.parent

        company = ""
        company_el = card.find("a", attrs={"data-id": "company-title"})
        if company_el:
            company = company_el.get_text(strip=True)

        location = ""

        jobs.append((title, company, location, url))

    return jobs


def _extract_from_jsonld(soup: BeautifulSoup) -> list[tuple[str, str, str, str]]:
    jobs: list[tuple[str, str, str, str]] = []

    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "")
        except (json.JSONDecodeError, TypeError):
            continue

        items = []
        if isinstance(data, dict):
            items = data.get("itemListElement", [])
        elif isinstance(data, list):
            for entry in data:
                if isinstance(entry, dict):
                    items.extend(entry.get("itemListElement", []))

        for item in items:
            name = item.get("name", "")
            url = item.get("url", "")
            if name and url:
                jobs.append((name, "", "", url))

    return jobs
