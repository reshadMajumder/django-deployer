# deployer/utils.py
import socket, os
from pathlib import Path
import subprocess

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def generate_nginx_config(project_name, port):
    config = f"""
    location /{project_name}/ {{
        proxy_pass http://127.0.0.1:{port}/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
    """
    path = f"/etc/nginx/conf.d/{project_name}.conf"
    with open(path, 'w') as f:
        f.write(config)
    subprocess.run(["nginx", "-s", "reload"])

def clone_repo(repo_url, dest_dir):
    """Clone a git repo to the destination directory."""
    if os.path.exists(dest_dir):
        subprocess.run(["rm", "-rf", dest_dir], check=True)
    subprocess.run(["git", "clone", repo_url, dest_dir], check=True)

def ensure_dockerfile(project_dir):
    """Ensure a Dockerfile exists in the project root. If not, create a standard Django Dockerfile."""
    dockerfile_path = os.path.join(project_dir, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        with open(dockerfile_path, "w") as f:
            f.write('''
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app/
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "$(ls | grep wsgi | sed 's/\\.py$//').wsgi:application"]
''')
        # Try to generate requirements.txt if not present
        req_path = os.path.join(project_dir, "requirements.txt")
        if not os.path.exists(req_path):
            subprocess.run(["pipreqs", project_dir, "--force"], check=False)
