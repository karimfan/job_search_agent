import json

from job_search_agent.config import Config
from job_search_agent.models import Job

ROLE_URL = "https://wellfound.com/role/l/{role}/{location}"

# Map common search terms to Wellfound role slugs
ROLE_SLUGS = {
    "software engineer": "software-engineer",
    "backend engineer": "backend-engineer",
    "frontend engineer": "frontend-engineer",
    "fullstack engineer": "fullstack-engineer",
    "data engineer": "data-engineer",
    "data scientist": "data-scientist",
    "product manager": "product-manager",
    "designer": "designer",
    "devops": "devops-engineer",
    "machine learning": "machine-learning-engineer",
    "recruiting": "recruiter",
    "recruiter": "recruiter",
    "recruiting manager": "recruiter",
    "recruiting director": "recruiter",
    "talent acquisition": "recruiter",
    "head of talent": "recruiter",
    "director of recruiting": "recruiter",
}


def scrape(config: Config) -> list[Job]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("  Warning: Wellfound requires 'playwright' package. "
              "Install with: uv add playwright && playwright install chromium")
        return []

    seen_urls: set[str] = set()
    all_jobs: list[Job] = []

    location = _to_location_slug(config.search.location)

    for keyword in config.search.keywords:
        role = _to_role_slug(keyword)
        url = ROLE_URL.format(role=role, location=location)

        try:
            jobs_data = _fetch_with_playwright(sync_playwright, url)
        except Exception as e:
            print(f"  Warning: Wellfound failed for '{keyword}': {e}")
            continue

        for title, company, loc, job_url, remote, posted in jobs_data:
            if job_url in seen_urls:
                continue
            seen_urls.add(job_url)

            all_jobs.append(Job(
                title=title,
                company=company,
                location=loc,
                url=job_url,
                source="wellfound",
                remote="remote" if remote else None,
                posted_date=posted,
            ))

            if len(all_jobs) >= config.results_per_board:
                return all_jobs

    return all_jobs


def _fetch_with_playwright(sync_playwright, url: str) -> list[tuple]:
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        try:
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            page.wait_for_timeout(3000)  # Wait for JS challenges

            content = page.content()
        except Exception as e:
            browser.close()
            raise RuntimeError(f"Page load failed: {e}")

        browser.close()

    if "__NEXT_DATA__" not in content:
        return []

    try:
        start = content.index('{"props"', content.index("__NEXT_DATA__"))
        end = content.index("</script>", start)
        next_data = json.loads(content[start:end])
    except (ValueError, json.JSONDecodeError):
        return []

    apollo = (next_data.get("props", {})
              .get("pageProps", {})
              .get("apolloState", {})
              .get("data", {}))

    if not apollo:
        return []

    # Build company lookup
    companies = {}
    for key, val in apollo.items():
        if key.startswith("StartupResult:") and isinstance(val, dict):
            companies[key] = val

    # Extract job listings
    for key, val in apollo.items():
        if not key.startswith("JobListingSearchResult:"):
            continue
        if not isinstance(val, dict):
            continue

        title = val.get("title", "")
        slug = val.get("slug", "")
        remote = val.get("remote", False)
        locations = val.get("locationNames", [])
        location = ", ".join(locations) if locations else ""

        posted = None
        live_start = val.get("liveStartAt")
        if live_start:
            import datetime
            try:
                posted = datetime.datetime.fromtimestamp(
                    live_start, tz=datetime.timezone.utc
                ).strftime("%Y-%m-%d")
            except (OSError, ValueError):
                pass

        # Find parent company
        company_name = ""
        for comp_key, comp in companies.items():
            highlighted = comp.get("highlightedJobListings", [])
            for ref in highlighted:
                if isinstance(ref, dict) and ref.get("__ref") == key:
                    company_name = comp.get("name", "")
                    break
            if company_name:
                break

        comp_slug = ""
        for comp_key, comp in companies.items():
            if comp.get("name") == company_name:
                comp_slug = comp.get("slug", "")
                break

        job_url = f"https://wellfound.com/company/{comp_slug}/jobs" if comp_slug else ""
        if not job_url:
            job_url = f"https://wellfound.com/role/l/{slug}"

        jobs.append((title, company_name, location, job_url, remote, posted))

    return jobs


def _to_role_slug(keyword: str) -> str:
    kw = keyword.lower().strip()
    if kw in ROLE_SLUGS:
        return ROLE_SLUGS[kw]
    return kw.replace(" ", "-")


def _to_location_slug(location: str) -> str:
    if not location:
        return "united-states"
    return location.lower().strip().replace(" ", "-")
