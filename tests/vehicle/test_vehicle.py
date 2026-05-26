import pytest
from django.apps import apps
from django.contrib.auth.models import Permission
from django.urls import reverse
from rest_framework.test import APIClient
import forge.models

pytestmark = pytest.mark.django_db


@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(username="testuser", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user.user_permissions.set(perms)
    return user


@pytest.fixture
def user2(django_user_model):
    user2 = django_user_model.objects.create_user(username="testuser2", password="pass11111111")
    perms = Permission.objects.filter(content_type__app_label='forge', content_type__model='refueling')
    user2.user_permissions.set(perms)
    return user2


@pytest.fixture
def api_client2(user2):
    client = APIClient()
    client.force_authenticate(user=user2)
    return client


@pytest.fixture
def api_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_create_vehicle(api_client, user):
    url = reverse("vehicle-list")
    payload = {
        "name": "Toyota Camry"
    }

    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    assert response.data["name"] == payload["name"]
    assert forge.models.Vehicle.objects.count() == 1


def test_access_vehicle(api_client, user, api_client2, user2):
    url = reverse("vehicle-list")
    payload = {
        "name": "Toyota Camry"
    }

    response = api_client.post(url, data=payload, format="json")
    response2 = api_client2.get(url,  format="json")

    assert response2.status_code == 401


def test_access_vehicle(api_client, user, api_client2, user2):
    url = reverse("vehicle-list")

    # 1. Первый пользователь создает для себя Toyota Camry
    payload = {"name": "Toyota Camry"}
    response = api_client.post(url, data=payload, format="json")
    assert response.status_code == 201
    created_id = response.data["id"]

    # 2. Первый пользователь проверяет свой список
    # Он ДОЛЖЕН увидеть свою машину
    my_cars_response = api_client.get(url, format="json")
    assert my_cars_response.status_code == 200
    my_car_ids = [car["id"] for car in my_cars_response.data]
    assert created_id in my_car_ids  # Машина на месте!

    # 3. Второй пользователь проверяет свой список
    # Он НЕ ДОЛЖЕН увидеть чужую машину
    other_cars_response = api_client2.get(url, format="json")
    assert other_cars_response.status_code == 200
    other_car_ids = [car["id"] for car in other_cars_response.data]
    assert created_id not in other_car_ids  # Чужой машины здесь нет!

# #TODO
# # Создание транспорта сдалано
# # Получение транспорта необходимым пользователем
# # отказ в доступе получение чужим пользователем
# # отказ в доступе вообще
# # получение доступа к транспорту по айди
# # Изминение траспорта
# # удаление траспорта
#
#
# @pytest.fixture
# def user(django_user_model):
#     user = django_user_model.objects.create_user(username="testuser", password="pass")
#     Task = apps.get_model('background_tasks', 'Task')
#     perms = Permission.objects.filter(content_type__app_label='background_tasks', content_type__model='task')
#     user.user_permissions.set(perms)
#     return user
#
#
# @pytest.fixture
# def api_client(user):
#     client = APIClient()
#     client.force_authenticate(user=user)
#     return client
#
#
# @pytest.fixture
# def task(user):
#     return Task.objects.create(
#         name='Тестовая задача1',
#         func_path="test1",
#     )
#
#
#
# @pytest.fixture
# def tasks_with_users(django_user_model):
#     user1 = django_user_model.objects.create_user(username="user1", password="pass")
#     user2 = django_user_model.objects.create_user(username="user2", password="pass")
#
#     return [
#         Task.objects.create(
#             name="name1",
#             func_path="test1",
#             user=user1
#         ),
#         Task.objects.create(
#             name="name2",
#             func_path="test2",
#             user=user2
#         ),
#     ]
#
# @pytest.fixture
# def single_task(user):
#     user1 = django_user_model.objects.create_user(username="user1", password="pass")
#
#     return Task.objects.create(
#         name="Single Task",
#         func_path="test",
#         user=user
#     )
#
# def test_filter(api_client, tasks_with_users, user):
#     pass
