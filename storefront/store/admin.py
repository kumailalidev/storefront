from django.contrib import admin
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_per_page = 10
    list_select_related = [
        "collection"
    ]  # eager load collection table fields for optimization.

    def collection_title(self, product):
        return product.collection.title

    # custom computed column
    @admin.display(ordering="inventory")  # enable sorting by inventory
    def inventory_status(self, product):
        if product.inventory < 10:
            return "Low"
        return "OK"


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["first_name", "last_name", "membership", "orders"]
    list_editable = ["membership"]
    ordering = ["first_name", "last_name"]
    list_per_page = 10
    search_fields = ["first_name__istartswith", "last_name__istartswith"]

    @admin.display(ordering="orders")  # order by 'orders' field
    def orders(self, customer):
        url = (
            reverse("admin:store_order_changelist")
            + "?"
            + urlencode({"customer__id": str(customer.id)})
        )
        return format_html("<a href='{}'>{} Orders</a>", url, customer.orders)

    # overriding the base queryset of Customer class
    def get_queryset(self, request):
        # annotating the base queryset before returning; adds orders field to each customer object.
        return super().get_queryset(request).annotate(orders=Count("order"))


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["id", "placed_at", "customer"]


class CollectionAdmin(admin.ModelAdmin):
    list_display = ["title", "products_count"]

    @admin.display(ordering="products_count")
    def products_count(self, collection):
        url = (
            reverse("admin:store_product_changelist")
            + "?"
            + urlencode({"collection__id": str(collection.id)})
        )
        return format_html("<a href='{}'>{}</a>", url, collection.products_count)

    # overriding the base QuerySet of Collection class
    def get_queryset(self, request):
        # annotating the base queryset before returning; adds product_count field to each collection object.
        return super().get_queryset(request).annotate(products_count=Count("product"))


admin.site.register(models.Collection, CollectionAdmin)
