from django.apps import AppConfig
from django.db.utils import OperationalError, ProgrammingError


class MonobankConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "monobank"

    def ready(self):
        from django_celery_beat.models import IntervalSchedule, PeriodicTask

        try:
            schedule_accounts_refresh, created = IntervalSchedule.objects.get_or_create(
                every=10,  # Interval period (e.g., every 10 seconds)
                period=IntervalSchedule.MINUTES,
            )

            PeriodicTask.objects.update_or_create(
                defaults={"interval": schedule_accounts_refresh},
                name="Update Every Mono Account Periodic Task",  # Name of the periodic task
                task="monobank.tasks.update_every_mono_account",  # Task reference
            )
        except (OperationalError, ProgrammingError) as err:
            # Exception handling if the database isn't ready yet
            print(err)
