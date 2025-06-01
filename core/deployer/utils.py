# deployer/utils.py
import socket, os
from pathlib import Path
import subprocess
import shutil
import platform
import stat

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]




def generate_nginx_config(project_name, port):
    if platform.system() == "Windows":
        # Skip nginx config on Windows
        return
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
    try:
        subprocess.run(["nginx", "-s", "reload"], check=True)
    except FileNotFoundError:
        raise RuntimeError("nginx not found. Please install nginx or skip nginx config on Windows.")





def generate_react_nginx_config(project_name, port):
    if platform.system() == "Windows":
        # Skip nginx config on Windows
        return
    config = f"""
    server {{
        listen 80;
        server_name _;

        location /{project_name}/ {{
            proxy_pass http://127.0.0.1:{port}/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            # Remove the /{project_name} prefix before proxying to React
            rewrite ^/{project_name}/(.*)$ /$1 break;
            try_files $uri $uri/ /index.html;
        }}
    }}
    """
    path = f"/etc/nginx/conf.d/{project_name}.conf"
    with open(path, 'w') as f:
        f.write(config)
    try:
        subprocess.run(["nginx", "-s", "reload"], check=True)
    except FileNotFoundError:
        raise RuntimeError("nginx not found. Please install nginx or skip nginx config on Windows.")





def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def clone_repo(repo_url, dest_dir):
    """Clone a git repo to the destination directory."""
    if os.path.exists(dest_dir):
        shutil.rmtree(dest_dir, onerror=on_rm_error)
    try:
        subprocess.run(["git", "clone", repo_url, dest_dir], check=True)
    except FileNotFoundError:
        raise RuntimeError("git not found. Please install git and ensure it's in your PATH.")

def ensure_dockerfile(project_dir, project_root):
    """Ensure a Dockerfile exists in the project root. If not, create a standard Django Dockerfile."""
    dockerfile_path = os.path.join(project_dir, "Dockerfile")
    req_path = os.path.join(project_dir, "requirements.txt")
    # Remove leading ./ or .\ from project_root for Docker paths
    docker_project_root = project_root.lstrip("./\\") or "."

    # Auto-detect Django project module (folder with wsgi.py and settings.py) inside project_root
    module_name = None
    project_root_path = os.path.join(project_dir, docker_project_root)
    if not os.path.isdir(project_root_path):
        raise FileNotFoundError(f"Project root directory '{docker_project_root}' does not exist in the repository. Available directories: {os.listdir(project_dir)}")
    for entry in os.listdir(project_root_path):
        entry_path = os.path.join(project_root_path, entry)
        if os.path.isdir(entry_path):
            if os.path.isfile(os.path.join(entry_path, "wsgi.py")) and os.path.isfile(os.path.join(entry_path, "settings.py")):
                module_name = entry
                break
    if not module_name:
        # fallback: check if project_root itself is the module
        if os.path.isfile(os.path.join(project_root_path, "wsgi.py")) and os.path.isfile(os.path.join(project_root_path, "settings.py")):
            module_name = os.path.basename(project_root_path)
        else:
            module_name = "core"  # fallback default

    if not os.path.exists(dockerfile_path):
        with open(dockerfile_path, "w") as f:
            f.write(f'''
FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app/{docker_project_root}
COPY requirements.txt /app/{docker_project_root}/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /app/
CMD ["gunicorn", "{module_name}.wsgi:application", "--bind", "0.0.0.0:8000"]
''')
    # Try to generate requirements.txt if not present
    if not os.path.exists(req_path):
        try:
            subprocess.run(["pipreqs", project_dir, "--force"], check=True)
        except FileNotFoundError:
            raise RuntimeError("pipreqs not found. Please install pipreqs and ensure it's in your PATH.")
    # Ensure gunicorn is present in requirements.txt
    with open(req_path, "r+") as f:
        lines = f.read().splitlines()
        if not any("gunicorn" in line for line in lines):
            f.write("\ngunicorn\n")









def ensure_react_dockerfile(project_dir):
    """Ensure a Dockerfile exists in the project root. If not, create a standard React Dockerfile for Vite."""
    dockerfile_path = os.path.join(project_dir, "Dockerfile")
    nginx_conf_path = os.path.join(project_dir, "nginx.conf")
    if not os.path.exists(dockerfile_path):
        with open(dockerfile_path, "w") as f:
            f.write('''
FROM node:18-alpine as build
WORKDIR /app
COPY . .
RUN npm install && npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
''')
    with open(nginx_conf_path, "w") as f:
        f.write('''
server {
    listen 80;
    server_name localhost;

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri /index.html;
    }
}
''')








def generate_react_nginx_config(project_name, port):
    if platform.system() == "Windows":
        return
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
    try:
        subprocess.run(["nginx", "-s", "reload"], check=True)
    except FileNotFoundError:
        raise RuntimeError("nginx not found. Please install nginx.")
