from django.conf import settings
from django.db import models
from django.contrib import admin
from django.core.validators import MinValueValidator

from uuid import uuid4

from .validators import validate_file_size


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

    # Related fields
    # product_set (Model: Product)


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", null=True, on_delete=models.SET_NULL, related_name="+"
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]

    # Related fields
    # product_set (Model: Product)


class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )
    inventory = models.IntegerField(
        validators=[
            MinValueValidator(
                1, message="Inventory value must be greater than or equal to 1."
            )
        ]
    )
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]

    # Related fields
    #   - images (Model: ProductImage)
    #   - orderitems (Model: OrderItem)
    #   - cartitem_set (Model: CartItem)
    #   - reviews (Model: Reviews)


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}"

    @admin.display(ordering="user__first_name")
    def first_name(self):
        return self.user.first_name

    @admin.display(ordering="user__last_name")
    def last_name(self):
        return self.user.last_name

    class Meta:
        ordering = ["user__first_name", "user__last_name"]
        permissions = [
            ("view_history", "Can view history"),
        ]

    # Related fields
    #   - order_set (Model: Order)
    #   - address_set (Model: Address)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="store/images", validators=[validate_file_size])


class Order(models.Model):
    PAYMENT_STATUS_PENDING = "P"
    PAYMENT_STATUS_COMPLETED = "C"
    PAYMENT_STATUS_FAILED = "F"

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, "Pending"),
        (PAYMENT_STATUS_COMPLETED, "Completed"),
        (PAYMENT_STATUS_FAILED, "Failed"),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING
    )
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    def __str__(self) -> str:
        return str(self.id)

    class Meta:
        permissions = [
            ("cancel_order", "Can cancel order"),
        ]

    # Related fields
    #   - items (Model: OrderItem)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="items")
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems"
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4)
    created_at = models.DateTimeField(auto_now_add=True)

    # Related fields
    #   - items (Model: CartItem)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = [
            ["cart", "product"],
        ]


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)


class Review(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    name = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateField(auto_now_add=True)
