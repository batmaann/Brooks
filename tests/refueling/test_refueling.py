from decimal import Decimal
from datetime import timedelta

import pytest
from django.apps import apps
from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user.user_permissions.set(perms)
    return user


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def vehicle(user):
    Vehicle = apps.get_model("forge", "Vehicle")
    return Vehicle.objects.create(
        name="Тестовый автомобиль (Toyota Camry)",
        initial_odometer=1000,
        user=user,
    )


@pytest.fixture
def refueling(user, vehicle):
    Refueling = apps.get_model("forge", "Refueling")

    return Refueling.objects.create(
        vehicle=vehicle,
        date=timezone.now().date(),
        mileage=100,
        fuel_quantity=Decimal("45.50"),
        price_per_liter=Decimal("55.30"),
        user=user,
    )


def test_create_refueling(api_client, vehicle, user):
    url = reverse("refueling-list")

    payload = {
        "vehicle": vehicle.id,
        "date": timezone.now().date().isoformat(),
        "mileage": 100,
        "fuel_quantity": "45.50",
        "price_per_liter": "55.30",
    }

    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert isinstance(response.data, dict)
    assert "id" in response.data


def test_refueling_save_sets_user_from_vehicle(vehicle, user):
    Refueling = apps.get_model("forge", "Refueling")

    refueling = Refueling.objects.create(
        vehicle=vehicle,
        date=timezone.now().date(),
        mileage=120,
        fuel_quantity=Decimal("40.00"),
        price_per_liter=Decimal("50.00"),
    )

    assert refueling.user == user


def test_create_refueling_updates_vehicle_current_odometer(api_client, vehicle):
    url = reverse("refueling-list")

    response = api_client.post(
        url,
        data={
            "vehicle": vehicle.id,
            "date": timezone.now().date().isoformat(),
            "mileage": 150,
            "fuel_quantity": "40.00",
            "price_per_liter": "50.00",
        },
        format="json",
    )

    vehicle.refresh_from_db()
    assert response.status_code == 201
    assert vehicle.current_odometer == vehicle.initial_odometer + 150


def test_refueling_odometer_adds_previous_refuelings(vehicle, user):
    Refueling = apps.get_model("forge", "Refueling")
    today = timezone.now().date()

    first = Refueling.objects.create(
        vehicle=vehicle,
        date=today,
        mileage=100,
        fuel_quantity=Decimal("35.00"),
        price_per_liter=Decimal("50.00"),
        user=user,
    )
    second = Refueling.objects.create(
        vehicle=vehicle,
        date=today + timedelta(days=1),
        mileage=200,
        fuel_quantity=Decimal("45.00"),
        price_per_liter=Decimal("52.00"),
        user=user,
    )

    assert first.odometer == 1100
    assert second.odometer == 1300


def test_refueling_calculated_cost_fields(refueling):
    assert refueling.total_cost == Decimal("2516.1500")
    assert refueling.effective_cost == Decimal("2516.1500")
    assert refueling.fuel_consumption == Decimal("45.50")


def test_refueling_effective_cost_subtracts_discount(refueling):
    refueling.discount = Decimal("100.00")

    assert refueling.effective_cost == Decimal("2416.1500")


@pytest.mark.parametrize(
    "field,value",
    [
        ("mileage", -1),
        ("fuel_quantity", Decimal("-1.00")),
        ("price_per_liter", Decimal("-1.00")),
        ("total_cost", Decimal("-1.00")),
        ("discount", Decimal("-1.00")),
    ],
)
def test_refueling_rejects_negative_values(refueling, field, value):
    setattr(refueling, field, value)

    with pytest.raises(ValidationError):
        refueling.full_clean()


def test_vehicle_delete_cascades_refuelings(refueling, vehicle):
    Refueling = apps.get_model("forge", "Refueling")

    vehicle.delete()

    assert Refueling.objects.count() == 0


def test_gas_station_delete_keeps_refueling_and_clears_station(refueling):
    GasStation = apps.get_model("forge", "GasStation")
    gas_station = GasStation.objects.create(
        name="АЗС 1",
        number="10",
        address="Тестовый адрес",
        company="Тестовая компания",
    )
    refueling.gas_station = gas_station
    refueling.save()

    gas_station.delete()

    refueling.refresh_from_db()
    assert refueling.gas_station is None


def test_anonymous_user_cannot_access_refuelings(client):
    url = reverse("refueling-list")

    response = client.get(url, format="json")

    assert response.status_code == 401


def test_user_cannot_create_refueling_for_another_users_vehicle(api_client, django_user_model):
    Vehicle = apps.get_model("forge", "Vehicle")
    other_user = django_user_model.objects.create_user(username="otheruser", password="pass11111111")
    other_vehicle = Vehicle.objects.create(name="Other car", user=other_user)
    url = reverse("refueling-list")

    response = api_client.post(
        url,
        data={
            "vehicle": other_vehicle.id,
            "date": timezone.now().date().isoformat(),
            "mileage": 100,
            "fuel_quantity": "40.00",
            "price_per_liter": "50.00",
        },
        format="json",
    )

    assert response.status_code == 400

# TODO
# Автоподстановка пользователя (user):
# Проверить, что если user не указан при сохранении,
# он автоматически берется из связанного автомобиля (vehicle.user).
#
# Обновление одометра автомобиля (vehicle.current_odometer)
# роверить, что после сохранения заправки current_odometer
# у связанного Vehicle увеличивается на сумму initial_odometer + все mileage
#
#
#
# Тесты для вычисляемого свойства
# Проверить, что для второй и следующих заправок odometer корректно
# суммирует одометр предыдущей заправки и mileage текущей.
#
#
#
# Тесты валидации данных (Validation & Constraints)
# Отрицательные значения:Убедиться, что MinValueValidator(0) выбрасывает
# ValidationError при попытке сохранить отрицательные значения в поля: mileage, fuel_quantity,
# price_per_liter, total_cost, discount.
#
#
#
#
# Тесты связей и метаданных
# Удаление связанных объектов (on_delete):
# Проверить on_delete=models.CASCADE для vehicle: при удалении машины должны удаляться и её заправки.
#
# Проверить on_delete=models.SET_NULL для gas_station: при удалении АЗС запись заправки должна остаться, но поле gas_station должно стать None.
#
#
#
#
#
#
