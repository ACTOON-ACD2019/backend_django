import asyncio

from django.contrib.auth import get_user_model
from django.core.files import File
from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.utils import json

from actoon.models import Project, Task, Effect, Media, Cut
from actoon.serializer import ProjectSerializer, TaskSerializer, EffectSerializer, TaskListSerializer, MediaSerializer, \
    UserSerializer, CutSerializer
from django.shortcuts import get_list_or_404, get_object_or_404
from actoon.apps import RpcClient
import os

from actoon_backend import settings


class ProjectView(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(user=user)

    def list(self, request):
        queryset = self.get_queryset()
        instance = get_list_or_404(queryset)
        serializer = ProjectSerializer(instance, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        instance = get_object_or_404(queryset, name=pk)
        serializer = ProjectSerializer(instance)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid() is True:
            queryset = self.get_queryset().filter(name=serializer.validated_data['name'])

            if queryset.count() is 0:
                self.perform_create(serializer, user=self.request.user)
                return Response(status=status.HTTP_201_CREATED)

            return Response(status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset(name=pk)

        if queryset.count() > 0:
            self.perform_destroy(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, user):
        return serializer.save(user=self.request.user)


class TaskView(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, task_index=None):
        if project_name is not None:
            project_instance = self.get_project(project_name)

            if task_index is not None:
                queryset_task_object = Task.objects.filter(project=project_instance) \
                    .order_by('created_at')

                if len(queryset_task_object) > task_index:
                    return queryset_task_object[task_index - 1]
            else:
                if project_instance is not None:
                    return Task.objects.filter(project=project_instance).order_by('created_at')

        return None

    def get_project(self, name):
        user = self.request.user
        queryset_project = Project.objects.filter(user=user).filter(name=name)
        project_instance = get_list_or_404(queryset_project)

        if len(project_instance) > 0:
            return project_instance[0]

        return None

    def get_effect(self, name):
        queryset_effect = Effect.objects.filter(name=name)
        effect_instance = get_list_or_404(queryset_effect)

        if len(effect_instance) > 0:
            return effect_instance[0]

        return None

    def list(self, request, pk=None):
        queryset = self.get_queryset(project_name=pk)

        if queryset is not None:
            instance = get_list_or_404(queryset)  # 404 if there are no tasks in project
            serializer = TaskListSerializer(instance, many=True)
            # serializer.validated_data.pop('project')  # remove project_id from task results
            return Response(serializer.data)

        return Response(status=status.HTTP_400_BAD_REQUEST)  # no such project

    def create(self, request, pk=None):
        if request.data.__contains__('effect_name'):  # validate on server-side
            serializer = self.get_serializer(data=request.data)

            if serializer.is_valid() is True:
                effect = self.get_effect(serializer.validated_data['effect_name'])  # sets the effect object
                project = self.get_project(pk)  # get projects to insert task

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
    queryset = Effect.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, pk=None):
        if pk is not None:
            queryset = Effect.objects.all(pk=pk)
        else:
            queryset = Effect.objects.all()

        return queryset

    def list(self, request):
        queryset = self.get_queryset()
        instance = get_list_or_404(queryset)
        serializer = EffectSerializer(instance, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = self.get_queryset()
        instance = get_object_or_404(queryset)
        serializer = EffectSerializer(instance)
        return Response(serializer.data)


class MediaView(viewsets.ModelViewSet):
    serializer_class = MediaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, media_id=None):
        if project_name is not None:
            project_instance = self.get_project(project_name)

            if media_id is not None:
                queryset_media_object = Media.objects.filter(pk=media_id)

                if len(queryset_media_object) > 0:
                    return queryset_media_object[0]
            else:
                if project_instance is not None:
                    return Media.objects.filter(project=project_instance)

        return None

    def get_project(self, project_name):
        user = self.request.user
        queryset_project = Project.objects.filter(user=user).filter(name=project_name)
        project_instance = get_list_or_404(queryset_project)

        if len(project_instance) > 0:
            return project_instance[0]

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
            project = self.get_project(project_name=pk)

            if project is not None:
                media = self.perform_create(serializer, project=project)

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(RpcClient.request(loop, 'cut_slicing', media))
                loop.close()

                # save files into database
                for root, dirs, files in os.walk('./temp/'):
                    for file in files:
                        fit = True

                        file = File(open(os.path.join(root, file), 'rb'))
                        new_path = os.path.basename(file.name)
                        os.rename(file.name, new_path)

                        obj = Cut(
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
    serializer_class = UserSerializer


class CutView(viewsets.ModelViewSet):
    serializer_class = CutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, media=None):
        if media is not None:
            queryset = Cut.objects.filter(media=media)
        else:
            queryset = Cut.objects.all()

        return queryset

    def get_project(self, project_name):
        user = self.request.user
        queryset_project = Project.objects.filter(user=user).filter(name=project_name)
        project_instance = get_list_or_404(queryset_project)

        if len(project_instance) > 0:
            return project_instance[0]

        return None

    def get_media(self, project=None):
        queryset = Media.objects.filter(project=project)
        instance = get_list_or_404(queryset)

        if len(instance) > 0:
            return instance

        return None

    def list(self, request, pk=None):
        project = self.get_project(project_name=pk)

        if project is not None:
            media = self.get_media(project=project)
            data = []

            for media_s in media:
                cut_individual = Cut.objects.filter(media=media_s)
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


class EncodeView(viewsets.ModelViewSet):
    def get_project(self, project_name):
        user = self.request.user
        queryset_project = Project.objects.filter(user=user).filter(name=project_name)
        project_instance = get_list_or_404(queryset_project)

        if len(project_instance) > 0:
            return project_instance[0]

        return None

    def retrieve(self, request, pk=None):
        project_i = self.get_project(project_name=pk)
        project_i
