from django.apps import AppConfig
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


class MonobankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monobank"

    def ready(self):
        if settings.IS_CI_TEST:  # Skip during tests
            return
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
                name=task_name, defaults={"task": task_path}
            )

            # Ensure only the crontab field is set
            periodic_task.interval = (
                None  # Clear the interval field if it was previously set
            )
            periodic_task.crontab = (
                schedule_accounts_refresh  # Assign the crontab schedule
            )
            periodic_task.task = task_path  # Ensure the task path is correctly set
            periodic_task.save()

        except (OperationalError, ProgrammingError) as err:
            # Exception handling if the database isn't ready yet
            print(err)
