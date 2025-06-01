from django.db import models



class DjangoProject(models.Model):
    name = models.CharField(max_length=100)
    repo_url = models.URLField()
    status = models.CharField(max_length=50, default='pending')  # pending, deploying, deployed, failed
    container_id = models.CharField(max_length=100, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    project_root = models.CharField(max_length=200, default="./")



# models.py
class ReactProject(models.Model):
    name = models.CharField(max_length=100)
    repo_url = models.URLField()
    port = models.IntegerField(null=True, blank=True)
    container_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, default="pending")  # pending, deploying, deployed, failed
    created_at = models.DateTimeField(auto_now_add=True)
