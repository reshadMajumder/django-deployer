# auto_deployer/urls.py
from django.urls import path
from deployer.views import DeployProjectView, ProjectControlView, DeployedProjectsView, DeployReactProjectView, DeployedReactProjectsView, RedeployProjectView, InstanceListCreateView, InstanceTestConnectionView

urlpatterns = [
    path("deploy/", DeployProjectView.as_view()),
    path("project/<int:pk>/<str:action>/", ProjectControlView.as_view()),
    path("projects/", DeployedProjectsView.as_view()),

    path("deploy-react/", DeployReactProjectView.as_view()),
    path("react-projects/", DeployedReactProjectsView.as_view()),
    path("redeploy/<int:pk>/", RedeployProjectView.as_view()),
    path("instances/", InstanceListCreateView.as_view()),
    path("instances/<int:pk>/test/", InstanceTestConnectionView.as_view()),
]
