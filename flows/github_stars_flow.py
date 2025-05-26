from prefect import flow, task
import httpx
from typing import List


@task(log_prints=True, retries=2, retry_delay_seconds=5)
def get_stars(repo: str) -> int:
    """Get the number of stars for a GitHub repository."""
    url = f"https://api.github.com/repos/{repo}"
    try:
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        count = response.json()["stargazers_count"]
        print(f"✨ {repo} has {count} stars!")
        return count
    except Exception as e:
        print(f"❌ Error fetching stars for {repo}: {e}")
        raise


@task(log_prints=True)
def calculate_total_stars(star_counts: List[int]) -> int:
    """Calculate the total number of stars across all repositories."""
    total = sum(star_counts)
    print(f"🌟 Total stars across all repositories: {total}")
    return total


@flow(name="GitHub Stars Tracker", log_prints=True)
def github_stars_flow(repos: List[str] = None):
    """
    Track GitHub stars for multiple repositories.
    
    Args:
        repos: List of repository names in format 'owner/repo'
    """
    if repos is None:
        repos = [
            "PrefectHQ/prefect",
            "apache/airflow",
            "dagster-io/dagster"
        ]
    
    print(f"🚀 Starting GitHub stars tracking for {len(repos)} repositories...")
    
    # Get stars for each repository
    star_counts = []
    for repo in repos:
        count = get_stars(repo)
        star_counts.append(count)
    
    # Calculate total
    total_stars = calculate_total_stars(star_counts)
    
    print(f"✅ GitHub stars tracking completed! Total: {total_stars} stars")
    return {"repositories": repos, "star_counts": star_counts, "total": total_stars}


if __name__ == "__main__":
    # Run the flow locally for testing
    result = github_stars_flow()
    print(f"Flow result: {result}") 