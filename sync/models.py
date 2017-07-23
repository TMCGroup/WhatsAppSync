import imaplib
import email
import os
from django.conf import settings
from django.db import models
from django.core.files.storage import default_storage
from dateutil.parser import parse


class ServerDetails(models.Model):
    owner = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    host = models.CharField(max_length=100)
    status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now=True)

    @classmethod
    def connect(cls):
        data = cls.objects.filter(status=True).all()
        hosts = []
        for d in data:
            host = imaplib.IMAP4_SSL(d.host)
            host.login(d.user_name, d.password)
            host.select()
            hosts.append(host)
        return hosts

    @classmethod
    def download_attachment(cls, host, emailid):
        resp, data = host.fetch(emailid, "(BODY.PEEK[])")
        email_body = data[0][1]
        mail = email.message_from_string(email_body)
        if mail.get_content_maintype() != 'multipart':
            return
        for part in mail.walk():
            if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
                open( 'media/logs/' + part.get_filename(), 'wb').write(part.get_payload(decode=True))

    @classmethod
    def sync_data(cls):
        hosts = cls.connect()
        if not hosts:
            return 'Not a list'
        else:
            for host in hosts:
                resp, items = host.search(None, "(ALL)")
                items = items[0].split()
                for emailid in items:
                    cls.download_attachment(host=host, emailid=emailid)

    def __unicode__(self):
        return self.owner


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
                    else:
                        clean_contact = Contact.correct_contact(number)
                        contact = cls.objects.create(number=clean_contact, name=clean_contact)
                        contact_id = Contact.objects.get(id=contact.id)
                        Message.insert_message(text=msg_line[second_appearance + 1:],
                                               sent_date=msg_line[:first_appearance + 3],
                                               contact=contact_id)

            Log.objects.filter(log=txt_file).update(synced=True)
            contact_count += 1
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
    chat_type = models.CharField(max_length=17, choices=CHAT)
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


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False
