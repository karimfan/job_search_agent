from job_search_agent.config import Config
from job_search_agent.models import Job
from job_search_agent.scrapers import (
    builtin, goinhouse, himalayas, jobicy, remoteok, remotive, themuse, underdog, wellfound, wttj,
)
from job_search_agent.storage import Storage

SCRAPERS = {
    "wttj": wttj.scrape,
    "himalayas": himalayas.scrape,
    "remotive": remotive.scrape,
    "themuse": themuse.scrape,
    "builtin": builtin.scrape,
    "underdog": underdog.scrape,
    "wellfound": wellfound.scrape,
    "jobicy": jobicy.scrape,
    "remoteok": remoteok.scrape,
    "goinhouse": goinhouse.scrape,
}


def run(config: Config) -> list[Job]:
    all_jobs: list[Job] = []

    for board in config.boards:
        scraper = SCRAPERS.get(board)
        if not scraper:
            print(f"Warning: unknown board '{board}', skipping")
            continue

        print(f"Scraping {board}...")
        jobs = scraper(config)
        print(f"  Found {len(jobs)} jobs")
        all_jobs.extend(jobs)

    if config.storage_enabled:
        storage = Storage(config.db_path)
        new_jobs = storage.save_jobs(all_jobs)
        storage.close()
        print(f"\n{len(new_jobs)} new job(s), {len(all_jobs) - len(new_jobs)} already seen")
        return new_jobs

    return all_jobs


def print_jobs(jobs: list[Job]) -> None:
    if not jobs:
        print("\nNo jobs found.")
        return

    print(f"\n{'=' * 60}")
    print(f" {len(jobs)} job(s) found")
    print(f"{'=' * 60}\n")

    for i, job in enumerate(jobs, 1):
        remote_tag = f" [{job.remote}]" if job.remote else ""
        location = job.location or "Not specified"
        print(f"{i}. {job.title}")
        print(f"   Company:  {job.company}")
        print(f"   Location: {location}{remote_tag}")
        if job.posted_date:
            print(f"   Posted:   {job.posted_date}")
        print(f"   URL:      {job.url}")
        print()
