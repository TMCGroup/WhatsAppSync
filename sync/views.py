from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Log, Message


def index(request):
    messages = Message.send_to_rapidpro()
    return render(request, 'sync/home.html', {'messages': messages})
