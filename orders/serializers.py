from rest_framework import serializers
from .models import Order, OrderLine, Payment


class OrderLineSerializer(serializers.ModelSerializer):
    class Meta:
        read_only_fields = ('status',)
        model = OrderLine
        fields = (
            'id',
            'product',
            'order',
            'quantity',
            'size',
            'weight',
            'shipping_fees',
            'shipping_status',
            'status',
        )


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            'id',
            'order',
            'first_name',
            'last_name',
            'country',
            'country_code',
            'state',
            'street_address',
            'post_code',
            'City',
            'Email_Address',
            'phone',
            'payment_method',
        )


class OrderSerializer(serializers.ModelSerializer):
    order_line = OrderLineSerializer(many=True, read_only=True)
    payment = PaymentSerializer(many=True, read_only=True)

    class Meta:
        read_only_fields = ('user', 'status')
        model = Order
        fields = (
            'id',
            'user',
            'order_date',
            'date_update',
            'coupon',
            'sub_total',
            'discount',
            'shipping',
            'amount',
            'tracking_no',
            'rpt_cache',
            'weight',
            'is_finished',
            'status',
            'details',
            'order_line',
            'payment',
        )

    def to_representation(self, instance):
        detail = []
        rep = super(OrderSerializer, self).to_representation(instance)
        if instance.coupon:
            rep['coupon'] = instance.coupon.code
        if instance.user:
            rep['user'] = instance.user.username
        if instance.order_line:
            for item in instance.order_line.all():
                detail.append({
                    'id': item.id,
                    'order': item.order.id,
                    'product': item.product,
                    'status': item.status,
                    'product_vendor': item.product.product_vendor.user.username,
                    'product': item.product.product_name,
                    'regular_price': item.product.regular_price.amount,
                })
            rep['order_line'] = detail
        return rep


class OrderLineVendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderLine
        fields = (
            'id',
            'quantity',
            'size',
            'weight',
            'shipping_fees',
            'shipping_status',
            'status',
        )
