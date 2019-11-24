from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, logout
from django.core.files.storage import default_storage
from django.shortcuts import render_to_response, render, redirect, HttpResponse
from django.template import RequestContext
from rest_framework.response import Response

from actoon.forms.login import LoginForm
import json

from actoon.forms.register import RegisterForm


def render_wrapper(request, template, additional_context=None):
    context = {
        'app_title': settings.APP_NAME,
        'user_name': request.user
    }

    if additional_context is not None:
        context += additional_context

    return render(request, template, context)
    # return render_to_response(template, context)


def index(request):
    return render_wrapper(request, './index.html')


def register(request):
    if request.method is 'GET':
        return render_wrapper(request, './register.html')
    else:
        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')
        else:
            error_message = {'error_message': 'register form is not valid'}
            return render_wrapper(request, './register.html', additional_context=error_message)


# @login_required(login_url='/login/')
def editor(request):
    return render_wrapper(request, './editor.html')


@login_required(login_url='/login/')
def profile(request):
    return render_wrapper(request,  './profile.html')


# @login_required()
def media(request):
    file = request.path_info.split('/')[-1]
    return HttpResponse(default_storage.open(file).read(), content_type='application/binary')
