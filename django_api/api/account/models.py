# pyright: reportArgumentType = false

# Create your models here.

from typing import Iterable, Set

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(
        self,
        tg_id: str | int,
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
        self, tg_id: str | int, password=None, is_staff=False, is_admin=False
    ):
        try:
            return self.create_user(tg_id, password, is_staff, is_admin)
        except:
            self.get_by_natural_key(str(tg_id))
            if self.objects.get(tg_id=tg_id).exists():
                return self.objects.get(tg_id=tg_id)


class User(AbstractBaseUser):
    tg_id = models.CharField(max_length=255, unique=True, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    family_members = models.ManyToManyField(
        "self", symmetrical=True, related_name="family_members", blank=True, null=True
    )

    USERNAME_FIELD = "tg_id"
    # REQUIRED_FIELDS = ['telegram_id']
    REQUIRED_FIELDS = []
    objects = UserManager()

    @property
    def is_active(self):  # pyright: ignore[reportIncompatibleVariableOverride]
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
        return self.tg_id

    @classmethod
    def expand_tg_ids_with_family(
        cls, tg_ids: Iterable[str | int], recursive: bool = False
    ) -> list[str]:
        """
        Expand a collection of tg_ids to include their family members.

        - If recursive=True, includes the full connected family component.
        - If recursive=False, includes only direct family members.
        Returns unique tg_ids as strings.
        """
        initial_ids: Set[str] = {str(tid) for tid in tg_ids if tid is not None}
        if not initial_ids:
            return []

        collected_ids: Set[str] = set()

        if not recursive:
            users = cls.objects.filter(tg_id__in=initial_ids).prefetch_related(
                "family_members"
            )
            for user in users:
                collected_ids.add(str(user.tg_id))
                for member in user.family_members.all():
                    collected_ids.add(str(member.tg_id))
            return list(collected_ids)

        # recursive traversal over the undirected family graph
        to_visit: list[str] = list(initial_ids)
        while to_visit:
            batch = to_visit[:50]
            to_visit = to_visit[50:]

            users = cls.objects.filter(tg_id__in=batch).prefetch_related(
                "family_members"
            )
            for user in users:
                user_id = str(user.tg_id)
                if user_id in collected_ids:
                    continue
                collected_ids.add(user_id)
                for member in user.family_members.all():
                    member_id = str(member.tg_id)
                    if member_id not in collected_ids:
                        to_visit.append(member_id)

        return list(collected_ids)

    def get_related_tg_ids(
        self, include_self: bool = True, recursive: bool = False
    ) -> list[str]:
        """
        Return this user's tg_id plus family members' tg_ids.
        - recursive=False: direct family only
        - recursive=True: full connected family component
        """
        base_ids: list[str] = [str(self.tg_id)] if include_self else []
        if recursive:
            return self.__class__.expand_tg_ids_with_family(base_ids, recursive=True)

        # Optimize direct family lookup with values_list
        ids: Set[str] = set(base_ids)
        family_tg_ids = self.family_members.values_list("tg_id", flat=True)
        ids.update(str(tg_id) for tg_id in family_tg_ids)
        return list(ids)
