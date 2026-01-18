from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from forge import filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated


class Refueling(ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = models.Refueling.objects.all()
    serializer_class = serializers.Refueling
    filterset_class = filters.Refueling
