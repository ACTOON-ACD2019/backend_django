from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _
from actoon.models import Effect, Media, Cut

# Register your models here.
admin.site.register(Effect)
admin.site.register(Media)
admin.site.register(Cut)
