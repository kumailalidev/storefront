from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist

from store.models import Product


def say_hello(request):
    # P01-05-05-Retrieving Objects

    # when pk is used instead of id, Django will automatically translate
    # into the name of primary key field. (can be any field)
    # try:
    #     product = Product.objects.get(pk=1)  # returns object not a QuerySet
    # except ObjectDoesNotExist:
    #     pass

    product = Product.objects.filter(pk=0).first()  # returns None instead of exception

    product = Product.objects.filter(pk=0).exists()  # returns True if product exists

    return render(request, "hello.html", {"name": "Kumail"})
