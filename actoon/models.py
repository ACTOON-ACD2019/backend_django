from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


# Project
class Project(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)


# managing action
class Action(models.Model):
    ACTION_TYPE_MOVE = 'MOVE'
    ACTION_TYPE_SWING = 'SWIG'
    ACTION_TYPE_APPEAR = 'APER'
    ACTION_TYPE_UNDEFINED = 'UDEF'

    TYPE_ACTION = [
        (ACTION_TYPE_MOVE, 'Move'),
        (ACTION_TYPE_SWING, 'Swing'),
        (ACTION_TYPE_APPEAR, 'Appear'),
        (ACTION_TYPE_UNDEFINED, 'Undefined')
    ]

    action = models.CharField(max_length=4, choices=TYPE_ACTION, default=ACTION_TYPE_UNDEFINED)
    pos_x_init = models.FloatField()
    pos_y_init = models.FloatField()
    pos_x_fin = models.FloatField()
    pos_y_fin = models.FloatField()


# History (Task)
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


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
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE)
    location = models.CharField(max_length=255)


# managing each cut
class Cut(models.Model):
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    sequence = models.IntegerField()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
