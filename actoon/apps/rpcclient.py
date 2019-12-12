import base64
import json
import os
import pathlib
import shutil
import uuid
import zipfile

from aio_pika import connect, IncomingMessage, Message
from django.core.files import File

from actoon.apps.renamer import create_random_name
from actoon_backend.settings import MEDIA_ROOT, BASE_DIR


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


def load_files(random_file, cut_type):
    return_list = []

    if cut_type is not 'final':
        # search provided types
        for root, dirs, files in os.walk(random_file + '.extracted/root/predictions/' + cut_type + '/'):
            for file in files:
                file = File(open(os.path.join(root, file), 'rb'))
                new_name = create_random_name(MEDIA_ROOT, pathlib.Path(file.name).suffix)
                new_path = MEDIA_ROOT + new_name
                os.rename(file.name, new_path)

                context = {
                    'type': cut_type,
                    'sequence': int(file.name.split('.')[-2].split('/')[-1]) if cut_type == 'bubble' else int(file.name.split('.')[-2].split('_')[-1]),
                    'file': new_name
                }

                return_list.append(context)

        return_list.sort(key=lambda x: x['sequence'])
    else:
        file = File(open(random_file + '.extracted/root/predictions/final/1.jpg'))
        new_name = create_random_name(MEDIA_ROOT, pathlib.Path(file.name).suffix)
        new_path = MEDIA_ROOT + new_name
        os.rename(file.name, new_path)

        return_list.append({
            'file': new_name,
            'type': 'proceeded_result'
        })

    return return_list


class RpcClient:
    rpc_connection = 'amqp://guest:guest@127.0.0.1/'
    rpc_queue_cut_slicing = 'rpc_cut_slicing_queue'
    rpc_queue_encoding = 'rpc_encoding_queue'
    temp_folder = BASE_DIR + '/temp/'

    def __init__(self, loop):
        self.connection = None
        self.channel = None
        self.callback_queue = None
        self.futures = {}
        self.loop = loop
        self.correlation_id = str(uuid.uuid4())

    async def close(self):
        await self.connection.close()

    async def connect(self):
        self.connection = await connect(
            self.rpc_connection, loop=self.loop
        )
        self.channel = await self.connection.channel()
        self.callback_queue = await self.channel.declare_queue(
            exclusive=True
        )
        await self.callback_queue.consume(self.on_response, no_ack=True)

        return self

    def on_response(self, message: IncomingMessage):
        future = self.futures.pop(message.correlation_id)
        future.set_result(message.body)

    async def call_cut_slicing(self, filename):
        data = open(filename.file.name, 'rb').read()
        future = self.loop.create_future()

        self.futures[self.correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                base64.b64encode(data),
                content_type=filename.file.name.split('.')[-1],
                correlation_id=self.correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=self.rpc_queue_cut_slicing,
        )

        return await future

    async def call_encoding(self, json_tasks):
        future = self.loop.create_future()

        self.futures[self.correlation_id] = future

        await self.channel.default_exchange.publish(
            Message(
                base64.b64encode(json_tasks.encode('utf-8')),
                content_type="task_data/json",
                correlation_id=self.correlation_id,
                reply_to=self.callback_queue.name,
            ),
            routing_key=self.rpc_queue_encoding,
        )

        return await future

    async def cut_slicing_request(self, media):
        print(" [x] Requesting cut slicing %s with event loop" % media.file)

        # make a rpc call
        response = json.loads(
            base64.b64decode(
                str(await self.call_cut_slicing(media.file),
                    'utf-8')))

        await self.close()

        random_name = create_random_name(self.temp_folder, '.zip')
        random_file = self.temp_folder + random_name

        open(random_file, 'wb').write(base64.b64decode(response['data']))

        # uncompressing zip
        with zipfile.ZipFile(random_file, 'r') as zip_ref:
            os.mkdir(random_file + '.extracted')
            zip_ref.extractall(random_file + '.extracted')

        # search cut/bubble/rect_cut/final images
        return_val = {
            'cut_info': json.loads(response['header']),
            'cut': load_files(random_file, 'cut'),
            'bubble': load_files(random_file, 'bubble'),
            'thumbnails': load_files(random_file, 'thumbnails'),
            'final': load_files(random_file, 'final')[0]
        }

        cleanup_folder(self.temp_folder)

        return return_val

    async def encode_request(self, tasks):
        print(" [x] Requesting encode")

        response = json.loads(str(await self.call_encoding(json.dumps(tasks)), 'utf-8'))

        await self.close()

        result = response['result']
        file_payload = base64.b64decode(response['file'])

        random_name = create_random_name(self.temp_folder, '.mp4')
        random_file = self.temp_folder + random_name

        open(random_file, 'wb').write(file_payload)

        return_val = {
            'result': result,
            'file': random_name
        }

        return return_val

    @staticmethod
    async def text_recognize(task, media=None):
        print(" [x] Requesting text recognition from cut")
        # should be implemented
