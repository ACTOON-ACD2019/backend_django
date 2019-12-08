from django.db import models


class Effect(models.Model):
    name = models.CharField(max_length=50)
    required_parameters = models.CharField(max_length=255)
