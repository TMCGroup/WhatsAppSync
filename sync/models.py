import os
from django.conf import settings
from django.db import models
from django.core.files.storage import default_storage
from dateutil.parser import parse
from datetime import datetime, tzinfo, timedelta
import requests
import glob

url = 'https://hiwa.tmcg.co.ug/handlers/external/received/52c5b798-ee7a-4322-9ea4-9ead3995b2c7/'


class TZ(tzinfo):
    def utcoffset(self, dt): return timedelta(minutes=180)  # Getting timezone offset


class Contact(models.Model):
    number = models.CharField(max_length=15)
    name = models.CharField(max_length=50)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_contact(cls, txt_file):
        contact_count = 0
        for msg_line in default_storage.open(os.path.join(str(txt_file)), 'r'):

            first_appearance = msg_line.find(":")
            second_appearance = msg_line.find(":", first_appearance + 1)
            if not ":" in msg_line[first_appearance + 1:]:
                list_of_msg_line = msg_line.split(",")
                if is_date(list_of_msg_line[0]):
                    Notification.insert_notification(text=msg_line[first_appearance + 5:-1],
                                                     sent_date=msg_line[:first_appearance + 3]).save()
            else:
                list_of_msg_line = msg_line.split(",")
                if is_date(list_of_msg_line[0]):
                    number = msg_line[first_appearance + 5:second_appearance]
                    clean_contact = Contact.correct_contact(number)
                    if Contact.contact_exists(clean_contact):
                        contact = cls.objects.filter(number=clean_contact).first()
                        contact_id = Contact.objects.get(id=contact.id)
                        Message.insert_message(text=msg_line[second_appearance + 1:],
                                               sent_date=msg_line[:first_appearance + 3],
                                               contact=contact_id)
                        contact_count += 1
                    else:
                        clean_contact = Contact.correct_contact(number)
                        contact = cls.objects.create(number=clean_contact, name=clean_contact)
                        contact_id = Contact.objects.get(id=contact.id)
                        Message.insert_message(text=msg_line[second_appearance + 1:],
                                               sent_date=msg_line[:first_appearance + 3], contact=contact_id)
                        contact_count += 1

            Log.objects.filter(log=txt_file).update(synced=True)
        return contact_count

    @classmethod
    def contact_exists(cls, number):
        return cls.objects.filter(number=number).exists()

    @classmethod
    def correct_contact(cls, number):
        if number[0:4] == "M - ":
            clean_contact = number[4:]
            return clean_contact
        else:
            clean_contact = number
            return clean_contact

    def __unicode__(self):
        return self.number


class Message(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.CharField(max_length=30)
    contact = models.ForeignKey(Contact)
    rapidpro_status = models.BooleanField(default=False)

    @classmethod
    def send_to_rapidpro(cls):
        messages = Message.objects.filter(rapidpro_status=False).all()
        sent = 0
        for m in messages:
            sent_date = parse(m.sent_date)
            date_iso = sent_date.isoformat()
            date = date_iso + '.180Z'
            number = m.contact.number
            text = m.text
            data = {'from': number, 'text': text + " " + date_iso, 'date': date}
            requests.post(url, data=data, headers={'context_type': 'application/x-www-form-urlencoded'})
            Message.objects.filter(id=m.id).update(rapidpro_status=True)
            sent += 1

        return sent

    @classmethod
    def insert_message(cls, text, sent_date, contact):
        return cls.objects.create(text=text, sent_date=sent_date, contact=contact)

    def __unicode__(self):
        return self.text


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
    chat_type = models.CharField(max_length=17, choices=CHAT, default='Individual Chat')
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    def __unicode__(self):
        return unicode(self.log)

    @classmethod
    def get_log_file(cls):
        if cls.objects.filter(synced=False).exists():
            txt_file = cls.objects.filter(synced=False).first().log
            Contact.create_contact(txt_file=txt_file)
            return txt_file
        else:
            print("All files synced")

    @classmethod
    def add_mulitple_logs_from_logs_directory(cls):
        path_extensions = ['media/logs/*.txt', 'media/logs/*.jpg', 'media/logs/*.jpeg', 'media/logs/*.gif', ]
        files_added = 0
        for path_extension in path_extensions:
            for filename in glob.iglob(path_extension):
                cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                Log.objects.create(log=cleaned_filename)
                files_added += 1
        return files_added


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False
