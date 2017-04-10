from django.contrib import admin
from .models import Log, Notification, Message, Contact


class LogAdmin(admin.ModelAdmin):
    list_display = ('id','log', 'chat_type', 'created_on', 'synced')
    list_filter = ['created_on']
    search_fields = ['log']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id','text', 'sent_date', 'created_on', 'modified_on')
    list_filter = ('modified_on','created_on')
    search_fields = ['id']


class ContactAdmin(admin.ModelAdmin):
    list_display = ('id','number', 'name', 'created_on', 'modified_on')
    list_filter = ('modified_on','created_on')
    search_fields = ['id']

class MessageAdmin(admin.ModelAdmin):
    list_display = ('id','text', 'sent_date', 'contact')
    list_filter = ('modified_on','created_on')
    fieldsets = [
        (None, {'fields': ['contact']}),
    ]
    search_fields = ['id', 'text']

admin.site.register(Log, LogAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Contact, ContactAdmin)
