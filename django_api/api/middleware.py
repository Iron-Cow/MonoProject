import logging

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from rest_framework.authentication import BaseAuthentication

logger = logging.getLogger(__file__)
UserModel = get_user_model()

## TODO
class AuthBackend(BaseAuthentication):
    def authenticate(self, request):
        try:
            user_data = request.user_data
        except AttributeError:
            return None

        user, created = UserModel._default_manager.get_or_create(
            **{
                UserModel.USERNAME_FIELD: user_data["username"],
                UserModel.EMAIL_FIELD: user_data["email"],
            }
        )

        if created:
            user = self.configure_user(user)

        return user, None

    @staticmethod
    def configure_user(user):
        view_permissions = Permission.objects.get(codename="end_of_month_report_view")
        view_permissions.user_set.add(user)

        if user.email in settings.ADMINS_EMAILS:
            user.is_staff = True
            user.save()

        return user
