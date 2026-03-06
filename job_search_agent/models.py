from dataclasses import dataclass


@dataclass
class Job:
    title: str
    company: str
    location: str
    url: str
    source: str
    remote: str | None = None
    posted_date: str | None = None
