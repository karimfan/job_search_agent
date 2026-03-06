from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class SearchConfig:
    keywords: list[str] = field(default_factory=list)
    location: str = ""
    remote: str = ""  # "fulltime", "partial", "hybrid", or "" for any


@dataclass
class Config:
    search: SearchConfig = field(default_factory=SearchConfig)
    boards: list[str] = field(default_factory=lambda: ["wttj"])
    results_per_board: int = 20
    storage_enabled: bool = False
    db_path: str = "jobs.db"


def load_config(path: str = "config.yaml") -> Config:
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(config_path) as f:
        raw = yaml.safe_load(f) or {}

    search_raw = raw.get("search", {})
    search = SearchConfig(
        keywords=search_raw.get("keywords", []),
        location=search_raw.get("location", ""),
        remote=search_raw.get("remote", ""),
    )

    return Config(
        search=search,
        boards=raw.get("boards", ["wttj"]),
        results_per_board=raw.get("results_per_board", 20),
        storage_enabled=raw.get("storage_enabled", False),
        db_path=raw.get("db_path", "jobs.db"),
    )
