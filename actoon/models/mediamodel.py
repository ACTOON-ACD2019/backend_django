from django.db import models

from actoon.models.projectmodel import Project


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
    proceeded_image = models.CharField(max_length=255)
