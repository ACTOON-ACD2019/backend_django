from django.shortcuts import get_list_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

import actoon.models.taskmodel
import actoon.serializers.taskserializer
from actoon.views.apihelper import get_project, get_effect, get_cut


class TaskView(viewsets.ModelViewSet):
    model = actoon.models.taskmodel.Task
    serializer_class = actoon.serializers.taskserializer.TaskSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, task_index=None):
        if project_name is not None:
            project_instance = get_project(self.request.user, project_name)

            if task_index is not None:
                queryset_task_object = self.model.objects.filter(project=project_instance) \
                    .order_by('-created_at')

                if len(queryset_task_object) > task_index:
                    return queryset_task_object[task_index - 1]
            else:
                if project_instance is not None:
                    return self.model.objects.filter(project=project_instance).order_by('created_at')

        return None

    def list(self, request, pk=None):
        queryset = self.get_queryset(project_name=pk)

        if queryset is not None:
            instance = get_list_or_404(queryset)  # 404 if there are no tasks in project
            serializer = actoon.serializers.taskserializer.TaskListSerializer(instance, many=True)
            # serializer.validated_data.pop('project')  # remove project_id from task results
            return Response(serializer.data)

        return Response({'errors': 'no such project'},
                        status=status.HTTP_400_BAD_REQUEST)  # no such project

    def create(self, request, pk=None):
        if request.data.__contains__('effect_name'):  # validate on server-side
            if request.data.__contains__('cut_name'):
                serializer = self.get_serializer(data=request.data)

                if serializer.is_valid() is True:
                    effect = get_effect(serializer.validated_data['effect_name'])  # sets the effect object
                    cut = get_cut(serializer.validated_data['cut_name'])
                    project = get_project(self.request.user, pk)  # get projects to insert task

                    if project is not None:
                        instance = self.perform_create(serializer, effect, project, cut)
                        return Response(status=status.HTTP_201_CREATED)  # serializer problem
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # no effect name

            return Response({'errors': 'no cut name'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'errors': 'no effect name'}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, tpk=None):
        instance = self.get_queryset(project_name=pk, task_index=tpk)

        if instance is not None:
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'no such project or index'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, effect, project, cut):
        return serializer.save(effect=effect, project=project, cut=cut)
