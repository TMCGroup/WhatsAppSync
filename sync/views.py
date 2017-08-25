from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Log, Server, Contact, Attachment, Message


def download_attach(request):
    Server.sync_data()
    return render(request, 'download_attach.html', locals())


def closeconnection(request):
    Server.close_connection()
    return render(request, 'close.html', locals())


def call_center_contacts(request):
    contacts = Contact.read_contact_csv()
    return render(request, 'contacts.html', locals())


def read_logs(request):
    contacts = Log.get_log_file()
    return render(request, 'read_logs.html', locals())


def move_files(request):
    Attachment.move_mulitple_files()
    Log.move_mulitple_logs()
    return render(request, 'move_files.html', locals())


def enter_files_into_the_db(request):
    Log.add_mulitple_logs_from_logs_directory()
    Attachment.add_mulitple_files_from_files_directory()
    return render(request, 'add.html', locals())


def readlogs(request):
    contacts = Log.get_log_file()
    return render(request, 'readlogs.html', locals())


def send_rapidpro_data(request):
    message = Message.send_to_rapidpro()
    return render(request, 'sendtorapidpro.html', locals())
