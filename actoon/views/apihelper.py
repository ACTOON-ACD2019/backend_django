from django.shortcuts import get_list_or_404

from actoon import models as actoon_model


def get_media(project=None):
    queryset = actoon_model.Media.objects \
        .filter(project=project)
    instance = get_list_or_404(queryset)

    if len(instance) > 0:
        return instance

    return None


def get_effect(name):
    queryset_effect = actoon_model.Effect.objects \
        .filter(name=name)
    effect_instance = get_list_or_404(queryset_effect)

    if len(effect_instance) > 0:
        return effect_instance[0]

    return None


def get_project(user, project_name):
    queryset_project = actoon_model.Project.objects \
        .filter(user=user) \
        .filter(name=project_name)
    project_instance = get_list_or_404(queryset_project)

    if len(project_instance) > 0:
        return project_instance[0]

    return None
