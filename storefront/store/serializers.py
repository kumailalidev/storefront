from decimal import Decimal

from rest_framework import serializers

from .models import Product, Collection, Review


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
