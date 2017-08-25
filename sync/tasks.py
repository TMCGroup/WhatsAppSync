from __future__ import absolute_import
from .models import Log, Server, Contact, Attachment, Message
from celery import shared_task


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
    Message.send_to_rapidpro()
    return


@shared_task
def call_center_contacts():
    Contact.read_contact_csv()
    return
