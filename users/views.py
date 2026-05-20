from django.shortcuts import render

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.generics import GenericAPIView

from users import models


class RegisterUser(GenericAPIView):
    queryset = models.User

    def post(self, request):

        # 1. Валидация - сериализатор (username, сложный пароль)
        # 2. Создавать пользователя User.objects.create_user()
        # 3. Создать токен
        # 4. Отдать токен
        pass

class LoginrUser(GenericAPIView):
    queryset = users.models.User

    def post(self, request):
        # 1. Валидация - сериализатор (username, пароль)
        # 2. Отдать токен
        pass
