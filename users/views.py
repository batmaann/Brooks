from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from users import models
from users import serializers


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
        models.Users.objects.create(user=user)
        token = Token.objects.create(user=user)
        return Response({'token': token.key}, status=201)


class LoginUser(GenericAPIView):
    queryset = models.Users
    serializer_class = serializers.LoginUser

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = Token.objects.get(user__username=serializer.validated_data['username'])
        return Response({'token': token.key})
