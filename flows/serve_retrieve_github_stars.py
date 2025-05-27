import httpx
from prefect import flow, task
import json


@task(log_prints=True)
def get_stars_for_repo(repo: str) -> int:
    response = httpx.Client().get(f"https://api.github.com/repos/{repo}")
    print(json.dumps(response.json(), indent=4))
    stargazer_count = response.json()["stargazers_count"]
    print(f"{repo} has {stargazer_count} stars")
    return stargazer_count


@flow
def retrieve_github_stars(repos: list[str]) -> list[int]:
    return get_stars_for_repo.map(repos).wait()


if __name__ == "__main__":
    retrieve_github_stars.serve(
        name="retrieve-github-stars",
        cron="*/5 * * * *",
        parameters={
            "repos": ["python/cpython", "prefectHQ/prefect"],
        }
    )