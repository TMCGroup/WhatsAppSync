from django.db import models


class Contact(models.Model):
    number = models.CharField(max_length=15)
    created_on = models.DateTimeField(auto_now_add=True)
    modified_on = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    created_on = models.DateTimeField(auto_now_add=True)
    modifies_on = models.DateTimeField(auto_now=True)
    text = models.TextField()
    sent_date = models.DateTimeField()
    contact = models.ForeignKey(Contact)


class Log(models.Model):
    log = models.FileField(upload_to="logs")
    created_on = models.DateTimeField(auto_now_add=True)
    synced = models.BooleanField(default=False)
