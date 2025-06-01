from django.db import models



class Instance(models.Model):
    name = models.CharField(max_length=100)
    remote_ip = models.CharField(max_length=100)
    remote_user = models.CharField(max_length=100, default='ubuntu')
    remote_port = models.IntegerField(default=22)
    pem_file = models.FileField(upload_to="pem_keys/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)





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



