from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer


@api_view()
def product_list(
    request,
):  # with api_view  decorator applied, the request is instance of Request object comes with Django REST framework
    queryset = Product.objects.select_related(
        "collection"
    ).all()  # select_related will solve lazy loading issue
    serializer = ProductSerializer(
        queryset,
        many=True,
        context={"request": request},  # context variable used by HyperlinkRelatedField
    )  # converts QuerySet object into dictionary
    return Response(serializer.data)


@api_view()
def product_detail(request, id):
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
    serializer = ProductSerializer(product)
    return Response(serializer.data)


@api_view()
def collection_detail(request, pk):
    return Response("OK")
