from __future__ import absolute_import
from .models import Log
from celery import shared_task


@shared_task
def call_data():
    Log.get_log_file()
    return

