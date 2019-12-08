from rest_framework import serializers

from actoon.models import Cut


class CutSerializer(serializers.ModelSerializer):
    file_upload = serializers.FileField(required=False)

    class Meta:
        model = Cut
        fields = ['file', 'type', 'sequence', 'sub_sequence', 'pos_x', 'pos_y', 'file_upload']
        read_only_fields = ['file', 'type', 'sequence', 'sub_sequence', 'pos_x', 'pos_y']

    def create(self, validated_data):
        validated_data.pop('file_upload')
        return Cut.objects.create(**validated_data)