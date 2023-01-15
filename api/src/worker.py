import os, sys
import time
from logging import warning
import requests

from celery import Celery
from celery.utils.log import get_task_logger
import time

celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

API_HOST = os.environ.get("API_HOST")
SECRET_KEY = os.environ.get("CHAT_BOT_API_KEY")


@celery.task(name="create_task")
def create_task(tg_id: str, account_id: str, account_type: str, sleep_time: int = 120):
    print("received task... sleeping")

    time.sleep(sleep_time)
    headers = {
        "CHAT_BOT_API_KEY": SECRET_KEY
    }
    data = {
        "account_id": account_id,
        "account_type": account_type,
    }
    requests.post(f"{API_HOST}/users/{tg_id}/update_account", headers=headers, json=data)
    return True
