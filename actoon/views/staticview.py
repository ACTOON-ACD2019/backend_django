from django.core.files.storage import default_storage
from django.shortcuts import HttpResponse


def media(request):
    file = request.path_info.split('/')[-1]
    return HttpResponse(default_storage.open(file).read(), content_type='application/binary')
