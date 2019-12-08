from django.db import models

from actoon.models.mediamodel import Media


class Cut(models.Model):
    TYPE_SCENE = 'SC'
    TYPE_BUBBLE = 'BU'
    TYPE_TEXT = 'TX'
    TYPE_FULL_SCENE = 'FC'
    TYPE_UNDEFINED = 'UD'

    TYPE_PROCEEDED = [
        (TYPE_SCENE, 'Scene'),
        (TYPE_BUBBLE, 'Bubble'),
        (TYPE_TEXT, 'Text'),
        (TYPE_FULL_SCENE, 'FullScene'),
        (TYPE_UNDEFINED, 'Undefined')
    ]

    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    file = models.CharField(max_length=255)
    type = models.CharField(max_length=2, choices=TYPE_PROCEEDED, default=TYPE_UNDEFINED)
    pos_x = models.IntegerField(null=True)
    pos_y = models.IntegerField(null=True)
    sequence = models.IntegerField()
    sub_sequence = models.IntegerField(null=True)
    linked = models.ForeignKey('self', on_delete=models.CASCADE, null=True)  # link to proceeded(user-uploaded) cut
