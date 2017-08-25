from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Log, ServerDetail, Contact, Attachment, Message


def downloadattach(request):
    ServerDetails.sync_data()
    return render(request, 'downloadattach.html', locals())


def closeconnection(request):
    ServerDetails.close_connection()
    return render(request, 'close.html', locals())


def move_files(request):
    Attachment.move_mulitple_files()
    Log.move_mulitple_logs()
    return render(request, 'movefiles.html', locals())


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


def call_center_contacts(request):
    contacts = Contact.read_contact_csv()
    return render(request, 'contacts.html', locals())
