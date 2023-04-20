from django.contrib import admin
from . import models

# Register your models here.

class RecordAdmin(admin.ModelAdmin):
    """
    record admin model
    """
    list_display = ( 'host', 'zone', 'type', 'data', 'ttl', 'status', 'create_time', 'update_time')
    search_fields = ('host',)
    raw_id_fields = ('zone_tag',)

class ZoneTagAdmin(admin.ModelAdmin):
    list_display = ('zone_name', 'comment')
    search_fields = ('zone_name',)


admin.site.register(models.Record, RecordAdmin)
admin.site.register(models.ZoneTag, ZoneTagAdmin)