import asyncio
import argparse
from prefect.client.orchestration import get_client
from prefect.client.schemas.actions import DeploymentUpdate
from prefect.client.schemas.responses import DeploymentResponse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("version", required=True)
    return parser.parse_args()


async def pause_deployment(deployment: DeploymentResponse):
    client = get_client()
    await client.update_deployment(
        deployment_id=deployment.id,
        deployment=DeploymentUpdate(
            paused=True,
            version=deployment.version,
            description=deployment.description,
            work_queue_name=deployment.work_queue_name,
            path=deployment.path,
            entrypoint=deployment.entrypoint,
            storage_document_id=deployment.storage_document_id,
            infrastructure_document_id=deployment.infrastructure_document_id,
        ),
    )
    print(f"Paused deployment with ID: {deployment.id}")


async def deduplicate_staging_deployments(version_id: str):
    client = get_client()

    relevant_staging_deployments = [
        deployment
        for deployment in await client.read_deployments()
        if deployment.name.endswith("stg") and deployment.version == version_id
    ]

    for deployment in relevant_staging_deployments:
        await pause_deployment(deployment)


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(deduplicate_staging_deployments(args.version))
