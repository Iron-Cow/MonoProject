from django.db import models
from django.contrib.auth import get_user_model
from requests import get
from api.celery import app
from humps import decamelize

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

    def get_cards_jars(self) -> list:
        url = MONO_API_URL + PERSONAL_INFO_PATH
        headers = {"X-Token": self.mono_token}
        user_data = get(url, headers=headers)
        data = user_data.json()
        if data.get("errorDescription"):
            # TODO: add logs / notifying
            raise MonoBankError(data.get("errorDescription"))
        return data

    def create_cards_jars(self, data=None):
        if not data:
            data = self.get_cards_jars()
        cards = data.get("accounts", [])
        for card in cards:
            MonoCard.create_card_from_webhook.apply_async(
                args=(self.user.tg_id, card),
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
        mono_account = MonoAccount.objects.get(user__tg_id=tg_id)
        card_data = decamelize(card_data)
        currency_code = card_data.pop("currency_code")
        try:
            currency = Currency.objects.get(code=int(currency_code))
        except Currency.DoesNotExist:
            currency = Currency.create_unknown_currency(currency_code)
        mono_card = MonoCard.objects.create(
            monoaccount=mono_account, currency=currency, **card_data
        )


class MonoJar(models.Model):
    monoaccount = models.ForeignKey(MonoAccount, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    send_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    # currency_code = models.IntegerField()
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)
    balance = models.IntegerField()
    goal = models.IntegerField()

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
