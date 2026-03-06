import json
import os
import random
import smtplib
from datetime import date
from email.message import EmailMessage
from pathlib import Path

from job_search_agent.config import Config
from job_search_agent.models import Job

KATE_EMAIL = "kateoreed2@gmail.com"
KATE_NOTES_HISTORY = ".kate_notes_used.json"

KATE_NOTES = [
    "Your smile could outshine\nevery job listing here —\nlucky me, I searched.",
    "Roses are red, resumes are long,\nbut none of these jobs make my heart sing like your song.",
    "I searched a thousand boards today, but my favorite find is still you.",
    "They say the best things aren't found on job boards — and you're proof.",
    "If charm were a keyword, you'd be the only search result.",
    "These jobs are great, but they'll never be as captivating as your laugh.",
    "Morning light arrives,\nI think of you, then press send —\nhope this makes you smile.",
    "Somewhere between 'apply now' and 'submit,' I just wanted to say — you're wonderful.",
    "Every search I run reminds me: the best discovery I ever made was you.",
    "The algorithm found {n} jobs today, but zero that compare to finding you.",
]


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

    try:
        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(username, password)

            for recipient in config.email.recipients:
                note = _pick_kate_note(recipient, len(jobs))
                html_body = _build_html(jobs, note)
                text_body = _build_text(jobs, note)

                msg = EmailMessage()
                msg["Subject"] = subject
                msg["From"] = from_addr
                msg["To"] = recipient
                msg.set_content(text_body)
                msg.add_alternative(html_body, subtype="html")
                server.send_message(msg)

        return True
    except Exception as e:
        print(f"  Warning: Failed to send email: {e}")
        return False


def _pick_kate_note(recipient: str, job_count: int) -> str | None:
    if recipient.lower().strip() != KATE_EMAIL:
        return None

    # Load history of used note indices
    history_path = Path(KATE_NOTES_HISTORY)
    used: list[int] = []
    try:
        if history_path.exists():
            used = json.loads(history_path.read_text())
    except (json.JSONDecodeError, OSError):
        used = []

    # Find unused notes; reset if all have been used
    all_indices = set(range(len(KATE_NOTES)))
    available = list(all_indices - set(used))
    if not available:
        used = []
        available = list(all_indices)

    idx = random.choice(available)
    used.append(idx)

    # Save updated history
    try:
        history_path.write_text(json.dumps(used))
    except OSError:
        pass

    return KATE_NOTES[idx].format(n=job_count)


def _build_html(jobs: list[Job], note: str | None = None) -> str:
    note_html = ""
    if note:
        note_escaped = note.replace("\n", "<br>")
        note_html = f"""
    <div style="background:linear-gradient(135deg,#fdf2f8,#fce7f3);border-left:4px solid #ec4899;
                padding:16px 20px;margin-bottom:20px;border-radius:0 8px 8px 0;font-style:italic;color:#831843;">
        {note_escaped}
        <div style="text-align:right;margin-top:8px;font-size:13px;color:#9d174d;">— K</div>
    </div>"""

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
    {note_html}
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


def _build_text(jobs: list[Job], note: str | None = None) -> str:
    lines = []

    if note:
        lines.append(note)
        lines.append(f"  — K")
        lines.append("")
        lines.append("-" * 50)
        lines.append("")

    lines.extend([
        f"Job Search Agent — {len(jobs)} jobs found",
        f"Report for {date.today()}",
        "=" * 50,
        "",
    ])

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
