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
- **Email** — composes and sends an HTML digest of new listings via SMTP.

### Supported Job Boards

- [Welcome to the Jungle](https://global.welcometothejungle.com/) — Algolia search API
- [Himalayas.app](https://himalayas.app/) — public JSON API
- [Remotive.com](https://remotive.com/) — public JSON API
- [The Muse](https://www.themuse.com/) — public JSON API
- [BuiltIn](https://builtin.com/) — HTML scraping (may be blocked by Cloudflare)
- [Underdog.io](https://underdog.io/) — public JSON API
- [Wellfound](https://wellfound.com/) — headless browser scraping (requires Playwright)

## Tech Stack

- **Python 3.11+**
- **SQLite** — job storage and deduplication
- **SMTP** (smtplib) — email delivery
- **YAML** — configuration (search criteria, recipients, schedule)
- **Cron** — scheduling
- **Playwright** (optional) — required only for Wellfound scraper

## Configuration

Search criteria, email recipients, and schedule are defined in a YAML config file. See `config.yaml.example` for all options.

## Email Notifications

Email is optional. To enable it, add an `email` section to your `config.yaml`:

```yaml
email:
  enabled: true
  recipients:
    - you@example.com
    - teammate@example.com
  subject_prefix: "[Job Search Agent]"
```

SMTP connection settings are loaded from environment variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `JSA_SMTP_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `JSA_SMTP_PORT` | SMTP port | `587` |
| `JSA_SMTP_USERNAME` | SMTP login username | `you@gmail.com` |
| `JSA_SMTP_PASSWORD` | SMTP login password | Gmail: use an [App Password](https://support.google.com/accounts/answer/185833) |
| `JSA_SMTP_FROM` | Sender email address | `you@gmail.com` |

### Gmail Setup

1. Enable 2-Step Verification on your Google account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Set environment variables:

```bash
export JSA_SMTP_HOST=smtp.gmail.com
export JSA_SMTP_PORT=587
export JSA_SMTP_USERNAME=you@gmail.com
export JSA_SMTP_PASSWORD=your-app-password
export JSA_SMTP_FROM=you@gmail.com
```

## Wellfound Setup (Optional)

Wellfound requires a headless browser to bypass anti-bot protection:

```bash
uv add playwright
playwright install chromium
```

Then add `wellfound` to your boards list in `config.yaml`.

## Running

```bash
# Run once manually
uv run python3 -m job_search_agent

# Schedule via cron (e.g. daily at 8am)
0 8 * * * cd /path/to/job_search_agent && uv run python3 -m job_search_agent
```
