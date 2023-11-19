from django.contrib import admin, messages
from django.db.models.aggregates import Count
from django.urls import reverse
from django.utils.html import format_html, urlencode

from . import models


class InventoryFilter(admin.SimpleListFilter):
    title = "inventory"
    parameter_name = "inventory"

    def lookups(self, request, model_admin):
        return [("<10", "Low")]

    def queryset(self, request, queryset):
        if self.value() == "<10":
            return queryset.filter(inventory__lt=10)


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    # fields = ["title", "slug"]
    # readonly_fields = ["title"]
    # exclude = ["promotions"]

    # NOTE: Fields are only prepopulated during creation of objects
    prepopulated_fields = {
        "slug": [
            "title",  # can be multiple field, Django will combine them
        ]
    }
    autocomplete_fields = [
        "collection"
    ]  # search_field must be defined in Collection admin class
    search_fields = ["product"]
    actions = ["clear_inventory"]
    list_display = ["title", "unit_price", "inventory_status", "collection_title"]
    list_editable = ["unit_price"]
    list_filter = ["collection", "last_update", InventoryFilter]
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

    # custom action
    @admin.action(description="Clear inventory")
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(
            inventory=0
        )  # set inventory of selected objects to 0
        # display message on success
        self.message_user(
            request,
            f"{updated_count} products were successfully updated.",
            messages.SUCCESS,  # message type
        )


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    # first_name and last_name refers to method names
    list_display = [
        "first_name",
        "last_name",
        "membership",
        "orders",
    ]  # cannot define related fields like user__first_name
    list_editable = ["membership"]

    # eager loading
    list_select_related = ["user"]

    ordering = ["user__first_name", "user__last_name"]
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


class OrderItemInline(admin.StackedInline):
    autocomplete_fields = ["product"]
    model = models.OrderItem
    min_num = 1
    max_num = 10
    extra = 0  # only one product field is displayed


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ["customer"]
    list_display = ["id", "placed_at", "customer"]
    inlines = [OrderItemInline]


class CollectionAdmin(admin.ModelAdmin):
    search_fields = [
        "title"
    ]  # required to make work autocomplete_fields in ProductAdmin class.
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
        return (
            super().get_queryset(request).annotate(products_count=Count("product"))
        )  # Use product instead of products if related _name=product is defined in collection field of Product model.


admin.site.register(models.Collection, CollectionAdmin)

admin.site.register(models.Cart)
admin.site.register(models.CartItem)
