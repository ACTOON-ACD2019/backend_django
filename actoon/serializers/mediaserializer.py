from rest_framework import serializers

from actoon.models.mediamodel import Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = ['media_type', 'project', 'file', 'proceeded', 'proceeded_image']
        read_only_fields = ['project', 'proceeded', 'proceeded_image']
