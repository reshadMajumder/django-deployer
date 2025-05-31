# deployer/tasks.py
from .models import DjangoProject,ReactProject
from .utils import clone_repo, ensure_dockerfile, find_free_port, generate_nginx_config, generate_react_nginx_config, ensure_react_dockerfile, ssh_and_run
from celery import shared_task
import os, subprocess

@shared_task
def deploy_project(project_id):
    project = DjangoProject.objects.get(id=project_id)
    project.status = "deploying"
    project.save()

    if project.deploy_mode == "local":
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
    else:
        # Remote deployment
        try:
            port = find_free_port()
            image_tag = f"{project.name.lower()}_{project.id}_image"
            container_name = f"{project.name.lower()}_{project.id}_container"
            remote_dir = f"/home/{project.remote_user}/{project.name}"
            pem_path = project.pem_file.path
            dockerfile_content = '''FROM python:3.10-slim\nENV PYTHONDONTWRITEBYTECODE 1\nENV PYTHONUNBUFFERED 1\nWORKDIR /app\nCOPY requirements.txt /app/\nRUN pip install --upgrade pip && pip install -r requirements.txt\nCOPY . /app/\nCMD [\"/bin/sh\", \"-c\", \"python manage.py makemigrations && python manage.py migrate && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:8000 core.wsgi:application\"]\n'''
            setup_cmds = [
                "sudo apt-get update -y && sudo apt-get upgrade -y",
                "sudo apt-get install -y docker.io git",
                f"rm -rf {remote_dir}",
                f"git clone {project.repo_url} {remote_dir}",
                # Ensure requirements.txt and gunicorn
                f"touch {remote_dir}/requirements.txt",
                f"grep -qxF 'gunicorn' {remote_dir}/requirements.txt || echo 'gunicorn' >> {remote_dir}/requirements.txt",
                # Ensure Dockerfile exists
                f"echo '{dockerfile_content}' > {remote_dir}/Dockerfile",
                f"cd {remote_dir} && sudo docker build -t {image_tag} .",
                f"sudo docker rm -f {container_name} || true",
                f"sudo docker run -d --name {container_name} -p {port}:8000 {image_tag}",
            ]
            nginx_config = f'''
server {{
    listen 80;
    server_name _;

    location / {{
        proxy_pass http://127.0.0.1:{port};
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
'''
            nginx_conf_path = f'/etc/nginx/sites-available/{project.name}'
            setup_cmds += [
                "sudo apt-get install -y nginx",
                f"echo '{nginx_config}' | sudo tee {nginx_conf_path}",
                f"sudo ln -sf {nginx_conf_path} /etc/nginx/sites-enabled/",
                "sudo rm -f /etc/nginx/sites-enabled/default",
                "sudo systemctl restart nginx"
            ]
            ssh_and_run(
                project.remote_ip,
                project.remote_user,
                pem_path,
                setup_cmds,
                port=project.remote_port or 22
            )
            # Optionally, add remote nginx config setup here
            project.container_id = container_name
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
    
