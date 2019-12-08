from django.db import models

from actoon.models.cutmodel import Cut
from actoon.models.effectmodel import Effect
from actoon.models.projectmodel import Project


class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    parameters = models.CharField(max_length=255)
    image_properties = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
