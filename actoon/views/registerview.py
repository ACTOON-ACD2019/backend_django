from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

from actoon import serializer as actoon_serializer


class RegisterView(viewsets.ModelViewSet):
    model = get_user_model()
    permission_classes = (permissions.AllowAny,)
    serializer_class = actoon_serializer.UserSerializer