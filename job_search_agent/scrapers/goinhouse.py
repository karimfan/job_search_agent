import httpx
from bs4 import BeautifulSoup

from job_search_agent.config import Config
from job_search_agent.models import Job

SEARCH_URL = "https://www.goinhouse.com/jobs/search"
BASE_URL = "https://www.goinhouse.com"
MAX_PAGES = 10  # 20 results per page = 200 max per keyword


def scrape(config: Config) -> list[Job]:
    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    remote_param = ""
    if config.search.remote == "fulltime":
        remote_param = "full"
    elif config.search.remote == "partial":
        remote_param = "hybrid"

    for keyword in config.search.keywords:
        page = 1
        collected = 0

        while collected < config.results_per_board and page <= MAX_PAGES:
            params: dict = {"q": keyword, "page": page}
            if remote_param:
                params["remote"] = remote_param

            try:
                resp = httpx.get(
                    SEARCH_URL,
                    params=params,
                    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"},
                    timeout=15,
                    follow_redirects=True,
                )
                resp.raise_for_status()
            except httpx.HTTPError as e:
                print(f"  Warning: GoInhouse request failed for '{keyword}' page {page}: {e}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            listings = soup.find_all("li", class_="job-listing")

            if not listings:
                break

            for li in listings:
                title_link = li.find("a", class_="jobList-title")
                if not title_link:
                    continue

                title = title_link.get_text(strip=True)
                href = title_link.get("href", "")
                job_url = f"{BASE_URL}{href}" if href.startswith("/") else href

                if not job_url or job_url in seen_urls:
                    continue
                seen_urls.add(job_url)

                # Extract company and location from meta list
                company = ""
                location = ""
                remote = None
                meta_items = li.select("ul.jobList-introMeta li")
                if len(meta_items) >= 1:
                    company = meta_items[0].get_text(strip=True)
                if len(meta_items) >= 2:
                    location = meta_items[1].get_text(strip=True)
                if len(meta_items) >= 3:
                    work_type = meta_items[2].get_text(strip=True)
                    if work_type:
                        remote = work_type

                # Extract salary
                salary_el = li.find("div", class_="jobList-salary")
                salary = salary_el.get_text(strip=True) if salary_el else None

                # Extract posted date
                date_el = li.find("div", class_="jobList-date")
                posted_date = date_el.get_text(strip=True) if date_el else None

                all_jobs.append(Job(
                    title=title,
                    company=company,
                    location=location,
                    url=job_url,
                    source="goinhouse",
                    remote=remote,
                    posted_date=posted_date,
                ))
                collected += 1

            page += 1

    return all_jobs
