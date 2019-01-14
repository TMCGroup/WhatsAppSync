
# WhatsAppSync
WhatsAppSync is a TMCG Project used for reading and inserting WhatsApp conversations and contacts into a database and
sending these messages to its RapidPro instance.

## Features
* Reading WhatsApp logs and inserting the contents into the database.
* Sending the messages to RapidPro


## Prerequisite
* Make sure you have rabbitmq-server installed globally.


## Installation
```
#clone the project.
git clone (project-link)

#Install requirements.
pip install requirements.pip

#Migrate migrations
python manage.py migrate

#Run django server
python manage.py runserver

#Run the worker.
 celery worker -A WhatsAppSync --loglevel=INFO

#Run the scheduler.
celery -A WhatsAppSync beat -l info -S django

 ```
 [For more info on periodic tasks](http://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html)


 ## Usage

* Create superuser `python manage.py createsuperuser` and login via django admin
* Add Workspace, this is to provide the external channel receiving url which has its own workspace to prevent
conflicts with the other channels in other workspaces.
* Add Intervals and Crontabs for when periodic tasks should run.