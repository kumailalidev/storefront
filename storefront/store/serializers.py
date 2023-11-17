from decimal import Decimal

from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    # name of field does not have to match
    price = serializers.DecimalField(
        max_digits=6, decimal_places=2, source="unit_price"
    )
    # custom field
    unit_price_tax = serializers.SerializerMethodField(method_name="calculate_tax")

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(
            1.1
        )  # Decimal and float multiplication not allowed
