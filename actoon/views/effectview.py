from django.shortcuts import get_list_or_404, get_object_or_404
from rest_framework import viewsets, permissions
from rest_framework.response import Response

import actoon.models.effectmodel
import actoon.serializers.effectserializer


class EffectView(viewsets.ModelViewSet):
    model = actoon.models.effectmodel.Effect
    queryset = model.objects.all()
    serializer_class = actoon.serializers.effectserializer.EffectSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, pk=None):
        if pk is not None:
            queryset = self.model.objects.all(pk=pk)
        else:
            queryset = self.model.objects.all()

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
