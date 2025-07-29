from datetime import timedelta

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        default = []
        fields = ["tg_id", "password", "name", "family_members"]
        extra_kwargs = {
            "password": {"write_only": True, "min_length": 6},
            "family_members": {"read_only": True},
        }

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


SUPERUSER_LIFETIME = timedelta(days=5)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    # def validate(self, attrs):
    #     data = super().validate(attrs)
    #     refresh = self.get_token(self.user)
    #     access_token = refresh.access_token
    #     access_token.set_exp(lifetime=timedelta(days=2))
    #     data["access"] = str(access_token)
    #
    #     data.update({'is_superuser': self.user.is_superuser})
    #
    #     return data

    def get_token(self, user):  # pyright: ignore[reportIncompatibleMethodOverride]
        token = super(CustomTokenObtainPairSerializer, self).get_token(user)
        token.payload["test_field"] = "test_value"
        return token
