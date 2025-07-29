from django.conf import settings
from django.contrib.auth import get_user_model

# from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Create admin user"

    def handle(self, *args, **options):
        # try:
        User.objects.create_superuser(
            tg_id=settings.ADMIN_TG_ID,
            password=settings.ADMIN_PASSWORD,
        )  # pyright: ignore[reportCallIssue]

    # except
