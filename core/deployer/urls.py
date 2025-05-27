# auto_deployer/urls.py
from django.urls import path
from deployer.views import DeployProjectView, ProjectControlView

urlpatterns = [
    path("deploy/", DeployProjectView.as_view()),
    path("project/<int:pk>/<str:action>/", ProjectControlView.as_view()),
]
