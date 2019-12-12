from rest_framework import serializers

from actoon.models.taskmodel import Task


class TaskListSerializer(serializers.ModelSerializer):
    cut_file = serializers.ReadOnlyField(source='cut.file')
    effect_name = serializers.ReadOnlyField(source='effect.name')
    project_resolution_width = serializers.ReadOnlyField(source='project.resolution_width')
    project_resolution_height = serializers.ReadOnlyField(source='project.resolution_height')

    class Meta:
        model = Task
        fields = [
            'effect_name',
            'cut_file',
            'image_properties',
            'project_resolution_width',
            'project_resolution_height',
            'parameters',
            'created_at'
        ]


class TaskSerializer(serializers.ModelSerializer):
    effect_name = serializers.CharField(max_length=50)
    cut_name = serializers.CharField(max_length=50)

    class Meta:
        model = Task
        fields = [
            'effect',
            'effect_name',
            'cut',
            'cut_name',
            'image_properties',
            'project',
            'parameters',
            'created_at'
        ]
        read_only_fields = ['effect', 'cut', 'project', 'created_at']

    def create(self, validated_data):
        validated_data.pop('effect_name')  # remove the field which is not a member
        validated_data.pop('cut_name')
        return Task.objects.create(**validated_data)
