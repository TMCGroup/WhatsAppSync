from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Log


def index(request):
    data = Log.get_log_file()
    return render(request, 'index.html', {'data': data})
