from decimal import Decimal

from rest_framework import serializers

from .models import Product, Collection


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
