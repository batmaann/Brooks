from forge import models
import django_filters


class Vehicle(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = models.Vehicle
        fields = '__all__'


class Refueling(django_filters.FilterSet):
    mileage = django_filters.NumberFilter(field_name='mileage', lookup_expr='icontains')
    odometer = django_filters.NumberFilter(field_name='odometer', lookup_expr='icontains')
    fuel_quantity = django_filters.NumberFilter(field_name='fuel_quantity', lookup_expr='icontains')
    quarter = django_filters.NumberFilter(field_name='quarter', lookup_expr='icontains')

    class Meta:
        model = models.Refueling
        fields = '__all__'


class FuelStatistics(django_filters.FilterSet):
    class Meta:
        model = models.Vehicle
        fields = '__all__'

class GasStation(django_filters.FilterSet):
    class Meta:
        model = models.GasStation
        fields = '__all__'
