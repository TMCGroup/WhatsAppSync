from django.test import TestCase
from .models import Contact, Message, Log, Notification


class DumbTest(TestCase):
    def test_one_plus_one(self):
        self.assertEquals(1 + 1, 2)


class TestLog(TestCase):
    def setUp(self):
        Log.objects.create(log='media/log/test.txt', chat_type='Individual Chat')

    def test_get_log_file(self):
        unsynced_file = Log.objects.filter(synced=False).first().log
        gotten_log_file = Log.get_log_file()
        self.assertEquals(unsynced_file, gotten_log_file)


class TestNotification(TestCase):
    def test_insert_notification(self):
        initial_notification_count = Notification.objects.count()
        notification_one = Notification.insert_notification(text="+256 XXXXXXX Added to group.",
                                                            sent_date="12/31/16, 19:20")
        notification_count = Notification.objects.count()

        self.assertEquals(Notification.objects.count(), initial_notification_count + notification_count)


class TestMessage(TestCase):
    def setUp(self):
        Contact.objects.create(number="+256XXXXXX", name="Jane Doe")

    def test_insert_message(self):
        contact = Contact.objects.first()
        initial_message_count = Message.objects.count()
        message_one = Message.insert_message(text="Hello there!", sent_date="12/31/16, 19:20", contact=contact)
        message_count = Message.objects.count()

        self.assertEquals(Message.objects.count(), initial_message_count + message_count)


class TestContact(TestCase):
    def setUp(self):
        Contact.objects.create(number="+256XXXXXX", name="Jane Doe")
        Log.objects.create(log='media/log/test.txt', chat_type='Individual Chat')

    def test_contact_exists(self):
        contact = Contact.objects.first()
        contact_two = Contact(number="+256XYXYXY", name="John Doe")
        self.assertEquals(Contact.contact_exists(contact.number), True)
        self.assertEquals(Contact.contact_exists(contact_two.number), False)

    def test_create_contact(self):
        contact_count = Contact.objects.count()
        log_file = Log.get_log_file()
        added_contacts = Contact.create_contact(log_file)
        self.assertEquals(Contact.objects.count(), contact_count + added_contacts)
