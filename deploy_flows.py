#!/usr/bin/env python3
"""
Deployment script for Prefect flows to Docker work pool.
This script will deploy both test flows to the docker-pool work pool using Prefect 3.0 syntax.
"""

import asyncio
from prefect.client.orchestration import get_client

# Import the flows
from flows.github_stars_flow import github_stars_flow
from flows.data_processing_flow import data_processing_flow


async def check_work_pool():
    """Check if the Docker work pool exists."""
    print("🔧 Checking Docker work pool...")
    
    async with get_client() as client:
        try:
            work_pool = await client.read_work_pool("docker-pool")
            print(f"✅ Work pool 'docker-pool' exists with ID: {work_pool.id}")
            return work_pool
        except Exception as e:
            print(f"❌ Work pool 'docker-pool' not found: {e}")
            print("💡 Create it first with: prefect work-pool create docker-pool --type docker")
            raise


async def deploy_github_stars_flow():
    """Deploy the GitHub Stars flow."""
    print("🚀 Deploying GitHub Stars flow...")
    
    deployment_id = await github_stars_flow.deploy(
        name="github-stars-deployment",
        work_pool_name="docker-pool",
        cron="0 */6 * * *",  # Every 6 hours
        parameters={
            "repos": [
                "PrefectHQ/prefect",
                "apache/airflow",
                "dagster-io/dagster",
                "spotify/luigi"
            ]
        },
        description="Monitor GitHub repository stars every 6 hours",
        tags=["github", "monitoring", "scheduled"],
        image="prefect-flows:latest",
        build=False,  # Don't build, use existing image
        push=False,  # Don't push to registry, use local image
        job_variables={
            "image_pull_policy": "IfNotPresent"  # Don't pull if image exists locally
        }
    )
    
    print(f"✅ GitHub Stars flow deployed with ID: {deployment_id}")
    return deployment_id


async def deploy_data_processing_flow():
    """Deploy the Data Processing flow."""
    print("🚀 Deploying Data Processing flow...")
    
    deployment_id = await data_processing_flow.deploy(
        name="data-processing-deployment",
        work_pool_name="docker-pool",
        cron="0 */4 * * *",  # Every 4 hours
        parameters={
            "user_count": 10
        },
        description="Process user data every 4 hours",
        tags=["data-processing", "api", "scheduled"],
        image="prefect-flows:latest",
        build=False,  # Don't build, use existing image
        push=False,  # Don't push to registry, use local image
        job_variables={
            "image_pull_policy": "IfNotPresent"  # Don't pull if image exists locally
        }
    )
    
    print(f"✅ Data Processing flow deployed with ID: {deployment_id}")
    return deployment_id


async def main():
    """Main deployment function."""
    print("🎯 Starting deployment of Prefect flows...")
    
    try:
        # Test connection to Prefect API
        async with get_client() as client:
            server_info = await client.api_healthcheck()
            print(f"✅ Connected to Prefect API: {server_info}")
        
        # Check work pool exists
        await check_work_pool()
        
        # Deploy both flows
        github_deployment_id = await deploy_github_stars_flow()
        data_deployment_id = await deploy_data_processing_flow()
        
        print("\n🎉 Deployment completed successfully!")
        print(f"📊 GitHub Stars Deployment ID: {github_deployment_id}")
        print(f"📊 Data Processing Deployment ID: {data_deployment_id}")
        print("\n📋 Next steps:")
        print("1. Build flow image: docker build -t prefect-flows:latest .")
        print("2. Start a worker: docker compose exec prefect-worker prefect worker start --pool docker-pool")
        print("3. View deployments: docker compose exec prefect-server prefect deployment ls")
        print("4. Trigger a run: docker compose exec prefect-server prefect deployment run 'github-stars-flow/github-stars-deployment'")
        print("5. Access UI: http://localhost:4200")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main()) 