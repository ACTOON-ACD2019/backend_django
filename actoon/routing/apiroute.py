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
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from actoon.views import apiviews

project_list = apiviews.ProjectView.as_view({
    'get': 'list',
    'put': 'create'
})

project_view = apiviews.ProjectView.as_view({
    'get': 'retrieve',  # retrieve projects
    'patch': 'update',  # update project description
    'delete': 'destroy'  # delete project
})

task_list = apiviews.TaskView.as_view({
    'get': 'list',  # list of tasks
    'put': 'create',  # create a new task with a specified action
})

task_view = apiviews.TaskView.as_view({
    'delete': 'destroy'  # delete the task
    # depends on history-based management, update the task won't be supported
})

effect_list = apiviews.EffectView.as_view({
    'get': 'list'  # get available effects
})

effect_view = apiviews.EffectView.as_view({
    'get': 'retrieve'
})

media_list = apiviews.MediaView.as_view({
    'get': 'list',
    'post': 'create'
})

media_view = apiviews.MediaView.as_view({
    'delete': 'destroy'
})

register_view = apiviews.RegisterView.as_view({
    'post': 'create',
    'patch': 'update'
})

cut_list = apiviews.CutView.as_view({
    'get': 'list',
    'delete': 'destroy'
})

cut_view = apiviews.CutView.as_view({
    'patch': 'update'
})

urlpatterns = format_suffix_patterns([
    path('auth/', obtain_auth_token, name='auth'),
    path('auth/register/', register_view, name='register'),

    path('project/', project_list, name='project_list'),
    path('project/<str:pk>/', project_view, name='project_desc'),

    path('task/<str:pk>/', task_list, name='task_list'),
    path('task/<str:pk>/<int:tpk>/', task_view, name='task_desc'),

    path('effect/', effect_list, name='effect_list'),
    path('effect/<int:pk>/', effect_view, name='effect_desc'),

    path('media/<str:pk>/', media_list, name='media_list'),
    path('media/<str:pk>/<int:mpk>/', media_view, name='media_view'),

    path('cut/<str:pk>/', cut_list, name='cut_list'),
    path('cut/<str:pk>/<str:cpk>/', cut_view, name='cut_view')
])
