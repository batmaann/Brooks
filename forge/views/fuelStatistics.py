from decimal import Decimal

from django.db.models import Sum
from django.db.models.functions import TruncMonth, TruncYear
from django.utils.dateparse import parse_date
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .. import filters, models, serializers


class FuelStatistics(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    permission_classes = (IsAuthenticated,)
    queryset = models.FuelStatistics.objects.all()
    serializer_class = serializers.FuelStatistics
    filterset_class = filters.FuelStatistics

    def get_queryset(self):
        return models.FuelStatistics.objects.filter(vehicle__user=self.request.user)

    def list(self, request):
        refuelings = models.Refueling.objects.filter(vehicle__user=request.user)
        vehicle_info = self._get_vehicle_info(request)
        if vehicle_info:
            refuelings = refuelings.filter(vehicle_id=vehicle_info["id"])
        elif request.query_params.get("vehicle"):
            refuelings = refuelings.none()

        period_from = parse_date(request.query_params.get("period_from", ""))
        period_to = parse_date(request.query_params.get("period_to", ""))
        if period_from:
            refuelings = refuelings.filter(date__gte=period_from)
        if period_to:
            refuelings = refuelings.filter(date__lte=period_to)

        period_type = request.query_params.get("period_type")
        period_types = [period_type] if period_type in {"month", "year"} else ["month", "year"]

        results = []
        for current_period_type in period_types:
            results.extend(self._build_period_results(refuelings, current_period_type))

        response_data = {
            "results": results,
            "summary": self._build_summary(refuelings),
        }
        if vehicle_info:
            response_data["vehicle_info"] = vehicle_info

        return Response(response_data)

    def _get_vehicle_info(self, request):
        vehicle_id = request.query_params.get("vehicle")
        if not vehicle_id:
            return None

        try:
            vehicle = models.Vehicle.objects.get(id=vehicle_id, user=request.user)
        except (models.Vehicle.DoesNotExist, ValueError):
            return None

        return {
            "id": vehicle.id,
            "name": vehicle.name,
        }

    def _build_period_results(self, refuelings, period_type):
        trunc_func = TruncMonth if period_type == "month" else TruncYear
        statistics = (
            refuelings.annotate(period=trunc_func("date"))
            .values("period")
            .annotate(
                total_distance=Sum("mileage"),
                total_cost=Sum("total_cost"),
                total_fuel_liters=Sum("fuel_quantity"),
            )
            .order_by("-period")
        )

        return [
            {
                "period": self._format_period(row["period"]),
                "period_type": period_type,
                "total_distance": row["total_distance"] or 0,
                "total_cost": self._format_decimal(row["total_cost"]),
                "total_fuel_liters": self._format_decimal(row["total_fuel_liters"]),
            }
            for row in statistics
        ]

    def _build_summary(self, refuelings):
        summary = refuelings.aggregate(
            total_distance=Sum("mileage"),
            total_cost=Sum("total_cost"),
            total_fuel_liters=Sum("fuel_quantity"),
        )
        return {
            "total_distance": summary["total_distance"] or 0,
            "total_cost": self._format_decimal(summary["total_cost"]),
            "total_fuel_liters": self._format_decimal(summary["total_fuel_liters"]),
        }

    def _format_period(self, value):
        if hasattr(value, "date"):
            value = value.date()
        return value.isoformat()

    def _format_decimal(self, value):
        value = value or Decimal("0")
        return str(value.quantize(Decimal("0.01")))
