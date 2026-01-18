from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from django.db.models import Sum
from .. import models, serializers, filters


class FuelStatistics(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = models.FuelStatistics.objects.all()
    serializer_class = serializers.FuelStatistics
    filterset_class = filters.FuelStatistics

    def list(self, request):
        vehicle_id = request.query_params.get('vehicle')
        vehicle_name = None
        total_refueling_cost = 0
        total_refueling_fuel = 0
        if vehicle_id:
            try:
                vehicle = models.Vehicle.objects.get(id=vehicle_id)
                vehicle_name = vehicle.name

                refueling_stats = models.Refueling.objects.filter(
                    vehicle_id=vehicle_id
                ).aggregate(
                    total_cost=Sum('total_cost'),
                    total_fuel=Sum('fuel_quantity')
                )

                total_refueling_cost = refueling_stats['total_cost'] or 0
                total_refueling_fuel = refueling_stats['total_fuel'] or 0
            except (models.Vehicle.DoesNotExist, ValueError):
                vehicle_name = None
                total_refueling_cost = 0
                total_refueling_fuel = 0

        # Применяем фильтры и получаем данные из FuelStatistics
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data

        # Создаем ответ
        response_data = {
            'results': data
        }
        if vehicle_name:
            response_data['vehicle_info'] = {
                'id': vehicle_id,
                'name': vehicle_name
            }
            response_data['refueling_totals'] = {
                'total_cost': float(total_refueling_cost),
                'total_fuel_liters': float(total_refueling_fuel),
                'average_price_per_liter': float(
                    total_refueling_cost / total_refueling_fuel) if total_refueling_fuel > 0 else 0
            }

        return Response(response_data)
