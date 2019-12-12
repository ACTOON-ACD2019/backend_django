from django.shortcuts import get_list_or_404

import actoon.models.effectmodel
import actoon.models.mediamodel
import actoon.models.projectmodel
import actoon.models.cutmodel


def get_media(project=None):
    queryset = actoon.models.mediamodel.Media.objects \
        .filter(project=project)
    instance = get_list_or_404(queryset)

    if len(instance) > 0:
        return instance

    return None


def get_effect(name):
    queryset_effect = actoon.models.effectmodel.Effect.objects \
        .filter(name=name)
    effect_instance = get_list_or_404(queryset_effect)

    if len(effect_instance) > 0:
        return effect_instance[0]

    return None


def get_project(user, project_name):
    queryset_project = actoon.models.projectmodel.Project.objects \
        .filter(user=user) \
        .filter(name=project_name)
    project_instance = get_list_or_404(queryset_project)

    if len(project_instance) > 0:
        return project_instance[0]

    return None


def get_cut(cut_name):
    queryset_cut = actoon.models.cutmodel.Cut.objects \
        .filter(file=cut_name)
    cut_instance = get_list_or_404(queryset_cut)

    if len(cut_instance) > 0:
        return cut_instance[0]

    return None
