from .models import Category, MonoAccount
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
