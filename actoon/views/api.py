import os
import asyncio
from actoon import models as actoon_model
from actoon import serializer as actoon_serializer
from django.contrib.auth import get_user_model
from django.core.files import File
from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from rest_framework.utils import json
from actoon.apps import RpcClient


def get_media(project=None):
    queryset = actoon_model.Media.objects\
        .filter(project=project)
    instance = get_list_or_404(queryset)

    if len(instance) > 0:
        return instance

    return None


def get_effect(name):
    queryset_effect = actoon_model.Effect.objects\
        .filter(name=name)
    effect_instance = get_list_or_404(queryset_effect)

    if len(effect_instance) > 0:
        return effect_instance[0]

    return None


def get_project(user, project_name):
    queryset_project = actoon_model.Project.objects\
        .filter(user=user)\
        .filter(name=project_name)
    project_instance = get_list_or_404(queryset_project)

    if len(project_instance) > 0:
        return project_instance[0]

    return None


class ProjectView(viewsets.ModelViewSet):
    serializer_class = actoon_serializer.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, name=None):
        user = self.request.user

        if name is None:
            return actoon_model.Project.objects.filter(user=user)
        else:
            return actoon_model.Project.objects\
                .filter(user=user).filter(name=name)

    def list(self, request):
        queryset = self.get_queryset()
        instance = get_list_or_404(queryset)
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        instance = get_object_or_404(queryset, name=pk)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid() is True:
            queryset = self.get_queryset().filter(name=serializer.validated_data['name'])

            if queryset.count() is 0:
                self.perform_create(serializer, user=self.request.user)
                return Response(status=status.HTTP_201_CREATED)

            return Response({'errors': 'given project name has been already taken'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset(pk)
        instance = get_object_or_404(queryset)
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            instance.name = serializer.validated_data['name']

            if instance.description != serializer.validate_data['description']:
                instance.description = serializer.validate_data['description']

            instance.save()

            return Response(status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset(name=pk)

        if queryset.count() > 0:
            self.perform_destroy(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'no such project'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, user):
        return serializer.save(user=self.request.user)


class TaskView(viewsets.ModelViewSet):
    serializer_class = actoon_serializer.TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, task_index=None):
        if project_name is not None:
            project_instance = get_project(self.request.user, project_name)

            if task_index is not None:
                queryset_task_object = actoon_model.Task.objects.filter(project=project_instance) \
                    .order_by('created_at')

                if len(queryset_task_object) > task_index:
                    return queryset_task_object[task_index - 1]
            else:
                if project_instance is not None:
                    return actoon_model.Task.objects.filter(project=project_instance).order_by('created_at')

        return None

    def list(self, request, pk=None):
        queryset = self.get_queryset(project_name=pk)

        if queryset is not None:
            instance = get_list_or_404(queryset)  # 404 if there are no tasks in project
            serializer = actoon_serializer.TaskListSerializer(instance, many=True)
            # serializer.validated_data.pop('project')  # remove project_id from task results
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)  # no such project

    def create(self, request, pk=None):
        if request.data.__contains__('effect_name'):  # validate on server-side
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid() is True:
                effect = get_effect(serializer.validated_data['effect_name'])  # sets the effect object
                project = get_project(self.request.user, pk)  # get projects to insert task

                if project is not None:
                    self.perform_create(serializer, effect, project)
                    return Response(status=status.HTTP_201_CREATED)

        return Response(status=status.HTTP_400_BAD_REQUEST)  # no effect name

    def destroy(self, request, pk=None, tpk=None):
        instance = self.get_queryset(project_name=pk, task_index=tpk)

        if instance is not None:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, effect, project):
        serializer.save(effect=effect, project=project)


class EffectView(viewsets.ModelViewSet):
    queryset = actoon_model.Effect.objects.all()
    serializer_class = actoon_serializer.EffectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, pk=None):
        if pk is not None:
            queryset = actoon_model.Effect.objects.all(pk=pk)
        else:
            queryset = actoon_model.Effect.objects.all()

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        instance = get_list_or_404(queryset)
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        instance = get_object_or_404(queryset)
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class MediaView(viewsets.ModelViewSet):
    serializer_class = actoon_serializer.MediaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, media_id=None):
        if project_name is not None:
            project_instance = get_project(self.request.user, project_name)

            if media_id is not None:
                queryset_media_object = actoon_model.Media.objects.filter(pk=media_id)

                if len(queryset_media_object) > 0:
                    return queryset_media_object[0]
            else:
                if project_instance is not None:
                    return actoon_model.Media.objects.filter(project=project_instance)

        return None

    def list(self, request, pk=None):
        queryset = self.get_queryset(project_name=pk)

        if queryset is not None:
            instance = get_list_or_404(queryset)  # 404 if there are no media in project
            serializer = self.get_serializer(instance, many=True)
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)  # no such project

    def create(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid() is True:
            project = get_project(self.request.user, project_name=pk)

            if project is not None:
                media = self.perform_create(serializer, project=project)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(RpcClient.request(loop, 'cut_slicing', media))
                loop.close()

                # save files into database
                for root, files in os.walk('./temp/'):
                    for file in files:
                        fit = True

                        file = File(open(os.path.join(root, file), 'rb'))
                        new_path = os.path.basename(file.name)
                        os.rename(file.name, new_path)

                        obj = actoon_model.Cut(
                            media=media,
                            file=File(open(new_path, 'rb'))
                        )

                        if root.__contains__('bubble'):
                            obj.type = 'BU'
                        elif root.__contains__('cut'):
                            obj.type = 'SC'
                        elif root.__contains__('text'):
                            obj.type = 'TX'
                        else:
                            fit = False
                            obj.type = 'UD'

                        if fit:
                            obj.sequence = int(file.name.split('.')[-2].split('_')[-1])
                            obj.save()

                # return object

                return Response(status=status.HTTP_201_CREATED)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        pass

    def pre_save(self, obj):
        obj.file = self.request.FILES.get('file')

    def perform_create(self, serializer, project=None):
        return serializer.save(project=project)


class RegisterView(viewsets.ModelViewSet):
    model = get_user_model()
    permission_classes = (permissions.AllowAny,)
    serializer_class = actoon_serializer.UserSerializer


class CutView(viewsets.ModelViewSet):
    serializer_class = actoon_serializer.CutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, media=None):
        if media is not None:
            queryset = actoon_model.Cut.objects.filter(media=media)
        else:
            queryset = actoon_model.Cut.objects.all()

        return queryset

    def list(self, request, pk=None):
        project = get_project(self.request.user, project_name=pk)

        if project is not None:
            media = get_media(project=project)
            data = []

            for media_s in media:
                cut_individual = actoon_model.Cut.objects.filter(media=media_s)
                instance = get_list_or_404(cut_individual)
                serializer = self.get_serializer(instance, many=True)
                _array = []
                _array += serializer.data
                data.append(_array)

            if len(data) > 0:
                return Response(json.dumps(data))
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)
