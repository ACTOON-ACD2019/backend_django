from rest_framework import serializers

from actoon.models.projectmodel import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name',
            'description'
        ]