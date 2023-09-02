from django.contrib.auth import get_user_model
from rest_framework import serializers
from utils.errors import MonoBankError

from .models import Category, Currency, MonoAccount, MonoCard, MonoJar, MonoTransaction

User = get_user_model()


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "symbol"]
        extra_kwargs = {"user_defined": {"write_only": True}}


class MonoAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonoAccount
        fields = ["user", "mono_token", "active"]

    def validate(self, data):
        user = User.objects.get(tg_id=data.get("user"))
        mono_token = data.get("mono_token")

        instance = MonoAccount(user=user, mono_token=mono_token)
        try:
            instance.get_cards_jars()
        except MonoBankError as error:
            raise serializers.ValidationError({"non_fields_errors": [error]})
        return data

    def save(self, **kwargs):
        user = User.objects.get(tg_id=self.data.get("user"))
        mono_token = self.data.get("mono_token")

        instance = MonoAccount.objects.create(user=user, mono_token=mono_token)
        instance.create_cards_jars()
        return instance


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        exclude = ["id"]


class MonoCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonoCard
        fields = [
            "id",
            "send_id",
            "currency",
            "cashback_type",
            "balance",
            "credit_limit",
            "masked_pan",
            "type",
            "iban",
        ]

    currency = CurrencySerializer()


class MonoJarSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonoJar
        fields = [
            "id",
            "send_id",
            "title",
            "currency",
            "balance",
            "goal",
        ]

    currency = CurrencySerializer()


class MonoTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonoTransaction
        fields = [
            "id",
            "amount",
            "account_id",
            "currency",
            "comment",
            "balance",
            "category",
            "category_symbol",
            "description",
        ]

    currency = CurrencySerializer()
    category = serializers.SerializerMethodField()
    category_symbol = serializers.SerializerMethodField()

    def get_category(self, obj: MonoTransaction):
        return obj.mcc.category.name

    def get_category_symbol(self, obj: MonoTransaction):
        return obj.mcc.category.symbol
