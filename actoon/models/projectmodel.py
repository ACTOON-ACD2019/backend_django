from django.contrib.auth import get_user_model
from django.db import models


class Project(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # name should be unique value per each users
    description = models.CharField(max_length=255)
