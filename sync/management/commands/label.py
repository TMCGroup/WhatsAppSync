from django.core.management import BaseCommand
from sync.models import Message


class Command(BaseCommand):
    def handle(self, *args, **options):
        sent = Message.label_messagesccdx()
        self.stdout.write(self.style.SUCCESS('Sent %s message(s) to rapidpro' % sent))