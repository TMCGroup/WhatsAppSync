# WhatsAppSync
WhatsAppSync
This is a project to read and insert whatsapp conversations and contacts into a database.

worker: celery worker -A WhatsAppSync --loglevel=INFO   
run the worker from the root directory of the project

scheduler: celery -A WhatsAppSync beat -l info -S django
run the scheduler from the root of the directory

make sure 'django_celery_beat' is included in your installed apps and then migrate

periodic tasks and crontabs can be added from the database after migration.
