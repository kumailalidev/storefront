from rest_framework import status
from rest_framework.test import APIClient

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
