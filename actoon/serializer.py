from rest_framework import serializers
from actoon.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'description']
        read_only_fields = ['id']
