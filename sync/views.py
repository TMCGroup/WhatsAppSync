from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import datetime
from .models import Log, Server, Contact, Attachment, Message, Workspace, RapidProMessages


def download_attach(request):
    Server.sync_data()
    return render(request, 'download_attach.html', locals())


def close_connection(request):
    Server.close_connection()
    return render(request, 'close.html', locals())


def call_center_contacts(request):
    contacts = Contact.read_contact_csv()
    return render(request, 'contacts.html', locals())


def move_files(request):
    Attachment.move_mulitple_files()
    Log.move_mulitple_logs()
    return render(request, 'move_files.html', locals())


def enter_files_into_the_db(request):
    Log.add_mulitple_logs_from_logs_directory()
    Attachment.add_mulitple_files_from_files_directory()
    return render(request, 'add.html', locals())


def read_logs(request):
    contacts = Log.get_log_file()
    return render(request, 'read_logs.html', locals())


def send_rapidpro_data(request):
    message = Message.send_to_rapidpro()
    return render(request, 'sendtorapidpro.html', locals())


def get_reapidpro_messages(request):
    downloaded = RapidProMessages.get_rapidpro_messages(Workspace.get_rapidpro_workspaces())
    return render(request, 'getrapidpromessages.html', locals())


def archive_rapidpro(request):
    d = ''
    date = datetime.datetime.strptime(d, '%Y %m %d')
    msgs = RapidProMessages.objects.filter(modified_on__gte=date)
    archived = 0
    ls = []
    for msg in msgs:
        ls.append(msg.msg_id)
        if len(ls) == 100:
            break
        archived += 1
    archived = RapidProMessages.message_archiver(ls)
    return render(request, 'archived.html', locals())
