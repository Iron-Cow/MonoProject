import time

from api.celery import app
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from humps import decamelize
from requests import get

# from polymorphic.models import PolymorphicModel
from utils.errors import MonoBankError

DEFAULT_RETRY_POLICY = {
    # 'max_retries': 3,
    # 'interval_start': 0,
    # 'interval_step': 0.2,
    # 'interval_max': 0.2,
}

User = get_user_model()

MONO_API_URL = "https://api.monobank.ua"
PERSONAL_INFO_PATH = "/personal/client-info"
TRANSACTIONS_PATH = "/personal/statement"


class Currency(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=16)
    flag = models.CharField(max_length=4, default=None, null=True, blank=True)
    symbol = models.CharField(max_length=4, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.flag} ({self.code})"

    @staticmethod
    def create_unknown_currency(currency_code: int):
        new_currency = Currency(code=currency_code, name="XXX")
        new_currency.save()
        # TODO: send some notifier
        return new_currency


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True)
    symbol = models.CharField(max_length=4, default=None, blank=True, null=True)
    user_defined = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.symbol or ''}"

    @classmethod
    def create_custom_category(cls, name, symbol="🤝", *args, **kwargs):
        if cls.objects.filter(name=name).exists():
            raise ValueError("Category Exists")
        category = Category(name=name, symbol=symbol, user_defined=True)
        category.save()
        mso = CategoryMSO(category=category, mso=999000 + category.id)
        mso.save()
        return category


class CategoryMSO(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    mso = models.IntegerField(unique=True)

    def __str__(self):
        return f"{self.mso} ({self.category.name})"


class MonoAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mono_token = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)

    # TODO: add for multi-account access
    # family_members = models.ManyToManyField("self", blank=True)

    def __str__(self):
        return f"{self.user.name or self.user.tg_id}"

    class Meta:
        ordering = [
            "-id",
        ]

    def get_cards_jars(self) -> dict:
        url = MONO_API_URL + PERSONAL_INFO_PATH
        headers = {"X-Token": self.mono_token}
        user_data = get(url, headers=headers)
        data = user_data.json()
        if data.get("errorDescription"):
            # TODO: add logs / notifying
            raise MonoBankError(data["errorDescription"])
        return data

    def create_cards_jars(self, data: dict | None = None):
        if not data:
            data = self.get_cards_jars()
        cards = data.get("accounts", [])
        for card in cards:
            MonoCard.create_card_from_webhook.apply_async(
                args=(self.user.tg_id, card, True),
                retry=True,
                retry_policy=DEFAULT_RETRY_POLICY,
            )
        jars = data.get("jars", [])
        for jar in jars:
            MonoJar.create_jar_from_webhook.apply_async(
                args=(self.user.tg_id, jar),
                retry=True,
                retry_policy=DEFAULT_RETRY_POLICY,
            )

    @app.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 60},
    )
    def update_users(self):
        users = MonoAccount.objects.all()
        for user in users:
            print(f"updating {user}")
            user.create_cards_jars()


class MonoCard(models.Model):
    monoaccount = models.ForeignKey(MonoAccount, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    send_id = models.CharField(max_length=255)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    cashback_type = models.CharField(max_length=255)
    balance = models.IntegerField()
    credit_limit = models.IntegerField()
    masked_pan = models.JSONField(null=True, blank=True)
    type = models.CharField(
        max_length=255, choices=[("black", "black"), ("white", "white")]
    )
    iban = models.CharField(max_length=255)

    @property
    def owner_name(self):
        return self.monoaccount.user.name

    def get_transactions(
        self, from_unix: int | None = None, to_unix: int | None = None
    ) -> list:
        # 30 days
        requested_period = 2592000
        if not to_unix:
            to_unix = int(time.time())
        if not from_unix:
            from_unix = to_unix - requested_period

        url = f"{MONO_API_URL}{TRANSACTIONS_PATH}/{self.id}/{from_unix}/{to_unix}"
        headers = {"X-Token": self.monoaccount.mono_token}
        user_data = get(url, headers=headers)

        data = user_data.json()
        if not isinstance(data, list) and data.get("errorDescription"):
            # TODO: add logs / notifying
            raise MonoBankError(data.get("errorDescription"))
        for transaction in data:
            MonoTransaction.create_transaction_from_webhook.apply_async(
                args=(self.id, transaction),
                retry=True,
                retry_policy=DEFAULT_RETRY_POLICY,
            )

        return data

    def __str__(self):
        return f"{self.monoaccount.user.name or self.monoaccount.user.tg_id}-card-{self.type}"

    @app.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 60},
    )
    def create_card_from_webhook(
        self, tg_id: str, card_data: dict, update_transactions: bool = False
    ):
        mono_account = MonoAccount.objects.select_related("user").get(user__tg_id=tg_id)
        card_data = decamelize(card_data)
        currency_code = card_data.pop("currency_code")
        try:
            currency = Currency.objects.get(code=int(currency_code))
        except Currency.DoesNotExist:
            currency = Currency.create_unknown_currency(currency_code)
        try:
            mono_card = MonoCard.objects.get(id=card_data.get("id"))
        except MonoCard.DoesNotExist:
            mono_card, _ = MonoCard.objects.get_or_create(
                monoaccount=mono_account, currency=currency, **card_data
            )
        if update_transactions:
            mono_card.get_transactions()


class MonoJar(models.Model):
    monoaccount = models.ForeignKey(MonoAccount, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    send_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    # currency_code = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.IntegerField()
    goal = models.IntegerField(null=True, blank=True)

    @property
    def owner_name(self):
        return self.monoaccount.user.name

    @app.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 60},
    )
    def create_jar_from_webhook(
        self, tg_id: str, jar_data: dict, update_transactions: bool = False
    ):
        mono_account = MonoAccount.objects.get(user__tg_id=tg_id)

        jar_data = decamelize(jar_data)
        jar_data.pop("description")
        currency_code = jar_data.pop("currency_code")
        try:
            currency = Currency.objects.get(code=int(currency_code))
        except Currency.DoesNotExist:
            currency = Currency.create_unknown_currency(currency_code)
        mono_jar = MonoJar(monoaccount=mono_account, currency=currency, **jar_data)
        mono_jar.save()

    def get_transactions(
        self, from_unix: int | None = None, to_unix: int | None = None
    ) -> list:
        # 30 days
        requested_period = 2592000
        if not to_unix:
            to_unix = int(time.time())
        if not from_unix:
            from_unix = to_unix - requested_period

        url = f"{MONO_API_URL}{TRANSACTIONS_PATH}/{self.id}/{from_unix}/{to_unix}"
        headers = {"X-Token": self.monoaccount.mono_token}
        user_data = get(url, headers=headers)

        data = user_data.json()
        if not isinstance(data, list) and data.get("errorDescription"):
            # TODO: add logs / notifying
            raise MonoBankError(data.get("errorDescription"))
        for transaction in data:
            JarTransaction.create_jar_transaction_from_webhook.apply_async(
                args=(self.id, transaction),
                retry=True,
                retry_policy=DEFAULT_RETRY_POLICY,
            )
            # JarTransaction.create_jar_transaction_from_webhook(self.id, transaction)

        return data


class MonoTransaction(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    time = models.IntegerField()
    description = models.TextField(max_length=2048, blank=True, null=True)
    mcc = models.ForeignKey(
        CategoryMSO, on_delete=models.CASCADE
    )  # connect with category
    original_mcc = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField()
    operation_amount = models.IntegerField(blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    commission_rate = models.IntegerField(blank=True, null=True)
    balance = models.IntegerField()
    hold = models.BooleanField()
    receipt_id = models.CharField(max_length=255)
    account = models.ForeignKey(MonoCard, on_delete=models.CASCADE)
    cashback_amount = models.IntegerField()
    comment = models.TextField(max_length=2048, blank=True, null=True)

    @property
    def owner_name(self):
        return self.account.monoaccount.user.name

    @app.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 60},
    )
    def create_transaction_from_webhook(self, card_id, transaction_data: dict):

        account = MonoCard.objects.get(id=card_id)
        try:
            mso = transaction_data.pop("mcc")
        except KeyError:
            mso_number = len(CategoryMSO.objects.all())
            mso = mso_number
        try:
            mcc = CategoryMSO.objects.get(mso=mso)
        except ObjectDoesNotExist:
            category, _ = Category.objects.get_or_create(name="Інше")
            mcc = CategoryMSO.objects.create(category=category, mso=mso)
        transaction_data = decamelize(transaction_data)
        currency_code = transaction_data.pop("currency_code")
        try:
            currency = Currency.objects.get(code=int(currency_code))
        except Currency.DoesNotExist:
            currency = Currency.create_unknown_currency(currency_code)
        mono_transaction = MonoTransaction.objects.get_or_create(
            account=account,
            mcc=mcc,
            currency=currency,
            **transaction_data,
        )


class JarTransaction(models.Model):
    account = models.ForeignKey(MonoJar, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    time = models.BigIntegerField()
    description = models.TextField(max_length=2048, blank=True, null=True)
    mcc = models.ForeignKey(CategoryMSO, on_delete=models.CASCADE)
    original_mcc = models.IntegerField(blank=True, null=True)
    amount = models.IntegerField()
    operation_amount = models.IntegerField(blank=True, null=True)
    currency = models.ForeignKey(Currency, on_delete=models.SET_NULL, null=True)
    commission_rate = models.IntegerField(blank=True, null=True)
    cashback_amount = models.IntegerField()
    balance = models.IntegerField()
    hold = models.BooleanField()

    @property
    def owner_name(self):
        return self.account.monoaccount.user.name

    @app.task(
        bind=True,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": 5, "countdown": 60},
    )
    def create_jar_transaction_from_webhook(self, card_id, transaction_data: dict):

        account = MonoJar.objects.get(id=card_id)
        try:
            mso = transaction_data.pop("mcc")
        except KeyError:
            mso_number = len(CategoryMSO.objects.all())
            mso = mso_number
        try:
            mcc = CategoryMSO.objects.get(mso=mso)
        except ObjectDoesNotExist:
            category, _ = Category.objects.get_or_create(name="Інше")
            mcc = CategoryMSO.objects.create(category=category, mso=mso)
        transaction_data = decamelize(transaction_data)
        currency_code = transaction_data.pop("currency_code")
        try:
            currency = Currency.objects.get(code=int(currency_code))
        except Currency.DoesNotExist:
            currency = Currency.create_unknown_currency(currency_code)
        mono_transaction = JarTransaction.objects.get_or_create(
            account=account,
            mcc=mcc,
            currency=currency,
            **transaction_data,
        )


@receiver(pre_save)
def pre_save_handler(sender, instance: MonoTransaction, *args, **kwargs):
    if type(instance) is not MonoTransaction:
        return
    # if instance.account_type == "jar":
    #     return
    #     # try:
    #     #     MonoJar.objects.get(id=instance.account_id)
    #     # except MonoJar.DoesNotExist:
    #     #     raise Exception("Jar id is invalid/not found.")
    # elif instance.account_type == "card":
    #     try:
    #         MonoCard.objects.get(id=instance.account_id)
    #     except MonoCard.DoesNotExist:
    #         raise Exception("Card id is invalid/not found.")
