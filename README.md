# Job Search Agent

A tool that periodically scans job boards for roles matching your criteria and sends an email digest with the results.

## Overview

Job Search Agent runs as a scheduled task (via cron) that scrapes multiple job boards, deduplicates listings, and emails new matches to a configured list of recipients. Each run is self-contained — it executes, sends any new results, and exits.

## Architecture

```
┌──────┐    ┌──────────┐    ┌──────────┐    ┌─────────┐    ┌────────────┐
│ cron │───>│  runner   │───>│ scrapers │───>│ storage │───>│   email    │
└──────┘    └──────────┘    └──────────┘    └─────────┘    └────────────┘
```

- **Cron** — triggers the tool on a schedule; each invocation runs to completion and exits.
- **Runner** — loads config, orchestrates scraping, dedup, and email delivery.
- **Scrapers** — one module per job board, each returning a common Job model.
- **Storage** — SQLite database for persisting seen jobs and deduplication.
- **Email** — composes and sends a digest of new listings via SMTP.

### Target Job Boards

- [Welcome to the Jungle](https://global.welcometothejungle.com/)
- [BuiltIn](https://builtin.com/)
- [Wellfound](https://wellfound.com/)
- [Underdog.io](https://underdog.io/)

## Tech Stack

- **Python 3.11+**
- **SQLite** — job storage and deduplication
- **SMTP** (smtplib) — email delivery
- **YAML** — configuration (search criteria, recipients, schedule)
- **Cron** — scheduling

## Configuration

Search criteria, email recipients, and schedule are defined in a YAML config file. SMTP credentials and other secrets should be set via environment variables — never commit them to source control.

## Running

```bash
# Run once manually
python3 -m job_search_agent

# Schedule via cron (e.g. daily at 8am)
0 8 * * * cd /path/to/job_search_agent && python3 -m job_search_agent
```
