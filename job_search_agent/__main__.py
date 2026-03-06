import sys

from job_search_agent.config import load_config
from job_search_agent.runner import print_jobs, run


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    try:
        config = load_config(config_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Copy config.yaml.example to config.yaml and edit it.")
        sys.exit(1)

    jobs = run(config)
    print_jobs(jobs)


if __name__ == "__main__":
    main()
