from rest_framework import serializers
from users import models


class RegisterUser(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(min_length=8)
    phone = serializers.CharField(max_length=20)

    def validate_username(self, value):
        if models.User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Пользователь с таким именем уже есть')
        return value


class LoginUser(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        user = models.User.objects.filter(username=attrs['username']).first()
        if not user or not user.check_password(attrs['password']):
            raise serializers.ValidationError('Неверное имя пользователя или пароль')
        return attrs
