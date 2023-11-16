from django.shortcuts import render

from store.models import Product


def say_hello(request):
    query_set = Product.objects.all()  # returns a QuerySet object.
    count = Product.objects.count()  # does not return a query set

    return render(request, "hello.html", {"name": "Kumail"})
