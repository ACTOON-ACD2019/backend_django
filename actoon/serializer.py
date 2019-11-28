from django.contrib.auth import get_user_model
from rest_framework import serializers
from actoon.models import Project, Task, Media, Effect, Cut


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'name',
            'description'
        ]


class TaskListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'effect',
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
            'project',
            'parameters',
            'created_at'
        ]
        read_only_fields = ['effect', 'project', 'created_at']

    def create(self, validated_data):
        validated_data.pop('effect_name')  # remove the field which is not a member
        return Task.objects.create(**validated_data)


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['media_type', 'project', 'file']
        read_only_fields = ['project']


class EffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = ['name', 'required_parameters']


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'password', 'email']
        write_only_fields = ['password']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = get_user_model().objects.create(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class CutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cut
        fields = ['file', 'type', 'sequence']
