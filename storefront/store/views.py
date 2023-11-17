from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


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


@api_view(["GET", "PUT"])
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


@api_view()
def collection_detail(request, pk):
    return Response("OK")
