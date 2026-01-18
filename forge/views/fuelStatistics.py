from forge import models, serializers
from rest_framework.viewsets import ModelViewSet
from forge import filters
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication

from forge import models, serializers


from datetime import date
from django.db.models import Sum, Avg
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated

from forge import models

class FuelStatistics(ViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    def list(self, request):
        today = date.today()
        queryset = models.Refueling.objects.filter(
            date__year=today.year,
            date__month=today.month
        )
        vehicle_id = request.query_params.get('vehicle')
        if vehicle_id:
            queryset = queryset.filter(vehicle_id=vehicle_id)

        stats = queryset.aggregate(
            total_distance=Sum('mileage'),
            total_fuel=Sum('fuel_quantity'),
            total_cost=Sum('total_cost'),
            avg_price=Avg('price_per_liter'),
        )
        avg_consumption = 0
        if stats['total_distance']:
            avg_consumption = (
                stats['total_fuel'] / stats['total_distance']
            ) * 100

        return Response({
            "period": f"{today.year}-{today.month:02d}",
            "vehicle": vehicle_id,
            "total_distance_km": stats['total_distance'] or 0,
            "total_fuel_liters": stats['total_fuel'] or 0,
            "total_cost": stats['total_cost'] or 0,
            "avg_price_per_liter": stats['avg_price'] or 0,
            "avg_consumption_l_100km": round(avg_consumption, 2),
        })

class FuelStatisticsViewSet(ReadOnlyModelViewSet):
    """
    Статистика расхода топлива по автомобилю
    """
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)

    queryset = models.FuelStatistics.objects.all()
    serializer_class = serializers.FuelStatistics