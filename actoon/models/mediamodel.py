from django.db import models

from actoon.models.projectmodel import Project


class Media(models.Model):
    TYPE_CARTOON = 'TO'
    TYPE_AUDIO = 'AU'
    TYPE_MOVIE = 'MO'
    TYPE_UNDEFINED = 'UD'

    TYPE_TOON_COMIC = 'TC'
    TYPE_TOON_BLACK = 'WB'
    TYPE_TOON_WHITE = 'WW'

    TYPE_MEDIA = [
        (TYPE_CARTOON, 'Cartoon'),
        (TYPE_AUDIO, 'Audio'),
        (TYPE_MOVIE, 'Movie'),
        (TYPE_UNDEFINED, 'Undefined')
    ]

    TYPE_TOON = [
        (TYPE_TOON_COMIC, 'Comic'),
        (TYPE_TOON_BLACK, 'Webtoon (Black)'),
        (TYPE_TOON_WHITE, 'Webtoon (White)')
    ]

    media_type = models.CharField(max_length=2, choices=TYPE_MEDIA, default=TYPE_UNDEFINED)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    file = models.FileField(blank=False, null=False)
    proceeded = models.BooleanField(default=False)
    proceeded_image = models.CharField(max_length=255)
    toon_type = models.CharField(max_length=2, choices=TYPE_TOON, default=TYPE_TOON_WHITE)
