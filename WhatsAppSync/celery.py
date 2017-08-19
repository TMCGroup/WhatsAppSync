from __future__ import absolute_import
import os
from celery import Celery


# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WhatsAppSync.settings')

app = Celery('tasks')


# Using a string here means the worker don't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')


# Load task modules from all registered Django app configs.
# app.autodiscover_tasks(force=True)
app.autodiscover_tasks()

app = Celery('tasks',
             broker='amqp://myuser:mypassword@localhost:5672/myvhost',
             backend='rpc://',
             include=['sync.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()


