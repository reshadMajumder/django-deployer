# auto_deployer/urls.py
from django.urls import path
from deployer.views import DeployProjectView, ProjectControlView, DeployedProjectsView, DeployReactProjectView

urlpatterns = [
    path("deploy/", DeployProjectView.as_view()),
    path("project/<int:pk>/<str:action>/", ProjectControlView.as_view()),
    path("projects/", DeployedProjectsView.as_view()),

    path("deploy-react/", DeployReactProjectView.as_view()),
]
