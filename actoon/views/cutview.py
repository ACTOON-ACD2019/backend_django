from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import get_list_or_404, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.utils import json

import actoon.models.cutmodel
import actoon.serializers.cutserializer
from actoon.apps.renamer import create_random_name
from actoon.models.cutmodel import Cut
from actoon.views.apihelper import get_project, get_media
from actoon_backend.settings import BASE_DIR


class CutView(viewsets.ModelViewSet):
    model = actoon.models.cutmodel.Cut
    serializer_class = actoon.serializers.cutserializer.CutSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, media=None):
        if media is not None:
            queryset = self.model.objects.filter(media=media)
        else:
            queryset = self.model.Cut.objects.all()

        return queryset

    def list(self, request, pk=None):
        project = get_project(self.request.user, project_name=pk)

        if project is not None:
            media = get_media(project=project)
            data = []

            for media_s in media:
                if media_s.proceeded is True:
                    cut_individual = actoon.models.cutmodel.Cut.objects.filter(media=media_s).filter(linked=None)
                    instances = get_list_or_404(cut_individual)

                    # arrange with cut sequence
                    instances.sort(key=lambda x: x.sequence)

                    bubbles = []
                    cuts = []
                    full_cuts = []

                    for instance in instances:
                        if instance.type == 'SC':
                            cuts.append(instance)
                        elif instance.type == 'FC':
                            full_cuts.append(instance)
                        elif instance.type == 'BU':
                            bubbles.append(instance)

                    # make a empty field
                    for index, cut in enumerate(cuts):
                        bubbles_in_cut = []

                        for bubble in bubbles:
                            if bubble.sequence is index:
                                bubbles_in_cut.append(
                                    self.get_serializer(bubble).data)

                        _data = {
                            'thumbnail': self.get_serializer(full_cuts[index]).data,
                            'background': self.get_serializer(cut).data,
                            'bubbles': bubbles_in_cut
                        }

                        data.append(_data)
                else:
                    print(' [x] %s is not proceeded, skipping...' % media_s)

            if len(data) > 0:
                return Response(json.dumps(data))
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_400_BAD_REQUEST)

    @method_decorator(csrf_exempt)
    def update(self, request, pk=None, cpk=None):
        project_instance = get_project(self.request.user, pk)
        media_instance = get_media(project_instance)

        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            for media in media_instance:
                cuts = Cut.objects.filter(media=media).filter(file=cpk)

                if cuts.exists():
                    cut_original = get_object_or_404(cuts)

                    uploaded_file = serializer.validated_data['file_upload']
                    temp_folder = BASE_DIR + '/media/'

                    random_name = create_random_name(temp_folder, '.' + uploaded_file.name.split('.')[-1])

                    new_file = default_storage.save(random_name, ContentFile(uploaded_file.read()))

                    instance = Cut(
                        file=new_file,
                        media=cut_original.media,
                        type=cut_original.type,
                        sequence=cut_original.sequence,
                        sub_sequence=cut_original.sub_sequence,
                        pos_x=cut_original.pos_x,
                        pos_y=cut_original.pos_y
                    )
                    instance.save()

                    cut_original.linked = instance
                    cut_original.save()

                    return Response(self.get_serializer(instance).data, status=status.HTTP_202_ACCEPTED)

            return Response({'errors': 'no such cut'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def pre_save(self, obj):
        obj.file = self.request.FILES.get('file')
