# deployer/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DjangoProject
import subprocess
import os
from .serializers import DjangoProjectSerializer
from .tasks import deploy_project


class DeployProjectView(APIView):
    def post(self, request):
        repo_url = request.data.get("repo_url")
        if not repo_url:
            return Response({"error": "repo_url is required"}, status=400)

        name = repo_url.strip('/').split('/')[-1].replace('.git', '')
        project = DjangoProject.objects.create(name=name, repo_url=repo_url)
        deploy_project.delay(project.id)
        return Response(DjangoProjectSerializer(project).data)

class ProjectControlView(APIView):
    def post(self, request, pk, action):
        try:
            project = DjangoProject.objects.get(pk=pk)
            if action == "stop":
                subprocess.run(["docker", "stop", project.container_id], check=True)
                project.status = "stopped"
            elif action == "start":
                subprocess.run(["docker", "start", project.container_id], check=True)
                project.status = "deployed"
            elif action == "delete":
                subprocess.run(["docker", "rm", "-f", project.container_id], check=True)
                subprocess.run(["rm", "-rf", f"/app/deployments/{project.name}"])
                os.remove(f"/etc/nginx/conf.d/{project.name}.conf")
                subprocess.run(["nginx", "-s", "reload"])
                project.delete()
                return Response({"deleted": True})
            project.save()
            return Response({"status": project.status})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
