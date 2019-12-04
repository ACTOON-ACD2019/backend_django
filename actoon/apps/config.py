import os
from django.apps import AppConfig

from actoon.apps.rpcclient import RpcClient


class ActoonConfig(AppConfig):
    name = 'actoon'

    def ready(self):
        # initializing custom event loop
        print(' [x] initializing rpc client')
        RpcClient()

        # creating temporary folder
        print(' [x] creating temporary folder')
        if not os.path.exists('/tmp/actoon'):
            os.makedirs('/tmp/actoon')
