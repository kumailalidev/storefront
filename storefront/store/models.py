from django.db import models
from django.core.validators import MinValueValidator


class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()
    # product_set (reverse relationship name)


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey(
        "Product", null=True, on_delete=models.SET_NULL, related_name="+"
    )  # circular relationship. '+' -> do not create reverse relationship

    # overriding magic __str__ method
    def __str__(self) -> str:  # type annotation syntax
        return self.title

    class Meta:
        ordering = ["title"]


class Product(models.Model):
    # sku = models.CharField(max_length=10, primary_key=True)
    title = models.CharField(max_length=255)  # varchar 255
    slug = models.SlugField()
    description = models.TextField(blank=True, null=True)
    unit_price = models.DecimalField(
        max_digits=6, decimal_places=2, validators=[MinValueValidator(1)]
    )  # 9999.99
    inventory = models.IntegerField(
        validators=[
            MinValueValidator(
                1, message="Inventory value must be greater than or equal to 1."
            )
        ]
    )
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion, blank=True)  # optional by default
    # orderitems

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["title"]


class Customer(models.Model):
    # choice values
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    # choices
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, "Bronze"),
        (MEMBERSHIP_SILVER, "Silver"),
        (MEMBERSHIP_GOLD, "Gold"),
    ]

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE
    )
    # order_set (reverse relationship created by Order class, use order when using Count())

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        ordering = ["first_name", "last_name"]

    # defined in admin.py
    # class Meta:
    #     ordering = ["first_name"]


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
    customer = models.ForeignKey(
        Customer, on_delete=models.PROTECT
    )  # orders should never be deleted
    # orderitems

    def __str__(self) -> str:
        return str(self.id)


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT
    )  # orderitem_set; reverse relationship
    product = models.ForeignKey(
        Product, on_delete=models.PROTECT, related_name="orderitems"
    )
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()


class Address(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)  # parent field
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
