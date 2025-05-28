# deployer/tasks.py
from .models import DjangoProject,ReactProject
from .utils import clone_repo, ensure_dockerfile, find_free_port, generate_nginx_config, generate_react_nginx_config, ensure_react_dockerfile
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
        image_tag = f"{project.name.lower()}_{project.id}_image"
        container_name = f"{project.name.lower()}_{project.id}_container"

        try:
            build_result = subprocess.run([
                "docker", "build", "-t", image_tag, "."
            ], cwd=base_dir, check=True, capture_output=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker build failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

        try:
            run = subprocess.run([
                "docker", "run", "-d", "--name", container_name, "-p", f"{port}:8000", image_tag
            ], capture_output=True, check=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker run failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
        container_id = run.stdout.strip()

        generate_nginx_config(project.name, port)

        project.container_id = container_id
        project.status = "deployed"
        project.port = port
        project.save()
    except Exception as e:
        project.status = "failed"
        project.save()
        raise e
    



# @shared_task
# def deploy_react_project(project_id):
#     from .models import ReactProject
#     project = ReactProject.objects.get(id=project_id)
#     project.status = "deploying"
#     project.save()

#     base_dir = f"/app/deployments/react_{project.name}"
#     try:
#         clone_repo(project.repo_url, base_dir)
#         ensure_react_dockerfile(base_dir)
#         port = find_free_port()
#         image_tag = f"react_{project.name.lower()}_{project.id}_image"
#         container_name = f"react_{project.name.lower()}_{project.id}_container"

#         try:
#             subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=base_dir, check=True)
#         except subprocess.CalledProcessError as e:
#             raise RuntimeError(f"Docker build failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

#         try:
#             run = subprocess.run([
#                 "docker", "run", "-d", "--name", container_name, "-p", f"{port}:80", image_tag
#             ], capture_output=True, check=True, text=True)
#         except subprocess.CalledProcessError as e:
#             raise RuntimeError(f"Docker run failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

#         container_id = run.stdout.strip()
#         generate_react_nginx_config(project.name, port)

#         project.container_id = container_id
#         project.port = port
#         project.status = "deployed"
#         project.save()
#     except Exception as e:
#         project.status = "failed"
#         project.save()
#         raise e


@shared_task
def deploy_react_project(project_id):
    project = ReactProject.objects.get(id=project_id)
    project.status = "deploying"
    project.save()

    base_dir = f"/app/deployments/react_{project.name}"
    try:
        clone_repo(project.repo_url, base_dir)
        ensure_react_dockerfile(base_dir)
        port = find_free_port()
        image_tag = f"{project.name.lower()}_{project.id}_image"
        container_name = f"{project.name.lower()}_{project.id}_container"

        try:
            build_result = subprocess.run([
                "docker", "build", "-t", image_tag, "."
            ], cwd=base_dir, check=True, capture_output=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker build failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")

        try:
            run = subprocess.run([
                "docker", "run", "-d", "--name", container_name, "-p", f"{port}:8000", image_tag
            ], capture_output=True, check=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker run failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
        container_id = run.stdout.strip()

        generate_react_nginx_config(project.name, port)

        project.container_id = container_id
        project.status = "deployed"
        project.port = port
        project.save()
    except Exception as e:
        project.status = "failed"
        project.save()
        raise e
    
