from __future__ import absolute_import
from .models import Log, Server, Contact, Attachment, Message, RapidProMessages, Workspace
from celery import shared_task
import datetime
from django.db.models import Q


@shared_task
def downloadattach():
    Server.sync_data()
    return


@shared_task
def move_files():
    Attachment.move_mulitple_files()
    Log.move_mulitple_logs()
    return


@shared_task
def closeconnection():
    Server.close_connection()
    return


@shared_task
def call_center_contacts():
    Contact.read_contact_csv()
    return


@shared_task
def enter_files_into_the_db():
    Log.add_mulitple_logs_from_logs_directory()
    Attachment.add_mulitple_files_from_files_directory()
    return


@shared_task
def readlogs():
    Log.get_log_file()
    return


@shared_task
def send_rapidpro_data():
    Message.send_message_to_rapidpro()
    return


@shared_task
def download_rapidpro_data():
    RapidProMessages.get_rapidpro_messages(Workspace.get_rapidpro_workspaces())
    return


@shared_task
def archive_rapidpro_data():
    d = '2018 3 20'
    date = datetime.datetime.strptime(d, '%Y %m %d')
    msgs = RapidProMessages.objects.filter(Q(modified_on__gte=date) & Q(archived=False)).order_by('id')[:100]
    ls = []
    for msg in msgs:
        ls.append(msg.msg_id)
        RapidProMessages.message_archiver(ls)
    return


@shared_task
def delete_rapidpro_data():
    d = '2018 3 20'
    date = datetime.datetime.strptime(d, '%Y %m %d')
    msgs = RapidProMessages.objects.filter(Q(modified_on__gte=date) & Q(deleted=False)).order_by('id')[:100]
    ls = []
    for msg in msgs:
        ls.append(msg.msg_id)
        RapidProMessages.message_deleter(ls)
    return
