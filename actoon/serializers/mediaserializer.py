from rest_framework import serializers

from actoon.models.mediamodel import Media


class MediaSerializer(serializers.ModelSerializer):
    TYPE_TR_NOCHANGES = 'NO'
    TYPE_TR_ENGLISH = 'EN'
    TYPE_TR_KOREAN = 'KO'
    TYPE_TR_JAPANESE = 'JP'

    TYPE_TR = (
        (TYPE_TR_NOCHANGES, 'Original'),
        (TYPE_TR_ENGLISH, 'English'),
        (TYPE_TR_JAPANESE, 'Japanese'),
        (TYPE_TR_KOREAN, 'Korean'),
    )

    translate_to = serializers.CharField(max_length=2, choices=TYPE_TR, default=TYPE_TR_NOCHANGES)

    class Meta:
        model = Media
        fields = ['media_type', 'project', 'file', 'proceeded',
                  'proceeded_image', 'toon_type', 'translate_to']
        read_only_fields = ['project', 'proceeded', 'proceeded_image']
