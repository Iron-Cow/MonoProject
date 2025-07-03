from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


class MonobankConfig(AppConfig):
    name = "monobank"
    default_auto_field = "django.db.models.BigAutoField"  # type: ignore

    def ready(self):
        if settings.IS_CI_TEST or not settings.IS_WORKER:  # Skip during tests
            return
        if settings.APPLY_MONOBANK_WEBHOOKS:
            from monobank.models import MonoAccount

            MonoAccount.set_monobank_webhook()

        from django_celery_beat.models import (
            CrontabSchedule,
            MultipleObjectsReturned,
            PeriodicTask,
        )

        try:
            schedule_accounts_refresh, created = CrontabSchedule.objects.get_or_create(
                minute=settings.AUTOMATIC_ACCOUNT_REFRESH_MINUTES,  # Run at the 45th minute
                hour="*",  # Every hour
                day_of_week="*",  # Every day of the week
                day_of_month="*",  # Every day of the month
                month_of_year="*",  # Every month
            )
        except MultipleObjectsReturned:
            schedule_accounts_refresh = CrontabSchedule.objects.filter(
                minute=settings.AUTOMATIC_ACCOUNT_REFRESH_MINUTES,  # Run at the 45th minute
                hour="*",  # Every hour
                day_of_week="*",  # Every day of the week
                day_of_month="*",  # Every day of the month
                month_of_year="*",  # Every month
            ).first()
        try:
            # Create or update the periodic task
            task_name = "Update Every Mono Account Periodic Task"
            task_path = "monobank.tasks.update_every_mono_account"
            periodic_task, created = PeriodicTask.objects.get_or_create(
                name=task_name,
                defaults={
                    "task": task_path,
                    "crontab": schedule_accounts_refresh,
                },
            )
            if not created:
                periodic_task.interval = None
                periodic_task.crontab = schedule_accounts_refresh
                periodic_task.task = task_path
                periodic_task.save()

        except (OperationalError, ProgrammingError) as err:
            # Exception handling if the database isn't ready yet
            print(err)
