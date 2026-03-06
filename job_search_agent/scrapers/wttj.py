import httpx

from job_search_agent.config import Config
from job_search_agent.models import Job

ALGOLIA_APP_ID = "CSEKHVMS53"
ALGOLIA_API_KEY = "4bd8f6215d0cc52b26430765769e65a0"
ALGOLIA_INDEX = "wttj_jobs_production_en"
ALGOLIA_URL = f"https://{ALGOLIA_APP_ID}-dsn.algolia.net/1/indexes/{ALGOLIA_INDEX}/query"

WTTJ_BASE_URL = "https://www.welcometothejungle.com/en/companies/{org_slug}/jobs/{job_slug}"


def scrape(config: Config) -> list[Job]:
    query = " ".join(config.search.keywords)
    params: dict = {
        "query": query,
        "hitsPerPage": config.results_per_board,
    }

    if config.search.remote:
        params["facetFilters"] = [[f"remote:{config.search.remote}"]]

    if config.search.location:
        params["aroundLatLngViaIP"] = False
        params["filters"] = f"offices.city:'{config.search.location}'"

    headers = {
        "x-algolia-application-id": ALGOLIA_APP_ID,
        "x-algolia-api-key": ALGOLIA_API_KEY,
        "Content-Type": "application/json",
        "Referer": "https://www.welcometothejungle.com/",
        "Origin": "https://www.welcometothejungle.com",
    }

    resp = httpx.post(ALGOLIA_URL, json=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    jobs = []
    for hit in data.get("hits", []):
        org = hit.get("organization", {})
        offices = hit.get("offices", [])
        city = offices[0]["city"] if offices else ""

        job_url = WTTJ_BASE_URL.format(
            org_slug=org.get("slug", ""),
            job_slug=hit.get("slug", ""),
        )

        jobs.append(Job(
            title=hit.get("name", ""),
            company=org.get("name", ""),
            location=city,
            url=job_url,
            source="wttj",
            remote=hit.get("remote"),
            posted_date=hit.get("published_at_date"),
        ))

    return jobs
