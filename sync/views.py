from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.conf import settings
import datetime
from .models import Log, Server, Contact, Attachment, Message, Workspace, RapidProMessages


def download_attach(request):
    downloads = Server.sync_data()
    return render(request, 'download_attach.html', locals())


def close_connection(request):
    Server.close_connection()
    return render(request, 'close.html', locals())


def call_center_contacts(request):
    contacts = Contact.read_contact_csv()
    return render(request, 'contacts.html', locals())


def move_files(request):
    attachments = Attachment.move_mulitple_files()
    logs = Log.move_mulitple_logs()
    return render(request, 'move_files.html', locals())


def enter_files_into_the_db(request):
    logs = Log.add_mulitple_logs_from_logs_directory()
    attachments = Attachment.add_mulitple_files_from_files_directory()
    return render(request, 'add.html', locals())


def read_logs(request):
    read = Log.get_log_file()
    return render(request, 'read_logs.html', locals())


def send_rapidpro_data(request):
    message = Message.send_message_to_rapidpro()
    return render(request, 'sendtorapidpro.html', locals())


def label_rapidpro_data(request):
    message = Message.get_messages_to_label()
    return render(request, 'labelrapidpro.html', locals())


def get_rapidpro_messages(request):
    downloaded = RapidProMessages.get_rapidpro_messages(Workspace.get_rapidpro_workspaces())
    return render(request, 'getrapidpromessages.html', locals())


def archive_rapidpro(request):
    d = '2017 1 1'
    date = datetime.datetime.strptime(d, '%Y %m %d')
    i = 0
    while i < 1000:
        msgs = RapidProMessages.objects.filter(Q(modified_on__gte=date) & Q(archived=False)).order_by('id')[:100]
        archived = 0
        ls = []
        if not msgs:
            return
        for msg in msgs:
            ls.append(msg.msg_id)
        archived = RapidProMessages.message_archiver(ls)
        i += 1
    return render(request, 'archived.html', locals())


def delete_rapidpro(request):
    d = '2018 6 19'
    date = datetime.datetime.strptime(d, '%Y %m %d')
    msgs = RapidProMessages.objects.filter(Q(modified_on__gte=date) & Q(deleted=False)).order_by('id')[:100]
    deleted = 0
    ls = []
    for msg in msgs:
        ls.append(msg.msg_id)
    deleted = RapidProMessages.message_deleter(ls)
    return render(request, 'deleted.html', locals())
