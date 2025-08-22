import os
from datetime import datetime
from random import randint
from time import sleep

from ai_agent.agent import get_daily_mono_transactions_report
from api.celery import app
from celery import shared_task
from django.conf import settings
from loguru import logger
from telegram.client import TelegramCustomClient

from .models import MonoAccount


@shared_task
def bar():
    return "Hello"


@shared_task
def update_every_mono_account():
    if not settings.SHOULD_AUTO_FETCH_TRANSACTIONS:
        logger.info(
            "skip update_every_mono_account as SHOULD_AUTO_FETCH_TRANSACTIONS turned off"
        )
        return
    accounts = MonoAccount.objects.all()
    logger.info("accounts -> ", accounts)
    for account in accounts:
        logger.info(account)
        account.create_cards_jars()
    logger.info(f"REPORT -> loaded {len(accounts)} account(s)")


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
    random_complete.apply_async(  # pyright: ignore[reportFunctionMemberAccess, reportCallIssue]
        args=(id,),
        retry=True,
        retry_policy={
            "max_retries": 3,
            "interval_start": 0,
            "interval_step": 0.2,
            "interval_max": 0.2,
        },
    )  # pyright: ignore[reportCallIssue]


@shared_task
def send_daily_mono_transactions_report(tg_id: str | int, date: str | None = None):
    """Generate and send daily mono transactions report with coverage status to the specified Telegram chat id."""

    try:
        logger.info(
            f"Generating daily mono transactions report for tg_id: {tg_id}, date: {date}"
        )

        # Generate the report
        report_content = get_daily_mono_transactions_report(date)

        # Send via Telegram
        token = os.environ.get("BOT_TOKEN", "not set bot token")
        client = TelegramCustomClient(token)

        client.send_html_message(str(tg_id), report_content)

        logger.info(
            f"Successfully sent daily mono transactions report to tg_id: {tg_id}"
        )

    except Exception as err:
        logger.error(f"Failed to generate or send daily report: {err}")
        # Send error notification
        try:
            token = os.environ.get("BOT_TOKEN", "not set bot token")
            client = TelegramCustomClient(token)
            client.send_html_message(
                str(tg_id),
                f"<b>❌ Daily Report Error</b>\n\nFailed to generate mono transactions report: {err}",
            )
        except Exception as send_err:
            logger.error(f"Failed to send error notification: {send_err}")
        raise err
