from rest_framework import status
from rest_framework.test import APIClient

# NOTE: AAA (Arrange, Act, Assert)


class TestCreateCollection:
    def test_if_user_is_anonymous_returns_401(self):
        """
        If the user is not authenticated we should get 401 error.
        """
        # Arrange
        # nothing to arrange...

        # Act
        client = APIClient()
        response = client.post("/store/collections/", {"title": "a"})

        # Assert (checking behavior)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
