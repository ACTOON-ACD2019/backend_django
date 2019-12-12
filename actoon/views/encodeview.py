import asyncio
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

import actoon.models.mediamodel
import actoon.models.taskmodel
from actoon.serializers.taskserializer import TaskSerializer, TaskListSerializer
from actoon.serializers.cutserializer import CutSerializer
from actoon.apps.rpcclient import RpcClient
from actoon.models.cutmodel import Cut
from actoon.models.taskmodel import Task
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
                    return queryset_task_object[task_index]
            else:
                if project_instance is not None:
                    return self.model.objects.filter(project=project_instance).order_by('created_at')

        return None

    def retrieve(self, request, pk=None, tpk=None):
        if pk is not None and tpk is not None:  # task id provided (preview)
            task = self.get_queryset(project_name=pk, task_index=tpk)

            if task is not None:
                target_cut = task.cut
                target_sequence = target_cut.sequence

                related_cuts = Cut.objects\
                    .filter(media=target_cut.media)\
                    .filter(sequence=target_sequence)\
                    .exclude(type='FC')

                # querying another tasks
                related_tasks = []

                for cut in related_cuts:
                    related_tasks += Task.objects.filter(cut=cut)

                # send related tasks to encoding server
                cuts_jsondata = CutSerializer(related_cuts, many=True).data
                tasks_jsondata = TaskListSerializer(related_tasks, many=True).data

                # setup event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # initialize rpc client
                rpc_client = RpcClient(loop)

                # connect
                loop.run_until_complete(rpc_client.connect())

                # request
                result = loop.run_until_complete(
                    rpc_client.encode_request({'tasks': tasks_jsondata, 'cuts': cuts_jsondata}))

                # close the loop
                loop.close()

                if result['result'] == 'success':
                    return Response({'preview': result['file']}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'encode failed with specified scene'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR);
            else:
                return Response({'error': 'no such task'}, status=status.HTTP_400_BAD_REQUEST)
        else:  # full-encode and merge encoded files
            pass

        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

    def create(self, pk=None):
        pass
