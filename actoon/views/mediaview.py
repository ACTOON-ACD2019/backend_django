from django.shortcuts import get_list_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

import actoon.models.mediamodel
import actoon.serializers.mediaserializer
from actoon.views.apihelper import get_project


class MediaView(viewsets.ModelViewSet):
    model = actoon.models.mediamodel.Media
    serializer_class = actoon.serializers.mediaserializer.MediaSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, project_name=None, media_id=None):
        if project_name is not None:
            project_instance = get_project(self.request.user, project_name)

            if media_id is not None:
                queryset_media_object = self.model.objects.filter(pk=media_id)

                if len(queryset_media_object) > 0:
                    return queryset_media_object[0]
            else:
                if project_instance is not None:
                    return self.model.objects.filter(project=project_instance)

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
                instance = self.perform_create(serializer, project=project)
                return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

            return Response({'errors': 'no such project'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def pre_save(self, obj):
        obj.file = self.request.FILES.get('file')

    def perform_create(self, serializer, project=None):
        return serializer.save(project=project)
