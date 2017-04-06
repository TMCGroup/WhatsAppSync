import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
import re
from django.db import transaction
from datetime import datetime
from dateutil.parser import parse


class Contact(models.Model):
    number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_contact(cls, txt_file):
        for msg_line in default_storage.open(os.path.join(str(txt_file)), 'r'):
            f_appearance = msg_line.find(":")
            s_appearance = msg_line.find(":", f_appearance + 1)
            if not ":" in msg_line[f_appearance+1:]:
                listofmsg_line = msg_line.split(",")
                if is_date(listofmsg_line[0]):
                    Notification(text=msg_line[f_appearance + 5:-1], sent_date=msg_line[:f_appearance + 3]).save()
            else:
                listofmsg_line = msg_line.split(",")
                if is_date(listofmsg_line[0]):
                    number = msg_line[f_appearance+5:s_appearance]
                    contact = cls.objects.create(number=number, name=number)
                    Message.create_msg(text=msg_line[s_appearance + 1:], sent_date=msg_line[:f_appearance + 3],
                                       contact=contact)
                # else:
                #     msg = []
                #     msg.append(listofmsg_line.)
                #     Message.create_msg(text=msg_line[s_appearance + 1:], sent_date=msg_line[:f_appearance + 3],
                #                        contact=contact)

    @classmethod
    def contact_exists(cls, number):
        return cls.objects.filter(number=number).exists()


class Message(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.CharField(max_length=30)
    contact = models.ForeignKey(Contact)

    @classmethod
    def create_msg(cls, text, sent_date, contact):
        return cls.objects.create(text = text, sent_date=sent_date, contact=contact)


class Notification(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.CharField(max_length=30)

    @classmethod
    def insert_notification(cls, text, sent_date):
        return cls.objects.create(text=text, sent_date=sent_date)

    def __unicode__(self):
        return self.text


class Log(models.Model):
    CHAT = (('Group Chat', 'Group Chat'), ('Individual Chat', 'Individual Chat'))

    log = models.FileField(upload_to="logs")
    chat_type = models.CharField(max_length=17, choices=CHAT)
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, related_name='created_by')
    modified_by = models.ForeignKey(User, related_name='modified_by')

    @classmethod
    def read_log_file(cls):
        data_list = []
        txt_file = cls.objects.filter(synced=False).first().log
        Contact.create_contact(txt_file=txt_file)


    def upload_log_file(self):
        pass


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False

