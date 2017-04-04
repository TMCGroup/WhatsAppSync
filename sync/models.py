import os
from django.db import models
from django.contrib.auth.models import User
from django.core.files.storage import default_storage


class Contact(models.Model):
    number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.DateTimeField()
    contact = models.ForeignKey(Contact)


class Notification(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.DateTimeField()


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
        # f = default_storage.open(os.path.join(str(txt_file)), 'r')
        # with default_storage.open(os.path.join(str(txt_file)), 'r') as g:
        for g in default_storage.open(os.path.join(str(txt_file)), 'r'):
            # stuff = g.readline()
            data_list.append(g)

        return data_list  # f.readline()

    def upload_log_file(self):
        pass
