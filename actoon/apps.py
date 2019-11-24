from django.apps import AppConfig
import uuid
import json
from aio_pika import connect, IncomingMessage, Message
from django.core.files import File
import base64
import asyncio
import zipfile
import os

# from actoon.models import Cut


class ActoonConfig(AppConfig):
    name = 'actoon'


class RpcClient:
    def __init__(self, loop):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = loop

    async def connect(self):
        self.connection = await connect(
            "amqp://test:test1234@beta.actoon.sokdak.me/", loop=self.loop
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            exclusive=True
        )
        await self.callback_queue.consume(self.on_response)

        return self

    def on_response(self, message: IncomingMessage):
        future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call_cut_slicing(self, filename):
        hexa = open(filename.file.name, 'rb').read()
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                base64.b64encode(hexa),
                content_type=filename.file.name.split('.')[-1],
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key='rpc_cut_slicing_queue',
        )

        return await future


async def request(loop, task, media=None):
    deeplearning_client = await RpcClient(loop).connect()
    print(" [x] Requesting cut slicing %s" % media.file)

    if task is 'cut_slicing':
        # make a rpc call
        response = await deeplearning_client.call_cut_slicing(media.file)
        open('./media/temp/result_received.zip', 'wb').write(base64.b64decode(response))

        # uncompressing zip
        with zipfile.ZipFile('./media/temp/result_received.zip', 'r') as zip_ref:
            zip_ref.extractall('./media/temp/')
    else:
        # preprocessing histories

        # go ahead
        pass
