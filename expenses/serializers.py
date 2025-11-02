# expenses/serializers.py
from rest_framework import serializers
from .models import Expense, Merchant

class MerchantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Merchant
        fields = ("id", "name")

class ExpenseSerializer(serializers.ModelSerializer):
    merchant = MerchantSerializer(read_only=True)
    merchant_id = serializers.PrimaryKeyRelatedField(
        queryset=Merchant.objects.all(),
        source="merchant",
        write_only=True,
        required=False
    )

    class Meta:
        model = Expense
        fields = (
            "id",
            "user",
            "merchant",
            "merchant_id",
            "amount",
            "date",
            "category",
            "receipt_image",
            "raw_text",
            "created_at",
        )
        read_only_fields = ("user", "raw_text", "created_at")


def validate_category(self, value):
    valid_categories = [choice[0] for choice in CATEGORY_CHOICES]
    if value not in valid_categories:
        return 'Other'
    return value
