import argparse
import sys

from job_search_agent.config import load_config
from job_search_agent.emailer import send_digest
from job_search_agent.runner import print_jobs, run


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="job_search_agent",
        description="Scrape job boards and send email digests.",
    )
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="path to YAML config file (default: config.yaml)",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Copy config.yaml.example to config.yaml and edit it.")
        sys.exit(1)

    jobs = run(config)
    print_jobs(jobs)

    if config.email.enabled:
        print("Sending email digest...")
        if send_digest(jobs, config):
            print(f"  Email sent to {len(config.email.recipients)} recipient(s)")


if __name__ == "__main__":
    main()
