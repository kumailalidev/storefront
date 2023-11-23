from rest_framework import status

from django.contrib.auth.models import User

from model_bakery import baker

from store.models import Collection

import pytest


@pytest.fixture
def create_collection(api_client):
    def do_create_collection(collection):
        return api_client.post("/store/collections/", collection)

    return do_create_collection


class TestCreateCollection:
    @pytest.mark.django_db
    def test_if_user_is_anonymous_returns_401(self, api_client):
        """
        If the user is not authenticated we should get 401 error.
        """
        response = api_client.post("/store/collections/", {"title": "a"})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client):
        """
        If the authenticated user is not admin we should get 403 error.
        """
        api_client.force_authenticate(user={})
        response = api_client.post("/store/collections/", {"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client):
        """
        If the authenticated user provided data is invalid return HTTP status 400
        """
        api_client.force_authenticate(user=User(is_staff=True))
        response = api_client.post("/store/collections/", {"title": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None

    @pytest.mark.django_db
    def test_if_data_is_valid_returns_201(
        self,
        api_client,
        authenticate,
        create_collection,
    ):
        """
        If the authenticated user provided data is valid return HTTP status 201
        """
        authenticate(is_staff=True)

        response = create_collection({"title": "Collection Name"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0


class TestRetrieveCollection:
    @pytest.mark.django_db
    def test_if_collection_exists_returns_200(self, api_client):
        collection = baker.make(Collection)

        response = api_client.get(f"/store/collections/{collection.id}/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0,
        }
