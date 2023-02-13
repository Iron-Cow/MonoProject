# celery.py
from __future__ import absolute_import
import os
from celery import Celery

# this code copied from manage.py
# set the default Django settings module for the 'celery' app.
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")

# you change change the name here
app = Celery("api")

# read config from Django settings, the CELERY namespace would make celery
# config keys has `CELERY` prefix
app.config_from_object("django.conf:settings", namespace="CELERY")

# load tasks.py in django apps
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# CELERY_BROKER_URL=redis://redis:6379/0
# CELERY_RESULT_BACKEND=redis://redis:6379/0


@app.task
def add(x, y):
    return x / y


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return f"Request: {self.request!r}"


# app.conf.beat_schedule = {
#     "run-me-every-ten-seconds": {
#         "task": "django_celery_example.celery.debug_task",
#         "schedule": 10.0
#     }
# }
