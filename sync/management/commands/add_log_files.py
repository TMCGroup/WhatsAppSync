from django.core.management import BaseCommand
from sync.models import Log


class Command(BaseCommand):
    def handle(self, *args, **options):
        added_files = Log.add_mulitple_logs_from_logs_directory()
        self.stdout.write(self.style.SUCCESS('Added %s log files' % added_files))

