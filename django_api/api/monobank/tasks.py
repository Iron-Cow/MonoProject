from celery import shared_task

# from .tasks_data import MonoAccount
from random import randint
from time import sleep
from datetime import datetime
from api.celery import app


@shared_task
def bar():
    return "Hello"


#
#
#
# @shared_task
# def model_operation():
#     return str(MonoAccount.objects.all())
#
# @shared_task
# def model_operation_with_agrs(account_id):
#     return str(MonoAccount.objects.filter(user__tg_id=account_id))


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 7, "countdown": 5},
)
def random_complete(self, id):
    sleep(1)
    result = randint(0, 1)
    result = 0
    print(f"random_complete id -> [{id}] -> {result}")
    if not result:
        # raise self.retry(ex=Exception("test"),countdown=1)
        raise Exception("bad luck")
    return result


@app.task(bind=True)
def create_delayed_task(self):
    id = datetime.now().microsecond
    random_complete.apply_async(
        args=(id,),
        retry=True,
        retry_policy={
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.2,
        },
    )
