from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Currency(models.Model):
    code = models.IntegerField(unique=True)
    name = models.CharField(max_length=16)
    flag = models.CharField(max_length=4, default=None, null=True, blank=True)
    symbol = models.CharField(max_length=4, default=None, null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.flag}"


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


class MonoCard(models.Model):
    monoaccount = models.ForeignKey(MonoAccount, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    send_id = models.CharField(max_length=255)
    currency_code = models.IntegerField()
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


class MonoJar(models.Model):
    monoaccount = models.ForeignKey(MonoAccount, on_delete=models.CASCADE)
    id = models.CharField(max_length=255, primary_key=True)
    send_id = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    currency_code = models.IntegerField()
    balance = models.IntegerField()
    goal = models.IntegerField()
