from datetime import date
from decimal import Decimal

import pytest
from django.apps import apps
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='fuelstatistics')
    user.user_permissions.set(perms)
    return user


@pytest.fixture
def other_user(django_user_model):
    return django_user_model.objects.create_user(username="otheruser", password="pass11111111")


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def vehicle(user):
    Vehicle = apps.get_model("forge", "Vehicle")
    return Vehicle.objects.create(name="Toyota Camry", user=user)


@pytest.fixture
def other_vehicle(other_user):
    Vehicle = apps.get_model("forge", "Vehicle")
    return Vehicle.objects.create(name="Other car", user=other_user)


def create_refueling(vehicle, refueling_date, mileage, fuel_quantity, price_per_liter):
    Refueling = apps.get_model("forge", "Refueling")
    return Refueling.objects.create(
        vehicle=vehicle,
        date=refueling_date,
        mileage=mileage,
        fuel_quantity=Decimal(fuel_quantity),
        price_per_liter=Decimal(price_per_liter),
    )


def test_fuel_statistics_returns_monthly_and_yearly_totals(api_client, vehicle, other_vehicle):
    create_refueling(vehicle, date(2026, 1, 10), 100, "10.00", "50.00")
    create_refueling(vehicle, date(2026, 1, 20), 150, "20.00", "55.00")
    create_refueling(vehicle, date(2026, 2, 5), 200, "30.00", "60.00")
    create_refueling(other_vehicle, date(2026, 1, 15), 999, "99.00", "99.00")
    url = reverse("fuelstatistics-list")

    response = api_client.get(url, format="json")

    assert response.status_code == 200
    assert response.data["summary"] == {
        "total_distance": 450,
        "total_cost": "3400.00",
        "total_fuel_liters": "60.00",
    }
    assert response.data["results"] == [
        {
            "period": "2026-02-01",
            "period_type": "month",
            "total_distance": 200,
            "total_cost": "1800.00",
            "total_fuel_liters": "30.00",
        },
        {
            "period": "2026-01-01",
            "period_type": "month",
            "total_distance": 250,
            "total_cost": "1600.00",
            "total_fuel_liters": "30.00",
        },
        {
            "period": "2026-01-01",
            "period_type": "year",
            "total_distance": 450,
            "total_cost": "3400.00",
            "total_fuel_liters": "60.00",
        },
    ]


def test_fuel_statistics_can_filter_by_year(api_client, vehicle):
    create_refueling(vehicle, date(2025, 12, 31), 100, "10.00", "50.00")
    create_refueling(vehicle, date(2026, 1, 1), 200, "20.00", "60.00")
    url = reverse("fuelstatistics-list")

    response = api_client.get(url, {"period_type": "year"}, format="json")

    assert response.status_code == 200
    assert response.data["results"] == [
        {
            "period": "2026-01-01",
            "period_type": "year",
            "total_distance": 200,
            "total_cost": "1200.00",
            "total_fuel_liters": "20.00",
        },
        {
            "period": "2025-01-01",
            "period_type": "year",
            "total_distance": 100,
            "total_cost": "500.00",
            "total_fuel_liters": "10.00",
        },
    ]


def test_fuel_statistics_can_filter_by_vehicle(api_client, vehicle, user):
    Vehicle = apps.get_model("forge", "Vehicle")
    second_vehicle = Vehicle.objects.create(name="Ford Focus", user=user)
    create_refueling(vehicle, date(2026, 1, 10), 100, "10.00", "50.00")
    create_refueling(second_vehicle, date(2026, 1, 20), 300, "30.00", "60.00")
    url = reverse("fuelstatistics-list")

    response = api_client.get(url, {"vehicle": second_vehicle.id, "period_type": "month"}, format="json")

    assert response.status_code == 200
    assert response.data["vehicle_info"] == {
        "id": second_vehicle.id,
        "name": "Ford Focus",
    }
    assert response.data["results"] == [
        {
            "period": "2026-01-01",
            "period_type": "month",
            "total_distance": 300,
            "total_cost": "1800.00",
            "total_fuel_liters": "30.00",
        },
    ]
