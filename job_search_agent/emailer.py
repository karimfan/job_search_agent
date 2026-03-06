import os
import smtplib
from datetime import date
from email.message import EmailMessage

from job_search_agent.config import Config
from job_search_agent.models import Job


def send_digest(jobs: list[Job], config: Config) -> bool:
    if not config.email.enabled:
        return False

    if not config.email.recipients:
        print("  Warning: Email enabled but no recipients configured")
        return False

    if not jobs:
        return False

    host = os.environ.get("JSA_SMTP_HOST", "")
    port = int(os.environ.get("JSA_SMTP_PORT", "587"))
    username = os.environ.get("JSA_SMTP_USERNAME", "")
    password = os.environ.get("JSA_SMTP_PASSWORD", "")
    from_addr = os.environ.get("JSA_SMTP_FROM", "")

    if not host or not username or not password or not from_addr:
        missing = []
        if not host:
            missing.append("JSA_SMTP_HOST")
        if not username:
            missing.append("JSA_SMTP_USERNAME")
        if not password:
            missing.append("JSA_SMTP_PASSWORD")
        if not from_addr:
            missing.append("JSA_SMTP_FROM")
        print(f"  Warning: Missing SMTP env vars: {', '.join(missing)}")
        return False

    subject = f"{config.email.subject_prefix} {len(jobs)} jobs found — {date.today()}"
    html_body = _build_html(jobs)
    text_body = _build_text(jobs)

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ", ".join(config.email.recipients)
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(username, password)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"  Warning: Failed to send email: {e}")
        return False


def _build_html(jobs: list[Job]) -> str:
    rows = ""
    for job in jobs:
        remote_badge = ""
        if job.remote:
            remote_badge = f' <span style="background:#e0f2fe;color:#0369a1;padding:2px 6px;border-radius:3px;font-size:12px;">{job.remote}</span>'

        posted = f"<br><small style='color:#888;'>Posted: {job.posted_date}</small>" if job.posted_date else ""

        rows += f"""
        <tr style="border-bottom:1px solid #eee;">
            <td style="padding:12px 8px;">
                <a href="{job.url}" style="color:#1a56db;text-decoration:none;font-weight:600;">{job.title}</a>{remote_badge}
                <br><span style="color:#555;">{job.company}</span>
                {f'<br><span style="color:#777;">{job.location}</span>' if job.location else ''}
                {posted}
            </td>
            <td style="padding:12px 8px;color:#888;font-size:13px;">{job.source}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;max-width:700px;margin:0 auto;padding:20px;">
    <h2 style="color:#1a1a1a;border-bottom:2px solid #1a56db;padding-bottom:8px;">
        Job Search Agent — {len(jobs)} jobs found
    </h2>
    <p style="color:#555;">Report for {date.today()}</p>
    <table style="width:100%;border-collapse:collapse;">
        <tr style="background:#f8f9fa;border-bottom:2px solid #dee2e6;">
            <th style="padding:8px;text-align:left;">Job</th>
            <th style="padding:8px;text-align:left;width:80px;">Source</th>
        </tr>
        {rows}
    </table>
    <p style="color:#888;font-size:12px;margin-top:20px;">
        Sent by <a href="https://github.com/karimfan/job_search_agent">Job Search Agent</a>
    </p>
</body>
</html>"""


def _build_text(jobs: list[Job]) -> str:
    lines = [
        f"Job Search Agent — {len(jobs)} jobs found",
        f"Report for {date.today()}",
        "=" * 50,
        "",
    ]

    for i, job in enumerate(jobs, 1):
        remote_tag = f" [{job.remote}]" if job.remote else ""
        location = job.location or "Not specified"
        lines.append(f"{i}. {job.title}")
        lines.append(f"   Company:  {job.company}")
        lines.append(f"   Location: {location}{remote_tag}")
        if job.posted_date:
            lines.append(f"   Posted:   {job.posted_date}")
        lines.append(f"   Source:   {job.source}")
        lines.append(f"   URL:      {job.url}")
        lines.append("")

    return "\n".join(lines)
