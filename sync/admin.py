from django.contrib import admin
from .models import Log


class LogAdmin(admin.ModelAdmin):
    list_display = ('id','log', 'chat_type', 'created_on', 'synced', 'created_by', 'modified_by')
    list_filter = ('created_by', 'modified_by','created_on')
    search_fields = ['log']


admin.site.register(Log, LogAdmin)
