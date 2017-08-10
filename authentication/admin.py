from django.contrib import admin
from . import models

# Register your models here.

class HostAdmin(admin.ModelAdmin):
    list_display = ('name', 'ip')

admin.site.register(models.UserProfile)