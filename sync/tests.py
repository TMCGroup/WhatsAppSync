from django.test import TestCase
from .models import Contact, Message, Log, Notification, Workspace
import datetime


class DumbTest(TestCase):
    def test_one_plus_one(self):
        self.assertEquals(1 + 1, 2)


class TestMessage(TestCase):
    def setUp(self):
        log = Log.objects.create(log='media/log/test.txt', chat_type='Individual Chat')
        contact = Contact.objects.create(number="+256XXXXXX", name="Jane Doe")
        Message.objects.create(uuid='test-uuid', contact=contact, text='test-text', log=log,
                               sent_date=datetime.datetime.now())
        Workspace.objects.create(host='test.com', key='test-key',
                                 external_channel_receive_url='https://test.com/external/channel/url')

    def test_send_to_rapidpro(self):
        contact = Contact.objects.first()
        message = Message.objects.first()
        message_count = Message.objects.filter(rapidpro_status=True).count()
        Message.send_message_to_rapidpro()
        sent_message_count = Message.objects.filter(rapidpro_status=True).count()
        self.assertEquals(sent_message_count, message_count + sent_message_count)

## Provide required  new tests as per new implementation

# class TestLog(TestCase):
#     def setUp(self):
#         Log.objects.create(log='media/log/test.txt', chat_type='Individual Chat')
#
#     def test_get_log_file(self):
#         unsynced_file = Log.objects.filter(synced=False).first().log
#         gotten_log_file = Log.get_log_file()
#         self.assertEquals(unsynced_file, gotten_log_file)
#
#
# class TestNotification(TestCase):
#     def test_insert_notification(self):
#         initial_notification_count = Notification.objects.count()
#         notification_one = Notification.insert_notification(text="+256 XXXXXXX Added to group.",
#                                                             sent_date="12/31/16, 19:20")
#         notification_count = Notification.objects.count()
#
#         self.assertEquals(Notification.objects.count(), initial_notification_count + notification_count)


# class TestContact(TestCase):
#     def setUp(self):
#         Contact.objects.create(number="+256XXXXXX", name="Jane Doe")
#         Log.objects.create(log='media/log/test.txt', chat_type='Individual Chat')
#
#     def test_contact_exists(self):
#         contact = Contact.objects.first()
#         contact_two = Contact(number="+256XYXYXY", name="John Doe")
#         self.assertEquals(Contact.contact_exists(contact.number), True)
#         self.assertEquals(Contact.contact_exists(contact_two.number), False)
#
#     def test_create_contact(self):
#         contact_count = Contact.objects.count()
#         log_file = Log.get_log_file()
#         added_contacts = Contact.create_contact(log_file)
#         self.assertEquals(Contact.objects.count(), contact_count + added_contacts)
