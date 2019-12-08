from django.contrib import admin

from actoon.models import cutmodel, effectmodel, mediamodel, projectmodel, taskmodel

# Register your models here.
admin.site.register(cutmodel.Cut)
admin.site.register(mediamodel.Media)
admin.site.register(effectmodel.Effect)
admin.site.register(projectmodel.Project)
admin.site.register(taskmodel.Task)
