from rest_framework import serializers

from actoon.models.taskmodel import Task


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'effect',
            'cut',
            'image_properties',
            'project',
            'parameters',
            'created_at'
        ]


class TaskSerializer(serializers.ModelSerializer):
    effect_name = serializers.CharField(max_length=50)

    class Meta:
        model = Task
        fields = [
            'effect',
            'effect_name',
            'cut',
            'image_properties',
            'project',
            'parameters',
            'created_at'
        ]
        read_only_fields = ['effect', 'project', 'created_at']

    def create(self, validated_data):
        self.validated_data.pop('effect_name')  # remove the field which is not a member
        return Task.objects.create(**validated_data)
