from django.shortcuts import get_list_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

import actoon.models.mediamodel
import actoon.models.taskmodel
import actoon.serializers.taskserializer
from actoon.views.apihelper import get_project


class EncodeView(viewsets.ModelViewSet):
    model = actoon.models.taskmodel.Task
    serializer_class = actoon.serializers.taskserializer.TaskListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, task_index=None):
        if project_name is not None:
            project_instance = get_project(self.request.user, project_name)

            if task_index is not None:
                queryset_task_object = self.model.objects.filter(project=project_instance) \
                    .order_by('created_at')

                if len(queryset_task_object) > task_index:
                    return queryset_task_object[task_index - 1]
            else:
                if project_instance is not None:
                    return self.model.objects.filter(project=project_instance).order_by('created_at')

        return None

    def retrieve(self, pk=None, tpk=None):
        if tpk is None:  # task id provided (preview)
            pass
        else:  # full-encode
            pass

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)