"""actoon_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from actoon.views import api
from rest_framework.authtoken.views import obtain_auth_token

project_list = api.ProjectView.as_view({
    'get': 'list',
    'put': 'create'
})

project_view = api.ProjectView.as_view({
    'get': 'retrieve',  # retrieve projects
    'patch': 'update',  # update project description
    'delete': 'destroy'  # delete project
})

urlpatterns = format_suffix_patterns([
    path('auth/', obtain_auth_token, name='auth'),

    path('project/', project_list, name='project_list'),
    path('project/<int:pk>/', project_view, name='project_desc'),
])
