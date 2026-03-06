"""Wellfound scraper — disabled.

Wellfound uses DataDome anti-bot protection that blocks headless browsers
with CAPTCHAs. This scraper is kept as a stub so imports don't break.
"""

from job_search_agent.config import Config
from job_search_agent.models import Job


def scrape(config: Config) -> list[Job]:
    print("  Warning: Wellfound is blocked by DataDome anti-bot (CAPTCHA). Skipping.")
    return []
