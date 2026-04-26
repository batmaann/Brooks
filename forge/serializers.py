from django.db import models
from rest_framework import serializers
from forge import models


class Vehicle(serializers.ModelSerializer):
    current_odometer = serializers.IntegerField(read_only=True)

    class Meta:
        model = models.Vehicle
        exclude = ['license_plate']
        read_only_fields = ['current_odometer']


class Refueling(serializers.ModelSerializer):
    odometer = serializers.SerializerMethodField(read_only=True)
    fuel_consumption = serializers.SerializerMethodField(read_only=True)
    effective_cost = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.Refueling
        fields = '__all__'
        read_only_fields = [
            'odometer', 'month', 'quarter', 'created_at', 'updated_at',
            'total_cost', 'fuel_consumption', 'effective_cost'
        ]

    def get_odometer(self, obj):
        """Вычисляемое поле одометра"""
        return obj.odometer

    def get_fuel_consumption(self, obj):
        """Расход топлива на 100 км"""
        return obj.fuel_consumption

    def get_effective_cost(self, obj):
        """Стоимость с учетом скидки"""
        return obj.effective_cost

    def validate(self, data):
        """Валидация последовательности заправок"""
        vehicle = data.get('vehicle')
        date = data.get('date')
        mileage = data.get('mileage')

        if vehicle and date and mileage is not None:
            # Проверяем, что нет заправок с более поздней датой для этого авто
            future_refuels = models.Refueling.objects.filter(
                vehicle=vehicle,
                date__gt=date
            ).exclude(pk=self.instance.pk if self.instance else None).exists()

            if future_refuels and self.instance is None:
                raise serializers.ValidationError({
                    "date": "Нельзя добавить заправку с датой раньше существующих будущих заправок. "
                            "Сначала удалите или отредактируйте более поздние заправки."
                })

            # Проверяем, что пробег не отрицательный
            if mileage < 0:
                raise serializers.ValidationError({
                    "mileage": "Пробег не может быть отрицательным"
                })

            # Проверка минимального пробега
            if mileage == 0:
                raise serializers.ValidationError({
                    "mileage": "Пробег должен быть больше 0"
                })

        return data

    def create(self, validated_data):
        """Создание заправки с автоматическим расчетом total_cost"""
        # Убедимся, что total_cost вычислен если не задан
        fuel_quantity = validated_data.get('fuel_quantity')
        price_per_liter = validated_data.get('price_per_liter')

        if fuel_quantity and price_per_liter and not validated_data.get('total_cost'):
            validated_data['total_cost'] = fuel_quantity * price_per_liter

        return super().create(validated_data)


class FuelStatistics(serializers.ModelSerializer):
    class Meta:
        model = models.FuelStatistics
        fields = '__all__'


class GasStation(serializers.ModelSerializer):
    class Meta:
        model = models.GasStation
        fields = '__all__'