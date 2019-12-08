from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response

import actoon.models.projectmodel
import actoon.serializers.projectserializer


class ProjectView(viewsets.ModelViewSet):
    serializer_class = actoon.serializers.projectserializer.ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, name=None):
        user = self.request.user

        if name is None:
            return actoon.models.projectmodel.Project.objects.filter(user=user)
        else:
            return actoon.models.projectmodel.Project.objects \
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
                instance = self.perform_create(serializer, user=self.request.user)
                return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)

            return Response({'errors': 'given project name has been already taken'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        queryset = self.get_queryset(pk)
        instance = get_object_or_404(queryset)
        serializer = self.get_serializer(instance, data=request.data)

        if serializer.is_valid():
            instance.name = serializer.validated_data['name']

            if instance.description != serializer.validated_data['description']:
                instance.description = serializer.validated_data['description']

            instance.save()

            return Response(self.get_serializer(instance).data, status=status.HTTP_202_ACCEPTED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        queryset = self.get_queryset(name=pk)

        if queryset.count() > 0:
            self.perform_destroy(queryset)
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'no such project'}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer, user):
        return serializer.save(user=self.request.user)
