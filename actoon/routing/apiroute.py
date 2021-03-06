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

import actoon.views.cutview
import actoon.views.effectview
import actoon.views.encodeview
import actoon.views.mediaview
import actoon.views.projectview
import actoon.views.registerview
import actoon.views.taskview

project_list = actoon.views.projectview.ProjectView.as_view({
    'get': 'list',
    'put': 'create'
})

project_view = actoon.views.projectview.ProjectView.as_view({
    'get': 'retrieve',  # retrieve projects
    'patch': 'update',  # update project description
    'delete': 'destroy'  # delete project
})

task_list = actoon.views.taskview.TaskView.as_view({
    'get': 'list',  # list of tasks
    'put': 'create',  # create a new task with a specified action
})

task_view = actoon.views.taskview.TaskView.as_view({
    'delete': 'destroy'  # delete the task
    # depends on history-based management, update the task won't be supported
})

effect_list = actoon.views.effectview.EffectView.as_view({
    'get': 'list'  # get available effects
})

effect_view = actoon.views.effectview.EffectView.as_view({
    'get': 'retrieve'
})

media_list = actoon.views.mediaview.MediaView.as_view({
    'get': 'list',
    'post': 'create'
})

media_view = actoon.views.mediaview.MediaView.as_view({
    'delete': 'destroy'
})

register_view = actoon.views.registerview.RegisterView.as_view({
    'post': 'create',
    'patch': 'update'
})

cut_list = actoon.views.cutview.CutView.as_view({
    'get': 'list',
    'delete': 'destroy'
})

cut_view = actoon.views.cutview.CutView.as_view({
    'patch': 'update'
})

encode_view = actoon.views.encodeview.EncodeView.as_view({
    'get': 'retrieve'
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
    path('cut/<str:pk>/<str:cpk>/', cut_view, name='cut_view'),

    path('preview/<str:pk>/<int:tpk>/', encode_view, name='encode_preview'),
    path('encode/<str:pk>/', encode_view, name='full_encode'),
])
