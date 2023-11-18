from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.db.models import Count

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from .models import Product, Collection
from .serializers import ProductSerializer, CollectionSerializer

# P02-02-Building RESTful APIs with Django REST Framework


@api_view(["GET", "POST"])  # HTTP methods supported, GET is supported by default
def product_list(
    request,
):  # with api_view  decorator applied, the request is instance of Request object comes with Django REST framework
    # handle GET request
    if request.method == "GET":
        queryset = Product.objects.select_related(
            "collection"
        ).all()  # select_related will solve lazy loading issue
        serializer = ProductSerializer(
            queryset,
            many=True,
            context={
                "request": request
            },  # context variable used by HyperlinkRelatedField
        )  # converts QuerySet object into dictionary
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = ProductSerializer(
            data=request.data
        )  # deserializing the data into dictionary OrderedDict

        # if serializer.is_valid():
        #     print(type(serializer.validated_data))
        #     return Response("OK")
        # else:
        #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # automatically raise exception
        serializer.is_valid(
            raise_exception=True
        )  # validation rules comes from Model fields.

        # print(serializer.validated_data, " type: ", type(serializer.validated_data))

        serializer.save()  # save to database

        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def product_detail(request: Request, id):
    # try:
    #     product = Product.objects.get(pk=id)
    #     serializer = ProductSerializer(
    #         product
    #     )  # convert the product object into a dictionary
    #     return Response(serializer.data)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)

    # Using get_object_or_404
    product = get_object_or_404(Product, pk=id)

    if request.method == "GET":
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProductSerializer(
            instance=product, data=request.data
        )  # when instance is provided update method of serializer will be executed while saving
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        # if product is present in order item
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product can not be deleted it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
def collection_list(request):
    # handle GET request
    if request.method == "GET":
        queryset = Collection.objects.prefetch_related(
            "product_set"
        ).all()  # fix lazy loading issue

        # OPTIONAL: Annotate queryset with extra column called products_count (requires related_name=products in collection field of Product model)
        # queryset = Collection.objects.annotate(products_counts=Count("products")).all()

        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializer(data=request.data)  # get the data
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)


@api_view(["GET", "PUT", "DELETE"])
def collection_detail(request, pk):
    # get the collection object
    collection = get_object_or_404(Collection, pk=pk)

    # OPTIONAL: Annotate queryset with extra field called products_count (requires related_name=products in collection field of Product model)
    # collection = get_object_or_404(
    #     Collection.objects.annotate(products_counts=Count("products")), pk=pk
    # )

    # handle GET request
    if request.method == "GET":
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    # handle PUT request
    elif request.method == "PUT":
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    # handle DELETE request
    elif request.method == "DELETE":
        # if product is present in order item
        if collection.product_set.count() > 0:
            return Response(
                {
                    "error": "Collection can not be deleted because products are associated with it."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# P02-03-Advanced API Concepts


class ProductList(APIView):  # help us write cleaner code
    # handle GET request
    def get(self, request):
        queryset = Product.objects.select_related("collection").all()
        serializer = ProductSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response(serializer.data)

    # handle POST request
    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    # handle the GET request
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    # handle the PUT request (fully update the object)
    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializer(instance=product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # handle the DELETE request
    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitems.count() > 0:
            return Response(
                {
                    "error": "Product can not be deleted it is associated with an order item."
                },
                status=status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
