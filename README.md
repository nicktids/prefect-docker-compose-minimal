# Prefect docker example 

# There are 2 options for running docker the short term effemeral or long term docker 

This small repo shows how to add both to a prefect server. 

- First a short term image (effemeral) :  prefect-flow
- Second a longer term image : prefect-longrunning

Both running on a server and and the shorter term image run through a worker

## To run this 

``` 
docker compose up -d --build
```

### Optional to turn on "Auto Remove (Optional)" within the Docker Worker

Still looking for the option to get this to be done in the docker compose.

![Alt text](images/AutoRemoveContainers.png?raw=true "Title")


## Short Term Image

Build a docker file from within the docker compose image  see   prefect-flows:

``` Dockerfile
prefect-flows:
    build:
      context: .
      dockerfile: Dockerfile
    image: prefect-flows:latest
    command: "python flows.py"
    environment:
      PREFECT_API_URL: http://prefect-server:4200/api
    networks:
      - prefect-network 
```

Then export the correct prefect url if hosting elsewhere 


to add docker running then add the python flow to the  
This builds the docker with all the requirements needed to successfully run the deployment

then create a script with full code to then run on the server in a deploy, requirements to get the env and the network correct

``` python 
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
        image=DockerImage"prefect-flows:latest",
        push=False,
        cron="* * * * *",  # Run every 4 hours instead of every minute
        build=False,
        job_variables={
            "image_pull_policy": "Never",
            "networks": ["prefect-docker-compose-minimal-prefect-network"],
            "env": {
                "PREFECT_API_URL": "http://prefect-server:4200/api"
            }
        },
        tags=["production", "trading"],  # Add deployment tags
    )
```

then run the below to get a deployment to the docker worker that you set in the dockerfile, this worker runs the docker image from python flow and the flow registers to the work_pool_name

within a venv with prefect
``` python 
export PREFECT_API_URL=http://localhost:4200/api
cd flows
python flows.py 
```

## Long Running Image


``` Dockerfile
  prefect-longrunning:
    build:
      context: .
      dockerfile: Dockerfile.longlived
    image: prefect-longrunning:latest
    command: "python serve_retrieve_github_stars.py"
    environment:
      PREFECT_API_URL: http://prefect-server:4200/api
    networks:
      - prefect-network
    depends_on:
      prefect-server:
        condition: service_healthy
```

This creates a long running dockerfile with a serve component, then in the UI you can add the schedule.
