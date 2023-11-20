from decimal import Decimal

from rest_framework import serializers

from django.db import transaction

from .models import (
    Cart,
    CartItem,
    Customer,
    Order,
    OrderItem,
    Product,
    Collection,
    Review,
)


# nested object
# class CollectionSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)


# class ProductSerializer(serializers.Serializer):
#     id = serializers.IntegerField()
#     title = serializers.CharField(max_length=255)

#     # name of field does not have to match
#     price = serializers.DecimalField(
#         max_digits=6, decimal_places=2, source="unit_price"
#     )

#     # custom field
#     unit_price_tax = serializers.SerializerMethodField(method_name="calculate_tax")

#     # primary key related field
#     # collection = serializers.PrimaryKeyRelatedField(
#     #     queryset=Collection.objects.all(),
#     # )

#     # returns string representation of Collection class
#     # collection = (
#     #     serializers.StringRelatedField()
#     # )  # lazy loading ~ 1005 SQL queries at runtime

#     # using CollectionSerializer
#     # collection = CollectionSerializer()  # nested collection object

#     # collection with URL
#     collection = serializers.HyperlinkedRelatedField(
#         queryset=Collection.objects.all(),
#         view_name="collection-detail",  # view for generating hyperlinks
#     )

#     def calculate_tax(self, product: Product):
#         return product.unit_price * Decimal(
#             1.1
#         )  # Decimal and float multiplication not allowed


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title"]


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "description",
            "slug",
            "inventory",
            "unit_price",
            "price_with_tax",
            "collection",  # by default models use PrimaryKeyRelatedField serializer.
        ]
        # fields = "__all__" # BAD PRACTICE

    price_with_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(
            1.1
        )  # Decimal and float multiplication not allowed

    # Overriding the validate method of serializer
    # def validate(self, data):
    #     # make sure password and confirm_password values are same
    #     if data["password"] != data["confirm_password"]:
    #         return serializers.ValidationError("Passwords do not match")
    #     return data

    # overriding the create method
    # def create(self, validated_data):
    #     product = Product(**validated_data)  # unpacking the dictionary
    #     product.other = (
    #         1  # setting 'other' field, not listed in fields attribute of Meta class
    #     )
    #     product.save()
    #     return product

    # Overriding the update method
    # def update(self, instance, validated_data):
    #     instance.unit_price = validated_data.get("unit_price")
    #     instance.save()
    #     return instance


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ["id", "title", "products_count"]

    products_count = serializers.SerializerMethodField(
        method_name="get_products_count"
    )  # default method is get_<field_name>

    # OPTIONAL: When using annotate we must define field name
    # products_count = serializers.IntegerField(read_only=True) # field won't be available during creating or updating a collection object.

    def get_products_count(self, collection: Collection):
        return collection.product_set.count()


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["id", "date", "name", "description"]

    def create(self, validated_data):
        # overriding implementation
        product_id = self.context["product_id"]
        return Review.objects.create(
            product_id=product_id, **validated_data
        )  # product_id==product


# class CartItemSerializer(serializers.ModelSerializer):
#     total_price = serializers.SerializerMethodField(method_name="get_total_price")

#     class Meta:
#         model = CartItem
#         fields = [
#             "product",
#             "quantity",
#             "total_price",
#         ]

#     def get_total_price(self, cartitem):
#         return cartitem.product.unit_price * Decimal(cartitem.quantity)


# class CartSerializer(serializers.ModelSerializer):
#     # read only id field, UUID created automatically when sending request to endpoint
#     id = serializers.UUIDField(read_only=True)
#     items = CartItemSerializer(
#         many=True,
#         read_only=True,
#     )  # requires field name to be same as related_name i.e. items
#     # items = serializers.SerializerMethodField(method_name="get_items")
#     total_price = serializers.SerializerMethodField(method_name="get_total_price")

#     class Meta:
#         model = Cart
#         fields = ["id", "items", "total_price"]

#     # def get_items(self, cart):
#     #     cart_items = CartItem.objects.filter(cart_id=cart)
#     #     return CartItemSerializer(cart_items, many=True).data

#     def get_total_price(self, cart):
#         cart_items = CartItem.objects.filter(cart_id=cart)
#         total_price = total_price = sum(
#             item.product.unit_price * item.quantity for item in cart_items
#         )
#         # for item in cart_items:
#         #     total_price += item.product.unit_price * item.quantity
#         return total_price


# Solution: 2


# simplified product serializer, contains less information
class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "title", "unit_price"]


class CartItemSerializer(serializers.ModelSerializer):
    # redefining product field
    product = SimpleProductSerializer()

    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart_item: CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total_price"]


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(read_only=True, many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        # list comprehension
        # cart.items.all() returns a manager obj. which is iterable
        return sum(
            [item.quantity * item.product.unit_price for item in cart.items.all()]
        )

    class Meta:
        model = Cart
        fields = ["id", "items", "total_price"]


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    # validating fields
    # syntax: validate_<fieldname>(self, value):
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError("No product with the given ID was found")
        return value

    # overriding the save method
    def save(self, **kwargs):
        """
        Updates the product quantity of cart item if product is already
        present inside cart.
        """
        # get cart_id from context
        cart_id = self.context["cart_id"]

        # get validated data
        product_id = self.validated_data["product_id"]
        quantity = self.validated_data["quantity"]

        # get the cart item if already present
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            # update the cart item
            cart_item.quantity += quantity  # TODO: instead of adding value to quantity replace it with new quantity value.
            cart_item.save()
            self.instance = cart_item  # default method of saving; check ModelSerializer for implementation
        except CartItem.DoesNotExist:
            # Create a new item
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )

        return self.instance

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "quantity"]


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["quantity"]


class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = [
            "id",  # created dynamically at runtime, if not explicitly defined.
            "user_id",  # created dynamically at runtime, if not explicitly defined.
            "phone",
            "birth_date",
            "membership",
        ]


class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = OrderItem
        fields = [
            "id",
            "product",
            "quantity",
            "unit_price",
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer",
            "placed_at",
            "payment_status",
            "items",
        ]


# using base serializer because of usage of fields from different models
class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    # overriding save method to delete cart on placing order.
    def save(self, **kwargs):
        # transaction
        with transaction.atomic():
            cart_id = self.validated_data["cart_id"]

            print(self.validated_data["cart_id"])
            print(self.context["user_id"])

            # getting customer
            (customer, created) = Customer.objects.get_or_create(
                user_id=self.context["user_id"]
            )
            # Creating a order object
            order = Order.objects.create(customer=customer)

            # get cart items
            cart_items = CartItem.objects.select_related("product").filter(
                cart_id=cart_id
            )

            # create order items
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    unit_price=item.product.unit_price,
                    quantity=item.quantity,
                )
                for item in cart_items
            ]

            # bulk create OrderItem objects
            OrderItem.objects.bulk_create(order_items)

            # now delete the shopping cart
            Cart.objects.filter(pk=cart_id).delete()

            return order
