# Автоматизированные тесты для микросервиса объявлений

import requests
import pytest

BASE_URL = "https://qa-internship.avito.com/api/1"
SUCCESSFUL_STATUS = "Сохранили объявление - "


@pytest.fixture
def unique_seller_id():
    """Генерация уникального sellerID в диапазоне 111111-999999"""
    import random
    return random.randint(111111, 999999)


@pytest.fixture
def ad_data(unique_seller_id):
    """Фикстура с данными объявления для использования в тестах"""
    return {
        "name": "Телефон",
        "price": 85566,
        "sellerId": unique_seller_id,
        "statistics": {
            "contacts": 32,
            "like": 35,
            "viewCount": 14
        }
    }


@pytest.fixture
def created_ad_id(ad_data):
    """Фикстура, создающая объявление и возвращающая его ID"""
    response = requests.post(f"{BASE_URL}/item", json=ad_data)
    assert response.status_code == 200
    return response.json()["status"].replace(SUCCESSFUL_STATUS, "").strip()


def test_create_ad(ad_data):
    """Тест на успешное создание объявления с корректными данными"""
    response = requests.post(f"{BASE_URL}/item", json=ad_data)
    assert response.status_code == 200
    assert SUCCESSFUL_STATUS in response.json()["status"]


@pytest.mark.parametrize("invalid_data", (
    {"name": ""},  # Пустое название
    {"price": -100},  # Отрицательная цена
    {"sellerId": "abc123"},  # Некорректный ID продавца
    {
        "statistics": {
            "contacts": "много",  # Неверный тип данных
            "like": 10,
            "viewCount": 20
        },
    },
    {
        "statistics": {
            "contacts": 32,
            "like": -10,  # Отрицательное значение
            "viewCount": 50
        },
    },
    {
        "statistics": {
            "contacts": 32,
            "like": -10,
            "viewCount": "none"  # Неверный тип данных
        },
    },
))
def test_create_ad_invalid_data(invalid_data, ad_data):
    """Тест на ошибку при создании объявления с некорректными данными"""
    response = requests.post(f"{BASE_URL}/item", json={
        **ad_data,
        **invalid_data,
    })
    assert response.status_code == 400


def test_get_ad_by_id(created_ad_id):
    """Тест на получение объявления по корректному ID"""
    response = requests.get(f"{BASE_URL}/item/{created_ad_id}")
    assert response.status_code == 200

    data = response.json()[0]
    assert data["id"] == created_ad_id
    assert data["name"] == "Телефон"


def test_get_ad_with_invalid_id():
    """Тест на ошибку при получении объявления с некорректным ID"""
    invalid_ad_id = "invalid-id"
    response = requests.get(f"{BASE_URL}/item/{invalid_ad_id}")
    assert response.status_code == 404


def test_get_ad_with_missing_id():
    """Тест на ошибку при получении объявления с отсутствующим ID"""
    response = requests.get(f"{BASE_URL}/item/")
    assert response.status_code == 404


def test_get_ads_by_seller_id_without_ads(unique_seller_id):
    """Тест на получение всех объявлений по корректному sellerID без созданных объявлений."""
    response = requests.get(f"{BASE_URL}/{unique_seller_id}/item")
    assert response.status_code == 200
    assert not response.json()


def test_get_ads_by_seller_id(created_ad_id, unique_seller_id):
    """Тест на получение всех объявлений по корректному sellerID"""
    response = requests.get(f"{BASE_URL}/{unique_seller_id}/item")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == created_ad_id
    assert data[0]["sellerId"] == unique_seller_id


def test_get_ads_by_invalid_seller_id():
    """Тест на получение всех объявлений по некорректному sellerID"""
    invalid_seller_id = "invalid-seller"
    response = requests.get(f"{BASE_URL}/{invalid_seller_id}/item")

    assert response.status_code == 404
