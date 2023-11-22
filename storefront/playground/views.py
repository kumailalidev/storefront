from django.db.models import DecimalField
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, F, Value, Func, ExpressionWrapper
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Min, Max, Avg, Sum
from django.contrib.contenttypes.models import ContentType
from django.db import transaction, connection
from django.core.mail import send_mail, mail_admins, BadHeaderError, EmailMessage
from templated_mail.mail import BaseEmailMessage
from django.core.cache import cache  # cache obj.

from store.models import Collection, Customer, Order, OrderItem, Product
from .tasks import notify_customers
from tags.models import TaggedItem

import requests


# def say_hello(request):
#     # P01-05-05-Retrieving Objects

#     # when pk is used instead of id, Django will automatically translate
#     # into the name of primary key field. (can be any field)
#     # try:
#     #     product = Product.objects.get(pk=1)  # returns object not a QuerySet
#     # except ObjectDoesNotExist:
#     #     pass

#     # product = Product.objects.filter(pk=0).first()  # returns None instead of exception
#     # product = Product.objects.filter(pk=0).exists()  # returns True if product exists

#     # P01-05-06-Filtering Objects

#     # queryset = Product.objects.filter(unit_price__gt=20)  # gt is a field lookup type
#     # queryset = Product.objects.filter(unit_price__range=(20, 30))
#     # queryset = Product.objects.filter(collection__id__range=(1, 2, 3)) # ERROR
#     # queryset = Product.objects.filter(title__icontains="coffee")
#     # queryset = Product.objects.filter(last_update__year=2021)
#     # queryset = Product.objects.filter(last_update__date=2021)
#     # queryset = Product.objects.filter(description__isnull=True)

#     # P01-05-07-Complex lookups using Q objects

#     # queryset = Product.objects.filter(inventory__lt=10, unit_price__lt=20) # Products: inventory < 10 and price < 20

#     # can be achieved using chaining filter method
#     # queryset = Product.objects.filter(inventory__lt=10).filter(unit_price__lt=20)

#     # We can use combine these two condition using OR operator '|' using Q objects.
#     # queryset = Product.objects.filter(
#     #     Q(inventory__lt=10) | Q(unit_price__lt=20)
#     # )  # Products: inventory < 10 OR price < 20

#     # queryset = Product.objects.filter(
#     #     Q(inventory__lt=10) | ~Q(unit_price__lt=20)
#     # )  # Products: inventory < 10 OR price is not < 20

#     # P01-05-08-Referencing fields using F objects.

#     # F objects are used to reference a particular field.
#     # queryset = Product.objects.filter(
#     #     inventory=F("unit_price")
#     # )  # Products: inventory=price

#     # we can also reference field in a related table
#     # queryset = Product.objects.filter(
#     #     inventory=F("collection__id")
#     # )  # Products: inventory=price

#     # P01-05-09-Sorting

#     # queryset = Product.objects.order_by("title")  # ascending order
#     # queryset = Product.objects.order_by("-title")  # descending order
#     # queryset = Product.objects.order_by(
#     #     "unit_price", "-title"
#     # )  # sort products by unit price in ASC order then by title in DESC order.

#     # reversing the order of filtering
#     # queryset = Product.objects.order_by("unit_price", "-title").reverse()

#     # queryset = Product.objects.filter(collection__id=1).order_by("unit_price")

#     # NOTE: Change context variable and hello.html template
#     # queryset = Product.objects.order_by("unit_price")[
#     #     0
#     # ] # returns object instead of QuerySet because of slicing operator query will executed.

#     # queryset = Product.objects.earliest(
#     #     "unit_price"
#     # )  # Sorts the product list in ASC order and returns first object
#     # queryset = Product.objects.latest(
#     #     "unit_price"
#     # )  # Sort the product list in DESC order and returns first object

#     # P01-05-10-Limiting Results

#     # queryset = Product.objects.all()[:5]  # limit query to first 5 products
#     # queryset = Product.objects.all()[
#     #     5:10
#     # ]  # limit query to 5 products, skip first 5 products

#     # P01-05-11-Selecting fields to Query

#     # queryset = Product.objects.values(
#     #     "id", "title"
#     # )  # Only return 'id' and 'title' column values

#     # queryset = Product.objects.values(
#     #     "id", "title", "collection__title"
#     # )  # Only return 'id', 'title' and 'title' column of related 'collection' table; Performs INNER JOIN

#     # values method returns QuerySet containing dictionaries instead of objects of Product instance
#     # print(type(queryset))

#     # values_list() method returns tuples instead of dictionaries
#     # queryset = Product.objects.values_list("id", "title", "collection__title")

#     # EXERCISE:
#     # Select products that have been ordered and sort them by title

#     # SOLUTION
#     # queryset = Product.objects.filter(
#     #     id__in=OrderItem.objects.values("product__id").distinct()
#     # ).order_by("title")

#     # P01-05-12-Deferring fields.

#     # only() reads only specified columns, returns objects of model class instead of
#     # dictionaries.
#     # queryset = Product.objects.only(
#     #     "id", "title"
#     # )  # NOTE: can result extra unnecessary queries if unspecified column value is rendered in template. value and value_list dont have this issue.

#     # defer() offloads loading of specified field later.
#     # queryset = Product.objects.defer("description")

#     # P01-05-13-Selecting related objects.

#     # NOTE: NOT RECOMMENDED When rendering related fields values (such as collection) inside
#     # a template
#     # queryset = Product.objects.all()

#     # SOLUTION: use select_related() -> performs INNER JOIN
#     # queryset = Product.objects.select_related("collection").all()

#     # can also select specific field of related table
#     # queryset = Product.objects.select_related("collection__someOtherField").all()

#     # select_related: used when other end of the relationship has only 1 instance
#     #   e.g. product has only one collection
#     #   ForeignKey relationships
#     # prefetch_related: used when other end of the relationship has many (n) instances
#     #   e.g. promotions of the product
#     #   ManyToMany relationships

#     # queryset = Product.objects.prefetch_related("promotions").all()

#     # chaining both
#     # queryset = (
#     #     Product.objects.prefetch_related("promotions")
#     #     .select_related("collection")
#     #     .all()
#     # )

#     # EXERCISE:
#     # Get the last 5 orders with their customer and items (incl product)

#     # SOLUTION # 1 (3 Queries)
#     # queryset = (
#     #     Order.objects.select_related("customer")
#     #     .prefetch_related("orderitem_set__product")
#     #     .order_by("-placed_at")[:5]
#     # )

#     # SOLUTION # 2 (2 queries)
#     # # NOTE: change context variable name to 'order_items'.
#     # queryset = (
#     #     OrderItem.objects.select_related("order")
#     #     .prefetch_related("order__customer")
#     #     .select_related("product")
#     #     .order_by("-order__placed_at")[:5]
#     # )

#     # P01-05-Aggregating Objects

#     # counting objects using aggregation
#     # result = Product.objects.aggregate(Count("id")) # returns dictionary with id__count key.
#     # result = Product.objects.aggregate(
#     #     count=Count("id")
#     # )  # returns dictionary with count key.
#     # result = Product.objects.aggregate(
#     #     count=Count("id"), min_price=Min("unit_price")
#     # )  # returns dictionary with count and min_price key.

#     # using filter and aggregate
#     # result = Product.objects.filter(collection__id=3).aggregate(
#     #     count=Count("id"), min_price=Min("unit_price")
#     # )  # returns dictionary with count and min_price key.

#     # P01-05-14-Annotating objects.

#     # Annotating allows to add new fields to objects when querying them.
#     # NOTE: Only Expression objects are allowed cannot pass boolean values
#     # queryset = Customer.objects.annotate(
#     #     is_new=True
#     # )  # ERROR.

#     # passing Expression object; Value
#     # queryset = Customer.objects.annotate(
#     #     is_new=Value(True)
#     # )  # adds new column 'is_true' to Customer populated by 1 (True)

#     # queryset = Customer.objects.annotate(
#     #     new_id=F("id") + 1
#     # )  # adds new column 'new_id' to Customer populated by id value + 1

#     # P01-05-16-Calling Database Functions.

#     # calling CONCAT function
#     # queryset = Customer.objects.annotate(
#     #     full_name=Func(F("first_name"), Value(" "), F("last_name"), function="CONCAT")
#     # )  # CONCAT function with 3 arguments. Results a new column called 'full_name'

#     # using Django builtin method
#     # queryset = Customer.objects.annotate(
#     #     full_name=Concat("first_name", Value(" "), "last_name")
#     # )

#     # P01-05-17-Grouping Data.

#     # Counting orders placed by customers
#     # queryset = Customer.objects.annotate(
#     #     orders_count=Count("order")
#     # )  #  adds new column 'orders_count' to Customer populated by no. of orders each customer made.

#     # P01-05-18-Working with Expression Wrappers.

#     # creating ExpressionWrapper object to calculate discounted price
#     # discounted_price = ExpressionWrapper(
#     #     F("unit_price") * 0.8, output_field=DecimalField()
#     # )
#     # queryset = Product.objects.annotate(discounted_price=discounted_price)

#     # P01-05-19-Querying Generic Relationships.

#     # getting content type object
#     # content_type = ContentType.objects.get_for_model(Product)

#     # getting tags for Product with id=1
#     # queryset = TaggedItem.objects.select_related("tag").filter(
#     #     content_type=content_type, object_id=1
#     # )

#     # P01-05-20-Custom Managers

#     # using get_tags_for custom manager method to get all tags for product
#     # queryset = TaggedItem.objects.get_tags_for(Product, 1)

#     # P01-05-21-Understanding QuerySet Cache

#     # get all the products QuerySet
#     # queryset = Product.objects.all()

#     # NOTE: the below behavior only happen if the complete queryset is executed first.
#     # Caching depends upon the structure of code.

#     # list(queryset)  # Django will execute the queryset and store into cache
#     # list(queryset)  # this time Django will read results from cache
#     # queryset[0]  #  gets object from cache instead of executing queryset again

#     # queryset[0]  # Django will execute queryset and get the object
#     # list(
#     #     queryset
#     # )  # Django will again execute queryset because previously it wasn't executed completely and cached.

#     # P01-05-22-Creating Objects

#     # creating new collection object

#     # Approach: 01 (Dont execute second time; data already present in db)
#     # collection = Collection()
#     # collection.title = "Video Games"
#     # collection.featured_product = Product(pk=1)
#     # collection.save()

#     # Approach: 02
#     # collection = Collection(title="Video Games", featured_product=Product(pk=1))
#     # collection.save()

#     # Approach: 03 (save method required)
#     # Collection.objects.create(title="Video Games", featured_product=Product(pk=1))
#     # OR
#     # Collection.objects.create(
#     #     title="Video Games", featured_product_id=1
#     # )  # featured_product_id is same as featured_product__id; Django by default save ForeignKey field as id

#     # P01-05-23-Updating Objects

#     # update complete object
#     # collection = Collection(pk=1)
#     # collection.title = "Games"
#     # collection.featured_product = None
#     # collection.save()

#     # update only featured_product
#     # collection = Collection(pk=1)
#     # # collection.title = "" # default behavior of Django; collection.title value does not exits in memory
#     # collection.featured_product = None
#     # collection.save()

#     # proper way of updating object
#     # collection = Collection.objects.get(pk=1) # get object from the database and store it into memory
#     # collection.featured_product = None
#     # collection.save()

#     # directly updating object using update method
#     # Collection.objects.filter(pk=1).update(featured_product=None)

#     # 🔵 P01-05-24-Deleting Objects.

#     # using delete method
#     # collection = Collection(pk=1)
#     # collection.delete()

#     # using filter and delete
#     # Collection.objects.filter(id__gt=5).delete()

#     # 🔵 P01-05-25-Transactions

#     # transaction block
#     # data will be committed to database only if both operations will be successful.
#     # with transaction.atomic():
#     #     # create an order
#     #     order = Order()
#     #     order.id = 1001
#     #     order.customer_id = 1
#     #     order.save()

#     #     # create order item
#     #     item = OrderItem()
#     #     item.id = 10001
#     #     item.order = order
#     #     item.product_id = 1
#     #     item.quantity = 1
#     #     item.unit_price = 10
#     #     item.save()

#     # 🔵 P01-05-26-Executing RAW SQL Queries

#     # raw SQL query
#     # queryset = Product.objects.raw("SELECT * FROM store_product")
#     # queryset = Product.objects.raw("SELECT id, title FROM store_product")

#     # accessing database directly; bypassing the model layer

#     # not recommended
#     # cursor = connection.cursor()
#     # cursor.execute("SELECT * FROM store_product")
#     # cursor.close()

#     # recommend method
#     # with connection.cursor() as cursor:
#     #     cursor.execute("SELECT * FROM store_product")
#     # cursor will close automatically; event there is an exception

#     # executing stored procedures
#     # with connection.cursor() as cursor:
#     #     cursor.callproc(
#     #         # stored procedure goes here...
#     #     )

#     return render(
#         request,
#         "hello.html",
#         {
#             "name": "Kumail",
#             # "orders": list(queryset),
#             # "result": list(queryset),
#             # "tags": list(queryset),
#         },
#     )


# @transaction.atomic
# def say_hello(request):
#     # 🔵 P01-05-25-Transactions

#     # create an order
#     order = Order()
#     order.customer_id = 1
#     order.save()

#     # create order item
#     item = OrderItem()
#     item.order = order
#     item.product_id = 1
#     item.quantity = 1
#     item.unit_price = 10
#     item.save()

#     return render(
#         request,
#         "hello.html",
#         {
#             "name": "Kumail",
#             # "orders": list(queryset),
#             # "result": list(queryset),
#             # "tags": list(queryset),
#         },
#     )

# P03-03-Sending Emails


# def say_hello(request):
#     # NOTE: Make sure smtp4dev is running
#     # docker run --rm -it -p 3000:80 -p 2525:25 rnwood/smtp4dev

#     # P03-03-04-Sending Emails

#     # sending mail
#     # try:
#     #     send_mail(
#     #         "subject",
#     #         "message",
#     #         "from@storefront.com",
#     #         ["admin@storefront.com"],
#     #     )
#     # except BadHeaderError:
#     #     pass

#     # sending mail to admins
#     # try:
#     #     mail_admins(
#     #         "subject",
#     #         "message",
#     #         html_message="message",
#     #     )
#     # except BadHeaderError:
#     #     pass

#     # P03-03-05-Attaching Emails

#     # By default send_mail and mail_admins use EmailMessage class
#     # sending mail using EmailMessage class
#     # try:
#     #     message = EmailMessage(
#     #         "subject",
#     #         "message",
#     #         "from@storefront.com",
#     #         ["admin1@storefront.com"],
#     #     )
#     #     # attaching file
#     #     # message.attach_file("playground/static/images/placeholder.jpg")
#     #     # send message
#     #     message.send()
#     # except BadHeaderError:
#     #     pass

#     # P03-03-06-Sending Templated Emails.
#     # try:
#     #     message = BaseEmailMessage(
#     #         template_name="emails/hello.html", context={"name": "Kumail"}
#     #     )
#     #     message.send(to=["admin1@storefront.com"])
#     # except BadHeaderError:
#     #     pass

#     return render(request, "hello.html", {"name": "Kumail"})

# P03-04-Running background tasks


# def say_hello(request):
#     notify_customers.delay("Hello")
#     return render(request, "hello.html", {"name": "Kumail"})


# P03-07-Caching


def say_hello(request):
    key = "httpbin_result"
    # check if cache data is available, if not add to the cache
    if cache.get(key) is None:
        # Simulating a slow api request, response will be send after 2 seconds of delay
        response = requests.get("https://httpbin.org/delay/2")
        data = response.json()
        cache.set(
            key, data
        )  # can set timeout as optional argument such as 10*60 (10 minutes)
    return render(request, "hello.html", {"name": cache.get(key)})
