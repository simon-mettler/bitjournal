from datetime import timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken

LOGIN = {'email': 'a@example.com', 'password': 'x'}


@pytest.fixture
def client(user):
    return APIClient()


def login(client):
    response = client.post('/api/token/', LOGIN)
    assert response.status_code == 200
    return client.cookies['refresh_token'].value


def refresh_with(cookie):
    other = APIClient()
    other.cookies['refresh_token'] = cookie
    return other.post('/api/token/refresh/')


def test_rotation_issues_new_cookie(client):
    old = login(client)
    response = refresh_with(old)
    assert response.status_code == 200
    assert response.cookies['refresh_token'].value != old


def test_second_refresh_with_same_token_gets_access_only(client):
    old = login(client)
    assert refresh_with(old).status_code == 200
    loser = refresh_with(old)
    assert loser.status_code == 200
    assert 'access' in loser.data
    assert 'refresh_token' not in loser.cookies


def test_leeway_expires(client, settings):
    settings.REFRESH_ROTATION_LEEWAY = timedelta(seconds=60)
    old = login(client)
    assert refresh_with(old).status_code == 200
    BlacklistedToken.objects.update(blacklisted_at=timezone.now() - timedelta(seconds=61))
    assert refresh_with(old).status_code == 401


def test_logged_out_token_is_rejected(client):
    old = login(client)
    client.cookies['refresh_token'] = old
    assert client.post('/api/token/logout/').status_code == 204
    assert refresh_with(old).status_code == 401


def test_missing_cookie_is_401(client):
    assert APIClient().post('/api/token/refresh/').status_code == 401
