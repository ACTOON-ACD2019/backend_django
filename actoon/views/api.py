from rest_framework import viewsets, permissions
from rest_framework.response import Response
from actoon.models import Project
from actoon.serializer import ProjectSerializer
from django.shortcuts import get_object_or_404, get_list_or_404


class ProjectView(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def list(self, request):
        queryset = Project.objects.all()
        instance = get_list_or_404(queryset, user_id=self.request.user)
        serializer = ProjectSerializer(instance, many=True)
        return Response(serializer.data)

    def retrieve(self, request, project_pk=None):
        queryset = Project.objects.filter(user_id=self.request.user)
        instance = get_object_or_404(queryset, pk=project_pk)
        serializer = ProjectSerializer(instance)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid() is True:
            obj = self.perform_create(serializer, user=self.request.user)
            return Response(obj.id)
        else:
            return Response(status=400)

    def perform_create(self, serializer, user):
        obj = serializer.save(user=self.request.user)
        return obj
