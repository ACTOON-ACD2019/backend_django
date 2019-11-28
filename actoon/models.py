import os

from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


# Project
class Project(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  # name should be unique value per each users
    description = models.CharField(max_length=255)


# managing available effects
class Effect(models.Model):
    name = models.CharField(max_length=50)
    required_parameters = models.CharField(max_length=255)


# managing media file
class Media(models.Model):
    TYPE_CARTOON = 'TO'
    TYPE_AUDIO = 'AU'
    TYPE_MOVIE = 'MO'
    TYPE_UNDEFINED = 'UD'

    TYPE_MEDIA = [
        (TYPE_CARTOON, 'Cartoon'),
        (TYPE_AUDIO, 'Audio'),
        (TYPE_MOVIE, 'Movie'),
        (TYPE_UNDEFINED, 'Undefined')
    ]

    media_type = models.CharField(max_length=2, choices=TYPE_MEDIA, default=TYPE_UNDEFINED)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(blank=False, null=False)


# managing each cut
class Cut(models.Model):
    TYPE_SCENE = 'SC'
    TYPE_BUBBLE = 'BU'
    TYPE_TEXT = 'TX'
    TYPE_UNDEFINED = 'UD'

    TYPE_PROCEEDED = [
        (TYPE_SCENE, 'Scene'),
        (TYPE_BUBBLE, 'Bubble'),
        (TYPE_TEXT, 'Text'),
        (TYPE_UNDEFINED, 'Undefined')
    ]

    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    file = models.FileField(blank=False, null=False)
    type = models.CharField(max_length=2, choices=TYPE_PROCEEDED, default=TYPE_UNDEFINED)
    sequence = models.IntegerField()


# History (Task)
# merging Action and Task model to simplify model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    # cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    parameters = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
