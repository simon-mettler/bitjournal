"""Shared pytest fixtures. App-specific fixtures live in the app's own conftest.py."""
import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(email='a@example.com', password='x')
