from rest_framework import serializers

from actoon.models.projectmodel import Project


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name',
            'description',
            'resolution_width',
            'resolution_height',
            'created_at'
        ]
        read_only_fields = ['created_at']
