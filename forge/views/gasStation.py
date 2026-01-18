from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from forge import filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class GasStation(ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = models.GasStation.objects.all()
    serializer_class = serializers.GasStation
    filterset_class = filters.GasStation
