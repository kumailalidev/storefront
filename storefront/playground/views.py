from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F

from store.models import Product


def say_hello(request):
    # P01-05-05-Retrieving Objects

    # when pk is used instead of id, Django will automatically translate
    # into the name of primary key field. (can be any field)
    # try:
    #     product = Product.objects.get(pk=1)  # returns object not a QuerySet
    # except ObjectDoesNotExist:
    #     pass

    # product = Product.objects.filter(pk=0).first()  # returns None instead of exception
    # product = Product.objects.filter(pk=0).exists()  # returns True if product exists

    # P01-05-06-Filtering Objects

    # queryset = Product.objects.filter(unit_price__gt=20)  # gt is a field lookup type
    # queryset = Product.objects.filter(unit_price__range=(20, 30))
    # queryset = Product.objects.filter(collection__id__range=(1, 2, 3)) # ERROR
    # queryset = Product.objects.filter(title__icontains="coffee")
    # queryset = Product.objects.filter(last_update__year=2021)
    # queryset = Product.objects.filter(last_update__date=2021)
    # queryset = Product.objects.filter(description__isnull=True)

    # P01-05-07-Complex lookups using Q objects

    # queryset = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # Products: inventory < 10 and price < 20

    # can be achieved using chaining filter method
    # queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

    # We can use combine these two condition using OR operator '|' using Q objects.
    # queryset = Product.objects.filter(
    #     Q(inventory__lt=10) | Q(unit_price__lt=20)
    # )  # Products: inventory < 10 OR price < 20

    # queryset = Product.objects.filter(
    #     Q(inventory__lt=10) | ~Q(unit_price__lt=20)
    # )  # Products: inventory < 10 OR price is not < 20

    # P01-05-08-Referencing fields using F objects.

    # F objects are used to reference a particular field.
    # queryset = Product.objects.filter(
    #     inventory=F("unit_price")
    # )  # Products: inventory=price

    # we can also reference field in a related table
    # queryset = Product.objects.filter(
    #     inventory=F("collection__id")
    # )  # Products: inventory=price

    # P01-05-09-Sorting

    # queryset = Product.objects.order_by("title")  # ascending order
    # queryset = Product.objects.order_by("-title")  # descending order
    # queryset = Product.objects.order_by(
    #     "unit_price", "-title"
    # )  # sort products by unit price in ASC order then by title in DESC order.

    # reversing the order of filtering
    # queryset = Product.objects.order_by("unit_price", "-title").reverse()

    # queryset = Product.objects.filter(collection__id=1).order_by("unit_price")

    # NOTE: Change context variable and hello.html template
    # queryset = Product.objects.order_by("unit_price")[
    #     0
    # ] # returns object instead of QuerySet because of slicing operator query will executed.

    # queryset = Product.objects.earliest(
    #     "unit_price"
    # )  # Sorts the product list in ASC order and returns first object
    # queryset = Product.objects.latest(
    #     "unit_price"
    # )  # Sort the product list in DESC order and returns first object

    # P01-05-10-Limiting Results

    # queryset = Product.objects.all()[:5]  # limit query to first 5 products
    queryset = Product.objects.all()[
        5:10
    ]  # limit query to 5 products, skip first 5 products

    return render(
        request,
        "hello.html",
        {
            "name": "Kumail",
            "products": list(queryset),
        },
    )
