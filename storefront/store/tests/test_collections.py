from rest_framework import status
from rest_framework.test import APIClient

from django.contrib.auth.models import User

from model_bakery import baker

from store.models import Collection, Product

import pytest

# NOTE: AAA (Arrange, Act, Assert)


@pytest.fixture
def create_collection(
    api_client,
):  # NOTE: if we pass collection here pytest will think it is a fixture (define in conftest.py) because of decorator. Therefore we create an inner function and pass collection dictionary there
    def do_create_collection(collection):  # 'closure' concept is applied here
        return api_client.post("/store/collections/", collection)  # returns response

    return do_create_collection  # return function reference


class TestCreateCollection:
    @pytest.mark.django_db  # By default database access is not allowed, Pytest can not create database objects
    # @pytest.mark.skip  # skip test
    def test_if_user_is_anonymous_returns_401(self, api_client):
        """
        If the user is not authenticated we should get 401 error.
        """
        # Arrange (prepare for database; arrange objects or put database in initial state)
        # nothing to arrange...

        # Act (behavior we want to test; sending request to server)
        # client = APIClient() # no longer needed, defined in conftest.py
        response = api_client.post("/store/collections/", {"title": "a"})

        # Assert (checking behavior)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_admin_returns_403(self, api_client):
        """
        If the authenticated user is not admin we should get 403 error.
        """
        # NOTE: Make sure FIRST authenticate then create a collection.

        # client = APIClient() # no longer needed, defined in conftest.py
        api_client.force_authenticate(user={})
        response = api_client.post("/store/collections/", {"title": "a"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_data_is_invalid_returns_400(self, api_client):
        """
        If the authenticated user provided data is invalid return HTTP status 400
        """
        # client = APIClient() # no longer needed, defined in conftest.py
        api_client.force_authenticate(
            user=User(is_staff=True)
        )  # creates a new user with staff privileges
        response = api_client.post("/store/collections/", {"title": ""})

        # NOTE: The code still follows "Test should have single assertion/Tests should have
        # sing responsibility" rule because both assertions stills testing the single rule.
        # Both assertions are logically related
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["title"] is not None  # assert if there is an error message

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
        # client = APIClient() # no longer needed, defined in conftest.py

        # api_client.force_authenticate(
        #     user=User(is_staff=True)
        # )  # creates a new user with staff privileges

        # authenticate as staff user using fixture (ARRANGE)
        authenticate(is_staff=True)

        # using fixture to create collection and getting response object (ACT)
        response = create_collection({"title": "Collection Name"})

        # (ASSERT)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["id"] > 0
        # assert response.data["title"] == "Collection Name"


class TestRetrieveCollection:
    @pytest.mark.django_db
    def test_if_collection_exists_returns_200(self, api_client):
        # Arrange
        # creating collection using model_bakery package
        collection = baker.make(Collection)

        # product = baker.make(Product) # automatically create related object 'collection'
        # baker.make(
        #     Product, collection=collection, _quantity=10
        # )  # all the 10 products belongs to same collection

        # MAKE SURE TO ADD '/' at the end, otherwise test will fail
        response = api_client.get(
            f"/store/collections/{collection.id}/"
        )  # DJANGO ALWAYS TERMINATES URLS WITH /, if missing in end it will automatically redirects to <url>/ with status_code 301.

        assert response.status_code == status.HTTP_200_OK
        # assert response.data["id"] == collection.id
        # assert response.data["title"] == collection.title
        assert response.data == {
            "id": collection.id,
            "title": collection.title,
            "products_count": 0,
        }
