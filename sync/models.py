import imaplib
import email
import shutil
import os
import hashlib
from django.db.models import Q
from WhatsAppSync.envvars import *
import pandas as pd
from django.db import models
from dateutil.parser import parse
from datetime import tzinfo, timedelta, datetime
import requests
import urllib2
import urllib
import datetime
import glob
import json
from temba_client.v2 import TembaClient as Client

import sys

reload(sys)
sys.setdefaultencoding('utf-8')

concepts = ['Symptom', 'Injury - Trauma', 'Infection', 'Environment - Exposure', 'Drug - Chemical']

conceptd = ['Disease - Condition']


def is_date(string):
    try:
        parse(string)
        return True
    except ValueError:
        return False


class TZ(tzinfo):
    def utcoffset(self, dt): return timedelta(minutes=180)  # Getting timezone offset


path_extensions = ['media/downloads/*.jpg', 'media/downloads/*.jpeg', 'media/downloads/*.gif', 'media/downloads/*.pdf',
                   'media/downloads/*.opus', 'media/downloads/*.mp3', 'media/downloads/*.docx', 'media/downloads/*.doc',
                   'media/downloads/*.odt', 'media/downloads/*.ics', 'media/downloads/*.PNG', 'media/downloads/*.aac',
                   'media/downloads/*.vcf', 'media/downloads/*.png', 'media/downloads/*.xlsx', 'media/downloads/*.mp4',
                   'media/downloads/*.opus', ]

path_ext_files = ['media/files/*.jpg', 'media/files/*.jpeg', 'media/files/*.gif', 'media/files/*.pdf',
                  'media/files/*.opus', 'media/files/*.mp3', 'media/files/*.docx', 'media/files/*.doc',
                  'media/files/*.odt', 'media/files/*.ics', 'media/files/*.PNG', 'media/files/*.aac',
                  'media/files/*.vcf', 'media/files/*.png', 'media/files/*.xlsx', 'media/files/*.mp4',
                  'media/files/*.opus', ]


class TZ(tzinfo):
    def utcoffset(self, dt): return timedelta(minutes=180)  # Getting timezone offset


class Server(models.Model):
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
            host.select('Whatsapp')
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
                open('media/downloads/' + str(part.get_filename()), 'wb').write(part.get_payload(decode=True))

    @classmethod
    def sync_data(cls):
        hosts = cls.connect()
        sender_email = 'info@tmcg.co.ug'
        today = datetime.date.today()
        cutoff = today - timedelta(days=30)
        downloads = 0
        if not hosts:
            return 'Not a list'
        else:
            for host in hosts:
                resp, items = host.search(None, 'FROM', sender_email, 'SINCE', cutoff.strftime('%d-%b-%Y'))
                items = items[0].split()
                for emailid in items:
                    cls.download_attachment(host=host, emailid=emailid)
                    downloads += 1
        return downloads

    @classmethod
    def close_connection(cls):
        data = cls.objects.filter(status=True).all()
        for d in data:
            host = imaplib.IMAP4_SSL(d.host)
            host.login(d.user_name, d.password)
            host.select()
            host.logout()
        return

    def __unicode__(self):
        return self.owner


class Workspace(models.Model):
    name = models.CharField(max_length=50)
    host = models.CharField(max_length=50)
    key = models.CharField(max_length=50)
    external_channel_receive_url = models.URLField()
    active_status = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    @classmethod
    def get_workspace(cls):
        return cls.objects.filter(active_status=True).first()

    @classmethod
    def get_rapidpro_workspaces(cls):
        workspace = cls.objects.filter(active_status=True).first()
        client = Client(workspace.host, workspace.key)
        return client


class Contact(models.Model):
    uuid = models.CharField(max_length=100)
    name = models.CharField(max_length=200, null=True)
    number = models.CharField(max_length=200, null=True)
    alt_number = models.CharField(max_length=200, blank=True, null=True)
    created_on = models.DateTimeField(auto_now=True)
    modified_on = models.DateTimeField(auto_now_add=True)

    @classmethod
    def read_contact_csv(cls):
        csv_file = ContactCsv.objects.filter(synced=False).first()
        try:
            df = pd.read_csv('media/' + str(csv_file.csv_log), usecols=[0, 30], header=None, skiprows=1)
            df.dropna(axis=0, how='any')
            dic = dict(zip(df[0], df[30]))
            for key, value in dic.iteritems():
                if ":" not in str(value):
                    uuid = hashlib.md5(str(value)).hexdigest()
                    if cls.contact_exists(uuid=uuid):
                        cls.objects.filter(uuid=uuid).update(name=str(key), alt_number="")
                    else:

                        cls.objects.create(uuid=uuid, name=str(key), number=str(value))
                else:
                    test = str(value).find(":")
                    first = str(value)[:test - 1]
                    second = str(value)[test + 4:]
                    uuid = hashlib.md5(first).hexdigest()
                    if cls.contact_exists(uuid=uuid):
                        cls.objects.filter(uuid=uuid).update(name=str(key), number=first, alt_number=second)
                    elif cls.second_contact_exists(second):
                        cls.objects.filter(alt_number=second).update(name=str(key), number=first)
                    else:
                        cls.objects.create(uuid=uuid, name=str(key), number=first, alt_number=second)
            ContactCsv.objects.filter(csv_log=csv_file).update(synced=True)
            return dic
        except AttributeError:
            return

    @classmethod
    def read_txt_log(cls, txt_file):
        msgs = []

        msg_count = 0

        if str(txt_file.log).count("_") == 3:
            name_concat = str(txt_file.log).split("with", 1)[1][1:].split("_", 2)
            name = name_concat[0] + '_' + name_concat[1]
        else:
            name = str(txt_file.log).split("with", 1)[1][1:].split("_", 1)[0]

        ct_inst = cls.objects.filter(name=name).first()
        if ct_inst is None:
            return
        else:

            with open('media/' + str(txt_file.log)) as txtfile:
                for line_num, line_msg in enumerate(txtfile):

                    # msgs.append(str(line_num) + ' ' + line_msg)

                    first_appearance = line_msg.find(":")
                    if ":" not in line_msg[first_appearance + 1:]:
                        list_of_msg_line = line_msg.split(",", 1)
                        if is_date(list_of_msg_line[0]):
                            Notification.insert_notification(contact=ct_inst, msg_line=line_msg, line=line_num,
                                                             log=txt_file)
                        else:
                            Message.update_continuing_message(ct_inst, line_msg)
                            msg_count += 1

                    else:
                        list_of_msg_line = line_msg.split(",", 1)
                        if is_date(list_of_msg_line[0]):
                            Message.insert_message(client=name, msg_line=line_msg, line=line_num,
                                                   log=txt_file)
                            msg_count += 1

                Log.objects.filter(log=txt_file).update(synced=True)
        return msg_count

    @classmethod
    def contact_exists(cls, uuid):
        return cls.objects.filter(uuid=uuid).exists()

    @classmethod
    def second_contact_exists(cls, number):
        return cls.objects.filter(alt_number=number).exists()

    @classmethod
    def correct_contact(cls, number):
        if number[0:4] == "M - ":
            clean_contact = number[4:]
            return clean_contact
        else:
            clean_contact = number
            return clean_contact

    def __unicode__(self):
        return self.name


class Attachment(models.Model):
    file = models.FileField(upload_to="files", max_length=200)
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    @classmethod
    def get_file(cls, chat_file):
        attached = cls.objects.filter(file=chat_file, synced=False).first()
        return attached

    @classmethod
    def add_mulitple_files_from_files_directory(cls):
        files_added = 0
        for path_extension in path_ext_files:
            for filename in glob.iglob(path_extension):
                cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                if cls.file_exists(cleaned_filename):
                    continue
                else:
                    cls.objects.create(file=cleaned_filename)
                    files_added += 1
        return files_added

    @classmethod
    def move_mulitple_files(cls):
        files_moved = 0
        for path_extension in path_extensions:
            for filename in glob.iglob(path_extension):
                cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                shutil.move(filename, 'media/files/' + cleaned_filename[10:])
                files_moved += 1
        return files_moved

    @classmethod
    def file_exists(cls, chat_file):
        return cls.objects.filter(file=chat_file).exists()

    def __unicode__(self):
        return unicode(self.file)


class Log(models.Model):
    CHAT = (('Group Chat', 'Group Chat'), ('Individual Chat', 'Individual Chat'))
    log = models.FileField(upload_to="logs", max_length=200)
    number_of_lines = models.IntegerField(null=True)
    chat_type = models.CharField(max_length=17, choices=CHAT, default='Individual Chat')
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    @classmethod
    def get_log_file(cls):
        if cls.objects.filter(synced=False).exists():
            txt_files = cls.objects.filter(synced=False).order_by('id')[:100]
            for txt_file in txt_files:
                read = Contact.read_txt_log(txt_file)
            return read

    @classmethod
    def add_mulitple_logs_from_logs_directory(cls):
        txt_extensions = ['media/logs/*.txt', ]
        files_added = 0
        for path_extension in txt_extensions:
            for filename in glob.iglob(path_extension):
                cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                with open(str(filename)) as txtfile:
                    number_of_lines = len(txtfile.readlines())

                if cls.log_exists(cleaned_filename, number_of_lines):
                    continue
                else:
                    cls.objects.create(log=cleaned_filename, number_of_lines=number_of_lines)
                    files_added += 1
        return files_added

    @classmethod
    def move_mulitple_logs(cls):
        txt_extensions = ['media/downloads/*.txt', ]
        files_added = 0

        for path_extension in txt_extensions:
            for filename in glob.iglob(path_extension):
                with open(str(filename)) as txtfile:
                    lines = txtfile.readlines()
                    last_date = cls.last_date(lines)

                if not last_date:
                    return
                else:
                    cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                    filename_split = cleaned_filename.split(".", 1)
                    filename_ext = filename_split[1]
                    new_filename = filename_split[0][1:] + '_' + ''.join(
                        str(last_date).replace('/', '-').replace(', ', '_').replace(':', '')) + '.' + filename_ext
                    shutil.move(filename, 'media/logs/' + new_filename[9:])

                    files_added += 1
        return files_added

    @classmethod
    def last_date(cls, lines):
        for line in lines[::-1]:
            if "-" in line:
                if is_date(line.split("-", 1)[0][:-1]):
                    return line.split("-", 1)[0][:-1]

    @classmethod
    def log_exists(cls, log_file, lines):
        return cls.objects.filter(Q(log__startswith=log_file[:-9]) & Q(number_of_lines=lines)).exists()

    def __unicode__(self):
        return unicode(self.log)


class Message(models.Model):
    rapidpro_id = models.IntegerField(default=False, blank=True)
    uuid = models.CharField(max_length=100)
    contact = models.ForeignKey(Contact)
    text = models.TextField()
    attachment = models.ForeignKey(Attachment, null=True, blank=True)
    log = models.ForeignKey(Log)
    sent_date = models.CharField(max_length=30)
    rapidpro_sent_on = models.DateTimeField(null=True, blank=True)
    rapidpro_status = models.BooleanField(default=False)
    rapidpro_label = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-sent_date',)

    @classmethod
    def insert_message(cls, client, msg_line, line, log):

        first_appearance = msg_line.find(":")
        second_appearance = msg_line.find(":", first_appearance + 1)
        sender_receiver = msg_line[first_appearance:second_appearance].split("-", 1)[1][1:]
        sent_date = msg_line[:first_appearance + 3]
        text = msg_line[second_appearance + 1:]
        if text:
            if sender_receiver == client:
                return cls.save_log_msg(sender=client, text=text, line=line, date=sent_date, log=log)
            else:
                return cls.save_log_msg(sender=client, text="WhatsAppDoc: " + text, line=line, date=sent_date, log=log)
        else:
            return

    @classmethod
    def save_log_msg(cls, sender, text, line, date, log):
        attachment_ext = ['jpg', 'jpeg', 'gif', 'pdf', 'opus', 'mp3', 'docx', 'doc', 'odt', 'ics', 'PNG', 'aac', 'vcf',
                          'png', 'xlsx', 'mp4']
        contact = Contact.objects.filter(name=sender).first()

        if contact is None:
            return
        else:
            uuid = hashlib.md5(str(contact.number) + str(line) + str(date)).hexdigest()
            if cls.message_exists(uuid):
                return
            else:

                if "(file attached)" in text:
                    ext_split = text.split(".", 1)[1].split("(", 1)[0][:-1]
                    if ext_split in attachment_ext:
                        attachment = 'files/' + text[1:-17]
                        attachment_instance = Attachment.objects.filter(file=attachment).first()
                        new_date = cls.second_incrementer(contact, date)
                        if not new_date:
                            return
                        else:
                            cls.objects.create(uuid=uuid, contact=contact, text=text,
                                               attachment=attachment_instance,
                                               log=log, sent_date=new_date)
                            Attachment.objects.filter(file=attachment).update(synced=True)

                else:
                    new_date = cls.second_incrementer(contact, date)
                    if not new_date:
                        return
                    else:
                        try:
                            cls.objects.create(uuid=uuid, contact=contact, text=text, log=log, sent_date=new_date)
                        except ValueError:
                            pass
                    return new_date

    @classmethod
    def second_incrementer(cls, contact, date):
        last_message = ''
        try:
            last_message = Message.objects.filter(contact=contact).latest('id')
        except Exception:
            pass

        if not last_message:
            return str(date) + ':00'
        else:
            last_date = last_message.sent_date
            delimit_ld = last_date.strip().split(":")
            delimit_nd = date.strip().split(":")
            last_sec = int(delimit_ld[2])
            if delimit_ld[1] == delimit_nd[1]:
                if last_sec < 9:
                    new_sec = last_sec + 1
                    return str(date) + ':0' + str(new_sec)
                elif 9 <= last_sec < 59:
                    new_sec = last_sec + 1
                    return str(date) + ':' + str(new_sec)
                elif last_sec < 60:
                    return str(date) + ':01'
            else:
                return str(date) + ':00'

    @classmethod
    def send_message_to_rapidpro(cls):
        messages = Message.objects.filter(rapidpro_status=False).order_by('created_on')
        tmcg_whatsapp_workspace = Workspace.get_workspace()
        external_channel_url = tmcg_whatsapp_workspace.external_channel_receive_url
        sent = 0
        for m in messages:
            sent_date = parse(m.sent_date)
            date_iso = sent_date.isoformat()
            date = date_iso + '.180Z'
            number = m.contact.number
            text = m.text
            data = {'from': number, 'text': text.encode('ascii', 'ignore').decode('ascii') + " " + date_iso,
                    'date': date}
            sent_data = requests.post(url=external_channel_url, data=data,
                                      headers={'context_type': 'application/x-www-form-urlencoded'})
            if sent_data.status_code == requests.codes.ok:
                if sent_data.content[:12] == "SMS Accepted":
                    Message.objects.filter(id=m.id).update(rapidpro_id=sent_data.content[14:], rapidpro_status=True,
                                                           rapidpro_sent_on=datetime.datetime.now())
                    sent += 1
            else:
                return sent_data.content

        return sent

    @classmethod
    def update_continuing_message(cls, contact, msg):
        last_insert = cls.objects.filter(contact=contact).latest('id')
        if not last_insert:
            return
        new_text = last_insert.text + '. ' + msg
        cls.objects.filter(uuid=last_insert.uuid).update(text=new_text)
        return

    @classmethod
    def message_exists(cls, uuid):
        return cls.objects.filter(uuid=uuid).exists()

    @classmethod
    def get_messages_to_label(cls):
        labels = 0
        l = []
        messages = cls.objects.filter(rapidpro_status=True, rapidpro_label=False).order_by('rapidpro_sent_on')[:100]
        for m in messages:
            if m.text[:11] == "WhatsAppDoc":
                continue
            else:
                hn_titles = cls.ccc(message=m)
                l.append(hn_titles)
                if not hn_titles:
                    hn_titles = cls.dx(message=m)
                    l.append(hn_titles)
                else:
                    continue
                labels += 1
        return l

    """
    :param int text: message id
    :param str label: existing label object
    """

    @classmethod
    def ccc(cls, message):
        hn_titles = []
        try:
            urlcc = "https://sandbox.healthnavigatorapis.com/3.0/FindCCC/?freetextchiefcomplaints={0}".format(
                urllib2.quote(message.text))
        except KeyError:
            return Message.objects.filter(rapidpro_id=message.rapidpro_id).update(rapidpro_label=True)
        req = urllib2.Request(urlcc)
        req.add_header("Authorization", "Basic %s" % key_health_nav)
        response = urllib2.urlopen(req)
        try:
            data = json.load(response)
        except ValueError:
            return

        for dd in data:
            if dd["Type"] in concepts:
                hn_titles.append(str(dd["Title"]))
        return hn_titles

    @classmethod
    def dx(cls, message):
        hn_titles = []
        try:
            urldx = "https://sandbox.healthnavigatorapis.com/3.0/FindDx?freetextdx={0}".format(
                urllib2.quote(message.text))
        except KeyError:
            return Message.objects.filter(rapidpro_id=message.rapidpro_id).update(rapidpro_label=True)
        req = urllib2.Request(urldx)
        req.add_header("Authorization", "Basic %s" % key_health_nav)
        response = urllib2.urlopen(req)
        try:
            data = json.load(response)
        except ValueError:
            return
        for dd in data:
            if dd["Type"] in conceptd:
                hn_titles.append(str(dd["Title"]))
        return hn_titles

    @classmethod
    def label_messages(cls, text, labels):
        client = Workspace.get_rapidpro_workspaces()
        for label in labels:
            client.bulk_label_messages(messages=[text], label_name=label)
        Message.objects.filter(rapidpro_id=text).update(rapidpro_label=True)
        return

    def __unicode__(self):
        return self.text


class Notification(models.Model):
    uuid = models.CharField(max_length=100)
    contact = models.ForeignKey(Contact)
    text = models.TextField()
    log = models.ForeignKey(Log)
    sent_date = models.CharField(max_length=30)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now=True)

    @classmethod
    def insert_notification(cls, contact, msg_line, line, log):
        first_appearance = msg_line.find(":")
        contact = contact
        text = msg_line[first_appearance + 5:-1]
        sent_date = msg_line[:first_appearance + 3]

        if contact is None:
            return
        else:
            uuid = hashlib.md5(str(contact.number) + str(line) + str(sent_date)).hexdigest()
            if cls.notification_exists(uuid=uuid):
                return
            else:
                cls.objects.create(uuid=uuid, contact=contact, text=text, log=log, sent_date=sent_date)
        return

    @classmethod
    def notification_exists(cls, uuid):
        return cls.objects.filter(uuid=uuid).exists()

    def __unicode__(self):
        return self.text


class ContactCsv(models.Model):
    csv_log = models.FileField(upload_to="csv")
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)

    @classmethod
    def get_csv_file(cls):
        if cls.objects.filter(synced=False).exists():
            csv_file = cls.objects.filter(synced=False)
            return csv_file
        else:
            print("All files synced")

    @classmethod
    def add_mulitple_logs_from_logs_directory(cls):
        path_extensions = ['media/logs/*.txt', 'media/logs/*.jpg', 'media/logs/*.jpeg', 'media/logs/*.gif',
                           'media/logs/*.pdf', 'media/logs/*.vcf']
        files_added = 0
        for path_extension in path_extensions:
            for filename in glob.iglob(path_extension):
                cleaned_filename = os.path.join(*(filename.split(os.path.sep)[1:]))
                Log.objects.create(log=cleaned_filename)
                files_added += 1
        return files_added

    def __unicode__(self):
        return str(self.csv_log)


class RapidProMessages(models.Model):
    msg_id = models.IntegerField(default=False)
    archived = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    created_on = models.DateTimeField(null=True, blank=False)
    modified_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now=False, auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        ordering = ['-created_on', ]
        get_latest_by = 'modified_on'

    @classmethod
    def get_rapidpro_messages(cls, client):
        added = 0
        folders = ['flows']
        for folder in folders:
            last = cls.objects.filter(msg_id__isnull=False).latest('created_on')
            if not last:
                for message_batch in client.get_messages(folder='flows').iterfetches(retry_on_rate_exceed=True):
                    for message in message_batch:
                        if not cls.message_exists(message):
                            cls.objects.create(msg_id=message.id, created_on=message.created_on,
                                               modified_on=message.modified_on)
                            added += 1

                else:
                    for message_batch in client.get_messages(folder=folder, after=last.created_on).iterfetches(
                            retry_on_rate_exceed=True):
                        for message in message_batch:
                            if not cls.message_exists(message):
                                cls.objects.create(msg_id=message.id, created_on=message.created_on,
                                                   modified_on=message.modified_on)
                                added += 1

        return added

    @classmethod
    def message_exists(cls, message):
        return cls.objects.filter(msg_id=message.id).exists()

    @classmethod
    def message_archiver(cls, ls):
        client = Workspace.get_rapidpro_workspaces()
        try:
            client.bulk_archive_messages(ls)
            for msg in ls:
                cls.objects.filter(msg_id=msg).update(archived=True)
        except Exception:
            pass
        return

    @classmethod
    def message_deleter(cls, ls):
        client = Workspace.get_rapidpro_workspaces()
        try:
            client.bulk_delete_messages(ls)
            for msg in ls:
                cls.objects.filter(msg_id=msg).update(deleted=True)
        except Exception:
            pass
        return ls


class Analytics1(models.Model):
    distinct_user = models.BigIntegerField()
    msg_count = models.BigIntegerField()

    @classmethod
    def get_distinct_users(cls):
        return


class Analytics2(models.Model):
    contact = models.ForeignKey(Contact)
    encounters = models.BigIntegerField()
