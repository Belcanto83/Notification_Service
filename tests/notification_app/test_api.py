import pytest

from rest_framework.test import APIClient
from rest_framework import status
from django.urls import reverse

from model_bakery import baker

from notification_app.models import Client


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def client_factory():
    def factory(*args, **kwargs):
        return baker.make(Client, *args, **kwargs)
    return factory


@pytest.mark.django_db
def test_clients_list(api_client, client_factory):
    # Arrange
    clients = client_factory(_quantity=5)

    # Action
    url = reverse('clients-list')
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    resp_json = response.json()
    assert len(resp_json['results']) == 5
    for ind, client in enumerate(clients):
        assert resp_json['results'][ind]['phone'] == client.phone


@pytest.mark.django_db
def test_clients_retrieve(api_client, client_factory):
    # Arrange
    client = client_factory(_quantity=3)[0]

    # Action
    url = reverse('clients-detail', args=[client.pk])
    response = api_client.get(url)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    resp_json = response.json()
    assert resp_json['phone'] == client.phone


@pytest.mark.django_db
def test_clients_partial_update(api_client, client_factory):
    # Arrange
    client = client_factory(_quantity=1)[0]

    # Action
    url = reverse('clients-detail', args=[client.pk])
    response = api_client.patch(url, data={'phone': 71112223344})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    resp_json = response.json()
    assert resp_json['phone'] == 71112223344
