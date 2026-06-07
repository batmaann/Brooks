from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from forge import filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class Vehicle(ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = serializers.Vehicle
    filterset_class = filters.Vehicle

    def get_queryset(self):
        return models.Vehicle.objects.filter(user=self.request.user)
