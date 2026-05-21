from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.generics import GenericAPIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.utils.timezone import now
from django.contrib.auth.models import AbstractUser
from users import models
from users import serializers
from django.contrib.auth.models import User


class RegisterUser(GenericAPIView):
    queryset = models.User
    serializer_class = serializers.RegisterUser

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = models.User.objects.create_user(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password'],
        )
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=201)


class LoginUser(GenericAPIView):
    queryset = models.Users
    serializer_class = serializers.LoginUser

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # token = Token.objects.get(user__username=serializer,validate_data['login'])
        token = Token.objects.get(user__username=serializer.validated_data['login'])

        return Response({'token': token.key})



        pass
