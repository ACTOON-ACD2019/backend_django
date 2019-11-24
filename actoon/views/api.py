from rest_framework import status
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from actoon.models import Project, Task, Effect
from actoon.serializer import ProjectSerializer, TaskSerializer, EffectSerializer, TaskListSerializer
from django.shortcuts import get_list_or_404, get_object_or_404


class ProjectView(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, )

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
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self, project_name=None, task_index=None):
        if project_name is not None:
            project_instance = self.get_project(project_name)

            if task_index is not None:
                queryset_task_object = Task.objects.filter(project=project_instance)\
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
    permission_classes = (permissions.IsAuthenticated, )

    def list(self, request):
        queryset = self.get_queryset()
        instance = get_list_or_404(queryset)
        serializer = EffectSerializer(instance, many=True)
        return Response(serializer.data)
