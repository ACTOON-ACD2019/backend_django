import asyncio
import base64
import os
import uuid
import zipfile
import shutil
import pathlib

from aio_pika import connect, IncomingMessage, Message
from django.core.files import File
from actoon_backend.settings import MEDIA_ROOT, BASE_DIR
from actoon.apps.renamer import create_random_name


def cleanup_folder(folder):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)

        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))


class SingletonDecorator:
    def __init__(self, klass):
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


@SingletonDecorator
class RpcClient:
    rpc_connection = 'amqp://guest:guest@127.0.0.1/'
    rpc_queue_cut_slicing = 'rpc_cut_slicing_queue'
    temp_folder = BASE_DIR + '/temp/'

    def __init__(self):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        self.connection = await connect(
            self.rpc_connection, loop=self.loop
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
        data = open(filename.file.name, 'rb').read()
        correlation_id = str(uuid.uuid4())
        future = self.loop.create_future()

        self.futures[correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                base64.b64encode(data),
                content_type=filename.file.name.split('.')[-1],
                correlation_id=correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=self.rpc_queue_cut_slicing,
        )

        return await future

    async def cut_slicing_request(self, media):
        print(" [x] Requesting cut slicing %s" % media.file)

        # make a rpc call
        response = await self.call_cut_slicing(media.file)

        random_name = create_random_name(self.temp_folder, '.zip')
        random_file = self.temp_folder + random_name

        open(random_file, 'wb').write(base64.b64decode(response))

        # uncompressing zip
        with zipfile.ZipFile(random_file, 'r') as zip_ref:
            os.mkdir(random_file + '.extracted')
            zip_ref.extractall(random_file + '.extracted')

        return_val = []

        # walking into directories
        for root, dirs, files in os.walk(random_file + '.extracted' + '/test/predictions'):
            for file in files:
                file = File(open(os.path.join(root, file), 'rb'))
                new_name = create_random_name(MEDIA_ROOT, pathlib.Path(file.name).suffix)
                new_path = MEDIA_ROOT + new_name
                os.rename(file.name, new_path)

                context = {}

                if file.name.__contains__('bubble'):
                    cut_type = 'bubble'
                elif file.name.__contains__('cut'):
                    cut_type = 'cut'
                elif file.name.__contains__('text'):
                    cut_type = 'text'
                else:
                    continue

                context['file'] = new_name
                context['type'] = cut_type
                context['sequence'] = int(file.name.split('.')[-2].split('_')[-1])
                return_val.append(context)

        cleanup_folder(self.temp_folder)

        return return_val

    @staticmethod
    async def encode_request(task, media=None):
        print(" [x] Requesting encoding")
        # should be implemented

    @staticmethod
    async def text_recognize(task, media=None):
        print(" [x] Requesting text recognition from cut")
        # should be implemented
