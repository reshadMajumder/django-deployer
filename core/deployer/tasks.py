# deployer/tasks.py
from .models import DjangoProject
from .utils import clone_repo, ensure_dockerfile, find_free_port, generate_nginx_config
from celery import shared_task
import os, subprocess

@shared_task
def deploy_project(project_id):
    project = DjangoProject.objects.get(id=project_id)
    project.status = "deploying"
    project.save()

    base_dir = f"/app/deployments/{project.name}"
    try:
        clone_repo(project.repo_url, base_dir)
        ensure_dockerfile(base_dir)
        port = find_free_port()
        image_tag = f"{project.name.lower()}_image"
        container_name = f"{project.name.lower()}_container"

        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=base_dir, check=True)
        run = subprocess.run(["docker", "run", "-d", "--name", container_name, "-p", f"{port}:8000", image_tag], capture_output=True, check=True)
        container_id = run.stdout.decode().strip()

        generate_nginx_config(project.name, port)

        project.container_id = container_id
        project.status = "deployed"
        project.port = port
        project.save()
    except Exception as e:
        project.status = "failed"
        project.save()
        raise e



def deploy_project(project_id):
    project = DjangoProject.objects.get(id=project_id)
    base_dir = f"/app/deployments/{project.name}"
    project.status = "deploying"
    project.save()

    try:
        clone_repo(project.repo_url, base_dir)
        ensure_dockerfile(base_dir)  # Adds Dockerfile if not present

        image_tag = f"{project.name.lower()}_image"
        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=base_dir, check=True)

        container_name = f"{project.name.lower()}_container"
        run = subprocess.run(["docker", "run", "-d", "--name", container_name, "-p", "0:8000", image_tag], capture_output=True, check=True)
        container_id = run.stdout.decode().strip()

        project.status = "deployed"
        project.container_id = container_id
        project.save()
    except Exception as e:
        project.status = "failed"
        project.save()
        raise e