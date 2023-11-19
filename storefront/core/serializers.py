from djoser.serializers import (
    UserCreateSerializer as BaseUserCreateSerializer,
    UserSerializer as BaseUserSerializer,
)
from rest_framework import serializers


class UserCreateSerializer(BaseUserCreateSerializer):
    # birth_date = serializers.DateField() # Not recommended, This serializer should only deal with creating user only using described in DEFAULT_AUTH_USER model

    class Meta(BaseUserCreateSerializer.Meta):
        fields = [
            "id",
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            # "birth_date",  # not part of DEFAULT_AUTH_USER model.
        ]


class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        ]
