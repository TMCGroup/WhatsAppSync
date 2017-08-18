from django.contrib import admin
from .models import Log, Notification, Message, Contact, Server, ContactCsv, Attachment, Workspace


class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'log', 'chat_type', 'created_on', 'synced')
    list_filter = ['created_on']
    search_fields = ['log']


class ServerAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'user_name', 'host', 'status', 'created_on')
    list_filter = ['status', 'created_on']
    search_fields = ['owner', 'host']


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'contact', 'text', 'log', 'sent_date', 'created_on', 'modified_on')
    list_filter = ('modified_on', 'created_on')
    search_fields = ['id']


class ContactCsvAdmin(admin.ModelAdmin):
    list_display = ('id', 'csv_log', 'synced', 'created_on')
    list_filter = ('created_on', 'synced')
    search_fields = ['id']


class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'file', 'created_on', 'synced')
    list_filter = ('created_on', 'synced')
    search_fields = ['id']


class ContactAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'name', 'number', 'alt_number', 'created_on', 'modified_on')
    list_filter = ('modified_on', 'created_on')
    search_fields = ['id']


class MessageAdmin(admin.ModelAdmin):
    list_display = ('uuid', 'contact', 'text', 'attachment', 'log', 'sent_date', 'created_on')
    list_filter = ('modified_on', 'created_on')
    search_fields = ['id', 'text']


class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('name','host', 'key', 'external_channel_receive_url', 'active_status')
    list_filter = ('modified_on', 'created_on')
    search_fields = ['id', 'name']


admin.site.register(Server, ServerAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Attachment, AttachmentAdmin)
admin.site.register(ContactCsv, ContactCsvAdmin)
admin.site.register(Log, LogAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(Workspace, WorkspaceAdmin)
