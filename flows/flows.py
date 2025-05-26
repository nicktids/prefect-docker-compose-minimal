from prefect import flow, tags


@flow(
    log_prints=True,
    name="buy-securities",
    description="Flow to handle buying of securities",
    retries=0,  # Prevent automatic retries
    version="1.0.0"
)
def buy():
    print("Buying securities")

if __name__ == "__main__":
    buy.deploy(
        name="buy-securities-deployment",
        work_pool_name="docker-pool",
        image="prefect-flows:latest",
        push=False,
        cron="* * * * *",  # Run every 4 hours instead of every minute
        build=False,
        job_variables={
            "image_pull_policy": "Never",
            "networks": ["prefect-docker-compose-minimal_prefect-network"],
            "env": {
                "PREFECT_API_URL": "http://prefect-server:4200/api"
            }
        },
        tags=["production", "trading"],  # Add deployment tags
    )