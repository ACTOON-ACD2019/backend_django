from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

import actoon.serializers.userserializer


class RegisterView(viewsets.ModelViewSet):
    model = get_user_model()
    permission_classes = (permissions.AllowAny,)
    serializer_class = actoon.serializers.userserializer.UserSerializer
