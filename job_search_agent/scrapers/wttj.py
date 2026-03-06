import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

ALGOLIA_APP_ID = "CSEKHVMS53"
ALGOLIA_API_KEY = "4bd8f6215d0cc52b26430765769e65a0"
ALGOLIA_INDEX = "wttj_jobs_production_en"
ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"

WTTJ_BASE_URL = "https://www.welcometothejungle.com/en/companies/{org_slug}/jobs/{job_slug}"

# Map common country names to ISO 3166-1 alpha-2 codes
COUNTRY_CODES = {
    "united states": "US",
    "usa": "US",
    "us": "US",
    "canada": "CA",
    "united kingdom": "GB",
    "uk": "GB",
    "france": "FR",
    "germany": "DE",
    "spain": "ES",
    "italy": "IT",
    "netherlands": "NL",
    "australia": "AU",
    "india": "IN",
    "brazil": "BR",
    "mexico": "MX",
    "japan": "JP",
    "singapore": "SG",
    "ireland": "IE",
    "sweden": "SE",
    "switzerland": "CH",
    "portugal": "PT",
    "poland": "PL",
    "belgium": "BE",
    "austria": "AT",
    "israel": "IL",
}


def scrape(config: Config) -> list[Job]:
    headers = {
        "x-algolia-application-id": ALGOLIA_APP_ID,
        "x-algolia-api-key": ALGOLIA_API_KEY,
        "Content-Type": "application/json",
        "Referer": "https://www.welcometothejungle.com/",
        "Origin": "https://www.welcometothejungle.com",
    }

    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    for keyword in config.search.keywords:
        params: dict = {
            "query": keyword,
            "hitsPerPage": config.results_per_board,
        }

        facet_filters: list[list[str]] = []
        if config.search.remote:
            facet_filters.append([f"remote:{config.search.remote}"])

        if config.search.location:
            country_code = COUNTRY_CODES.get(config.search.location.lower().strip())
            if country_code:
                facet_filters.append([f"offices.country_code:{country_code}"])
            else:
                # Treat as city name
                params["filters"] = f"offices.city:'{config.search.location}'"

        if facet_filters:
            params["facetFilters"] = facet_filters

        resp = httpx.post(ALGOLIA_URL, json=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        for hit in data.get("hits", []):
            org = hit.get("organization", {})
            offices = hit.get("offices", [])
            city = offices[0]["city"] if offices else ""

            job_url = WTTJ_BASE_URL.format(
                org_slug=org.get("slug", ""),
                job_slug=hit.get("slug", ""),
            )

            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            all_jobs.append(Job(
                title=hit.get("name", ""),
                company=org.get("name", ""),
                location=city,
                url=job_url,
                source="wttj",
                remote=hit.get("remote"),
                posted_date=hit.get("published_at_date"),
            ))

    return all_jobs
