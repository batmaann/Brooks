from django.shortcuts import render

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.generics import GenericAPIView



class RegisterUser(GenericAPIView):
    queryset = models.User

    def post(self, request):
        pass
