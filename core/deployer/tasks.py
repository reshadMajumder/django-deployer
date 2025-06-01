# deployer/tasks.py
from .models import DjangoProject,ReactProject
from .utils import clone_repo, ensure_dockerfile, find_free_port, generate_nginx_config, generate_react_nginx_config, ensure_react_dockerfile
from celery import shared_task
import os, subprocess

@shared_task
def deploy_project(project_id, env_content=None):
    project = DjangoProject.objects.get(id=project_id)
    project.status = "deploying"
    project.save()

    base_dir = f"/app/deployments/{project.name}"
    project_root = project.project_root or "./"
    project_dir = os.path.join(base_dir, project_root)
    try:
        clone_repo(project.repo_url, base_dir)
        if env_content:
            env_path = os.path.join(project_dir, ".env")
            with open(env_path, "w") as f:
                f.write(env_content)
        ensure_dockerfile(base_dir, project_root)
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
                "docker", "run", "-d", "--name", container_name, "-p", f"{port}:80", image_tag
            ], capture_output=True, check=True, text=True, encoding="utf-8")
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Docker run failed:\nSTDOUT:\n{e.stdout}\nSTDERR:\n{e.stderr}")
        container_id = run.stdout.strip()
        if not container_id:
            raise RuntimeError(f"Failed to get container ID. Docker output: {run.stdout} {run.stderr}")

        generate_react_nginx_config(project.name, port)

        project.container_id = container_id
        project.status = "deployed"
        project.port = port
        project.save()
    except Exception as e:
        project.status = "failed"
        project.save()
        raise e
    

@shared_task
def redeploy_project(project_id):
    project = DjangoProject.objects.get(id=project_id)
    base_dir = f"/app/deployments/{project.name}"
    project_root = project.project_root or "./"
    project_dir = os.path.join(base_dir, project_root)
    port = project.port or find_free_port()
    image_tag = f"{project.name.lower()}_{project.id}_image"
    container_name = f"{project.name.lower()}_{project.id}_container"
    try:
        # Stop and remove old container if exists
        if project.container_id:
            subprocess.run(["docker", "rm", "-f", project.container_id], check=False)
        # Pull latest code
        subprocess.run(["git", "pull"], cwd=base_dir, check=True)
        ensure_dockerfile(base_dir, project_root)
        # Rebuild image
        subprocess.run(["docker", "build", "-t", image_tag, "."], cwd=base_dir, check=True)
        # Run new container
        run = subprocess.run([
            "docker", "run", "-d", "--name", container_name, "-p", f"{port}:8000", image_tag
        ], capture_output=True, check=True, text=True, encoding="utf-8")
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
    
