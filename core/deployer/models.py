from django.db import models

# Create your models here.


# deployer/models.py
from django.db import models

class DjangoProject(models.Model):
    name = models.CharField(max_length=100)
    repo_url = models.URLField()
    status = models.CharField(max_length=50, default='pending')  # pending, deploying, deployed, failed
    container_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
