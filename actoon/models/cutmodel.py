import asyncio

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from actoon.apps.rpcclient import RpcClient
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
        result = loop.run_until_complete(
            rpc_client.cut_slicing_request(instance.file))

        # close the loop
        loop.close()

        bubble_index = 0

        for cut_index in range(0, len(result['cut_info'])):
            current_cut = result['cut_info'][cut_index]
            pos_x, pos_y, _, _ = current_cut[0]

            # insert cut
            Cut(
                media=instance,
                file=result['cut'][cut_index]['file'],
                type='SC',
                sequence=cut_index
            ).save()

            # insert full cut
            Cut(
                media=instance,
                file=result['thumbnails'][cut_index]['file'],
                type='FC',
                sequence=cut_index
            ).save()

            # if there are cuts to be proceeded
            if len(current_cut[1]) > 0:
                bubbles_in_cut = current_cut[1]
                temp_bubble_index = bubble_index

                for str_index in bubbles_in_cut:
                    pos_bub_x, pos_bub_y, _, _ = bubbles_in_cut[str_index]

                    # insert bubble
                    Cut(
                        media=instance,
                        file=result['bubble'][int(str_index)]['file'],
                        type='BU',
                        sequence=cut_index,
                        sub_sequence=(bubble_index - temp_bubble_index),
                        pos_x=(pos_bub_x - pos_x),
                        pos_y=(pos_bub_y - pos_y)
                    ).save()

                    bubble_index += 1

        # insert proceeded image
        instance.proceeded_image = result['final']['file']
        instance.proceeded = True
        instance.save()