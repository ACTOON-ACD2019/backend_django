import os
from django.apps import AppConfig

from actoon.apps.rpcclient import RpcClient
from actoon_backend.settings import BASE_DIR


class ActoonConfig(AppConfig):
    name = 'actoon'

    def ready(self):
        # creating temporary folder
        print(' [x] creating temporary folder')
        if not os.path.exists(BASE_DIR + '/temp/'):
            os.makedirs(BASE_DIR + '/temp/')
