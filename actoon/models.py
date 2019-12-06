import asyncio
from django.dispatch import receiver
from django.db import models
from django.db.models.signals import post_save
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


# Project
from actoon.apps.rpcclient import RpcClient


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
    proceeded = models.BooleanField(default=False)


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
    file = models.CharField(max_length=255)
    type = models.CharField(max_length=2, choices=TYPE_PROCEEDED, default=TYPE_UNDEFINED)
    sequence = models.IntegerField()


# History (Task)
# merging Action and Task model to simplify model
class Task(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    cut = models.ForeignKey(Cut, on_delete=models.CASCADE)
    effect = models.ForeignKey(Effect, on_delete=models.CASCADE)
    parameters = models.CharField(max_length=255)
    image_properties = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Media)
def create_cuts(sender, instance=None, created=False, **kwargs):
    if created and instance.media_type == 'TO':
        # setup event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # initialize rpc client
        rpc_client = RpcClient(loop)

        # connect
        loop.run_until_complete(rpc_client.connect())

        # request
        files = loop.run_until_complete(
            rpc_client.cut_slicing_request(instance.file))

        # close the loop
        loop.close()

        for data in files:
            obj = Cut(
                media=instance,
                file=data['file'],
                type=data['type'],
                sequence=data['sequence']
            )

            obj.save()

        instance.proceeded = True
        instance.save()
