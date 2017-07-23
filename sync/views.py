from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
from .models import Log, ServerDetails


def index(request):
     ServerDetails.sync_data()

