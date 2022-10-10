from rest_framework import serializers

from .models import Product, ProductRating, ProductImage,Category
from djmoney.contrib.django_rest_framework import MoneyField

from rest_framework_recursive.fields import RecursiveField

class CategorySerializer(serializers.ModelSerializer):

    children = RecursiveField(many=True,read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name','category_image','date','date_update','parent', 'children']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('product_vendor','archived_by','archived_date', )
        model = Product
        fields = (
            'id',
            'product_vendor',
            'product_name',
            'category',
            'short_description',
            'description',
            'product_image',
            'regular_price',
            'sale_price',
            'sale_price_currency',
            'additional_image_1',
            'additional_image_2',
            'additional_image_3',
            'additional_image_4',
            'feedback_average',
            'feedback_number',
            'length',
            'width',
            'height',
            'weight',
            'pieces',
            'stock_quantity',
            'SKU',
            'is_sale',
            'promotional',
            'status',
            'archived',
            'archived_by',
            'archived_date',
            'product_tags',
            'product_slug',
            'published_date',
            'updated',
            'date',
        )

    def to_representation(self, instance):
        rep = super(ProductSerializer, self).to_representation(instance)
        if instance.product_vendor:
            rep['product_vendor'] = instance.product_vendor.user.username
        if instance.category:
            rep['category'] = instance.category.name

        return rep


class ProductRatingSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('client_name', 'product')
        model = ProductRating
        fields = (
            'id',
            'product',
            'vendor',
            'rate',
            'client_name',
            'client_comment',
            'rating_date',
            'rating_update'
        )

    def to_representation(self, instance):
        rep = super(ProductRatingSerializer, self).to_representation(instance)
        if instance.client_name:
            rep['client_name'] = instance.client_name.user.username
        if instance.vendor:
            rep['vendor'] = instance.vendor.user.username
        if instance.product:
            rep['product'] = instance.product.product_name
        return rep


class ProductRatingVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = (
            'id',
            'product',
            'vendor',
            'client_name',
            'rate',
            'client_comment',
            'rating_date',
            'rating_update',
            'active',
        )

    def to_representation(self, instance):
        rep = super(ProductRatingVendorSerializer, self).to_representation(instance)
        if instance.client_name:
            rep['client_name'] = instance.client_name.user.username
        if instance.vendor:
            rep['vendor'] = instance.vendor.user.username
        if instance.product:
            rep['product'] = instance.product.product_name
        return rep


class ProductRatingVendorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductRating
        fields = (
            'id',
            'active',
        )
