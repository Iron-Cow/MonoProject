from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(
        self,
        tg_id: int or str,
        password=None,
        is_staff=False,
        is_admin=False,
    ):
        if not tg_id:
            raise ValueError("User must have a telegram account")
        if not password:
            raise ValueError("User must have a password")

        user_obj = self.model(tg_id=tg_id)
        user_obj.set_password(password)
        user_obj.staff = is_staff
        user_obj.admin = is_admin
        user_obj.name = f"User-{tg_id}"
        user_obj.save(using=self._db)
        return user_obj

    def create_staffuser(self, tg_id, password=None):
        user = self.create_user(tg_id, password=password, is_staff=True)
        return user

    def create_superuser(self, tg_id, password=None):
        user = self.create_user(tg_id, password=password, is_staff=True, is_admin=True)
        return user

    def get_or_create_user(
        self, tg_id: int or str, password=None, is_staff=False, is_admin=False
    ):
        try:
            return self.create_user(tg_id, password, is_staff, is_admin)
        except:
            self.get_by_natural_key(tg_id)
            if self.objects.get(tg_id=tg_id).exists():
                return self.objects.get(tg_id=tg_id)


class User(AbstractBaseUser):

    tg_id = models.CharField(max_length=255, unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)

    USERNAME_FIELD = "tg_id"
    # REQUIRED_FIELDS = ['telegram_id']
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_active(self):
        return self.active

    @property
    def is_staff(self):
        return self.staff

    @property
    def is_superuser(self):
        return self.admin

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True

    def get_name(self):
        return self.name

    def get_telegram_id(self):
        return self.telegram_id
