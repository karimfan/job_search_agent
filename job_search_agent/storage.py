import sqlite3
from pathlib import Path

from job_search_agent.models import Job

DEFAULT_DB_PATH = "jobs.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    url TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    company TEXT NOT NULL,
    location TEXT,
    source TEXT NOT NULL,
    remote TEXT,
    posted_date TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


class Storage:
    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.execute(SCHEMA)
        self._conn.commit()

    def save_jobs(self, jobs: list[Job]) -> list[Job]:
        """Save jobs and return only the newly inserted ones."""
        new_jobs = []
        for job in jobs:
            try:
                self._conn.execute(
                    "INSERT INTO jobs (url, title, company, location, source, remote, posted_date) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (job.url, job.title, job.company, job.location, job.source, job.remote, job.posted_date),
                )
                new_jobs.append(job)
            except sqlite3.IntegrityError:
                pass  # already exists
        self._conn.commit()
        return new_jobs

    def close(self) -> None:
        self._conn.close()
