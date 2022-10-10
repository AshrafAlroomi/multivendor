from dataclasses import fields
from rest_framework import serializers
from special_deals.models import SpecialDeal, SpecialDealItem


class SpecialDealItemSerializer(serializers.ModelSerializer):
    # specialDeal_id = serializers.PrimaryKeyRelatedField(
    #     queryset=SpecialDeal.objects.all(), source="specialDeal.id"
    # )

 
    class Meta:
        model = SpecialDealItem
        fields = [
            "id",
            "specialDeal",
            'product',
            'quantity',

        ]

   

class SpecialDealSerializer(serializers.ModelSerializer):
    items = SpecialDealItemSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = SpecialDeal
        owner = serializers.ReadOnlyField(source="owner.username")
        fields = [
            "id",
            "owner",
            "ordinal",
            "name",
            "description",
            "special_deal_image",
            "additional_image_1",
            "additional_image_2",
            "additional_image_3",
            "additional_image_4",
            "price",
            "valid_form",
            "valid_to",
            "active",
            "date",
            "date_update",
            "items",
        ]

