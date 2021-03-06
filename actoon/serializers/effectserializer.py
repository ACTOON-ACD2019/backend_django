from rest_framework import serializers

from actoon.models.effectmodel import Effect


class EffectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Effect
        fields = ['name', 'required_parameters']
