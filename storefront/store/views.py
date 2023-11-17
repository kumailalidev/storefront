from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view()
def product_list(
    request,
):  # with api_view  decorator applied, the request is instance of Request object comes with Django REST framework
    return Response("OK")


@api_view()
def product_detail(request, id):
    return Response(id)
