from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth.models import User

import pytest

# NOTE: AAA (Arrange, Act, Assert)


class TestCreateCollection:
    @pytest.mark.django_db  # By default database access is not allowed, Pytest can not create database objects
    # @pytest.mark.skip  # skip test
    def test_if_user_is_anonymous_returns_401(self):
        """
        If the user is not authenticated we should get 401 error.
        """
        # Arrange (prepare for database; arrange objects or put database in initial state)
        # nothing to arrange...

        # Act (behavior we want to test; sending request to server)
        client = APIClient()
        response = client.post("/store/collections/", {"title": "a"})

        # Assert (checking behavior)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self):
        """
        If the authenticated user is not admin we should get 403 error.
        """
        client = APIClient()
        client.force_authenticate(user={})
        response = client.post("/store/collections/", {"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self):
        """
        If the authenticated user provided data is invalid return HTTP status 400
        """
        client = APIClient()
        client.force_authenticate(
            user=User(is_staff=True)
        )  # creates a new user with staff privileges
        response = client.post("/store/collections/", {"title": ""})

        # NOTE: The code still follows "Test should have single assertion/Tests should have
        # sing responsibility" rule because both assertions stills testing the single rule.
        # Both assertions are logically related
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None  # assert if there is an error message

    @pytest.mark.django_db
    def test_if_data_is_valid_returns_201(self):
        """
        If the authenticated user provided data is valid return HTTP status 201
        """
        client = APIClient()
        client.force_authenticate(
            user=User(is_staff=True)
        )  # creates a new user with staff privileges
        response = client.post("/store/collections/", {"title": "Collection Name"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
        # assert response.data["title"] == "Collection Name"
