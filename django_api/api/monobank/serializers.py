from .models import Category, MonoAccount, MonoCard
from rest_framework import serializers
from account.serializers import UserSerializer


class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = ["name", "symbol"]
        extra_kwargs = {"user_defined": {"write_only": True}}


class MonoAccountSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonoAccount
        fields = ["user", "mono_token", "active"]

    user = UserSerializer()


class MonoCardSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MonoCard
        fields = [
            "id",
            "send_id",
            "currency_code",
            "cashback_type",
            "balance",
            "credit_limit",
            "masked_pan",
            "type",
            "iban",
        ]
