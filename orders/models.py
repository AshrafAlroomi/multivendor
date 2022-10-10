from django.db import models
from django.contrib.auth.models import User
from products.models import Product
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import Profile
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from rest_framework.exceptions import ValidationError


# Create your models here.


class Order(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, related_name='user_client', blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    details = models.ManyToManyField(Product, through="OrderLine")
    coupon = models.ForeignKey(
        "Coupon", on_delete=models.SET_NULL, blank=True, null=True)
    sub_total = models.CharField(max_length=50, blank=True, null=True)
    discount = models.CharField(max_length=50, blank=True, null=True)
    shipping = models.CharField(max_length=50, blank=True, null=True)
    amount = models.CharField(max_length=50, )
    tracking_no = models.CharField(max_length=50, blank=True, null=True)
    rpt_cache = models.URLField(blank=True, null=True)
    weight = models.DecimalField(
        default=0, max_digits=10, decimal_places=3, verbose_name=_("WEIGHT"))
    is_finished = models.BooleanField(default=False)
    PENDING = 'PENDING'
    Accepted = 'Accepted'
    Underway = 'Underway'
    COMPLETE = 'COMPLETE'
    Refunded = 'Refunded'
    Status_select = [
        (PENDING, 'PENDING'),
        (Accepted, 'Accepted'),
        (Underway, 'Underway'),
        (COMPLETE, 'COMPLETE'),
        (Refunded, 'Refunded'),
    ]
    status = models.CharField(
        max_length=13,
        choices=Status_select,
        default=PENDING,
    )

    def __str__(self):
        return str(self.id)

    # def get_recommended_profiles(self):
    #     qs = Profile.objects.all()
    #     my_recs = []
    #     for profile in qs:
    #         if profile.recommended_by == self.user:
    #             my_recs.append(profile)
    #     return my_recs

    def save(self, *args, **kwargs):
        if self.status == "PENDING":
            order_suppliers = OrderSupplier.objects.all().filter(order=self.id)
            for order_supplier in order_suppliers:
                order_supplier.status = self.status
                order_supplier.save()

        else:
            order_suppliers = OrderSupplier.objects.all().filter(order=self.id)
            for order_supplier in order_suppliers:
                order_supplier.status = self.status
                order_supplier.is_finished = True
                order_supplier.save()

            ref = float(self.amount) * 0.025
            try:
                recommended_by = Profile.objects.get(
                    user=self.user).recommended_by
                blance = Profile.objects.get(user=recommended_by)
                blance.blance = blance.blance + float(ref)
                blance.save()
            except:
                pass

        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)


class OrderLine(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_line')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_line')
    quantity = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("quantity"))
    size = models.CharField(max_length=10, blank=True, null=True)
    weight = models.DecimalField(
        default=0, max_digits=10, decimal_places=3, verbose_name=_("WEIGHT"))
    shipping_fees = models.CharField(max_length=50, blank=True, null=True)
    shipping_status = models.CharField(max_length=50, blank=True, null=True)
    price = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("Price"))
    PENDING = 'PENDING'
    Accepted = 'Accepted'
    Underway = 'Underway'
    COMPLETE = 'COMPLETE'
    Refunded = 'Refunded'
    Status_select = [
        (PENDING, 'PENDING'),
        (Accepted, 'Accepted'),
        (Underway, 'Underway'),
        (COMPLETE, 'COMPLETE'),
        (Refunded, 'Refunded'),
    ]
    status = models.CharField(
        max_length=13,
        choices=Status_select,
        default=PENDING,
    )

    def __str__(self):
        return f"Order Line ID:{self.id}-user:{self.order.user}-product id:{self.product.id}-order id:{self.order.id}"

    def save(self, *args, **kwargs):
        if self.status == "Accepted":
            product = Product.objects.get(id=self.product.id)
            if self.quantity <= product.stock_quantity:
                product.stock_quantity = product.stock_quantity - self.quantity
                product.save()
            else:
                raise ValidationError(
                    {'403': "The quantity is higher than the available amount in the stock."}
                )

        product = Product.objects.all().get(id=self.product.id)
        if product.sale_price:
            self.price = product.sale_price.amount
        else:
            self.price = product.regular_price.amount

        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)

    def order_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.product.product_image.url))

    order_photo.short_description = "image"
    order_photo.allow_tags = True

    # def save(self, *args, **kwargs):

    #     super().save(*args, **kwargs)


class Coupon(models.Model):
    code = models.CharField(max_length=50, unique=True)
    valid_form = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)])
    active = models.BooleanField()

    class Meta:
        # verbose_name = "Coupons"
        # verbose_name_plural = "Couponss"
        ordering = ('-id',)

    def __str__(self):
        return f"{self.code}"


class Payment(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True, related_name='payment')
    first_name = models.CharField(max_length=100, )
    last_name = models.CharField(max_length=100, )
    # country = models.ForeignKey(
    #     Country, on_delete=models.SET_NULL, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    country_code = models.CharField(max_length=100, blank=True, null=True)
    # state = models.ForeignKey(
    #     State, on_delete=models.SET_NULL, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    street_address = models.CharField(max_length=100, )
    post_code = models.CharField(max_length=10, )
    # by_blance = models.CharField(max_length=100, )
    City = models.CharField(max_length=100, )
    Email_Address = models.EmailField()
    phone = models.CharField(max_length=20, )
    payment_method = models.CharField(max_length=100, )

    def __str__(self):
        return f"Payment ID:{self.id}- order:{self.order}"

    class Meta:
        ordering = ('-id',)


class Country(models.Model):
    name_country = models.CharField(max_length=40)
    country_code = models.CharField(max_length=40)
    countries = CountryField()

    def __str__(self):
        return self.name_country

    class Meta:
        ordering = ('name_country',)


class OrderSupplier(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    email_client = models.EmailField(
        max_length=250, blank=True, null=True)
    vendor = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, related_name='vendors', blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True)
    order_date = models.DateTimeField(auto_now_add=True)
    date_update = models.DateTimeField(auto_now=True)
    coupon = models.ForeignKey(
        Coupon, on_delete=models.SET_NULL, blank=True, null=True)
    sub_total = models.CharField(max_length=50, blank=True, null=True)
    discount = models.CharField(max_length=50, blank=True, null=True)
    shipping = models.CharField(max_length=50, blank=True, null=True)
    amount = models.CharField(max_length=50, )
    # tracking_no = models.CharField(max_length=50,  blank=True, null=True)
    # rpt_cache = models.URLField(blank=True, null=True)
    weight = models.DecimalField(
        default=0, max_digits=10, decimal_places=3, verbose_name=_("WEIGHT"))
    is_finished = models.BooleanField(default=False)
    PENDING = 'PENDING'
    Underway = 'Underway'
    COMPLETE = 'COMPLETE'
    Refunded = 'Refunded'
    Status_select = [
        (PENDING, 'PENDING'),
        (Underway, 'Underway'),
        (COMPLETE, 'COMPLETE'),
        (Refunded, 'Refunded'),
    ]
    status = models.CharField(
        max_length=13,
        choices=Status_select,
        default=PENDING,
    )

    def __str__(self):

        return str(self.id)

    def save(self, *args, **kwargs):

        if self.status == "Underway":
            ref = float(self.amount) * 0.025
            try:
                recommended_by = Profile.objects.get(
                    user=self.user).recommended_by
                blance = Profile.objects.get(user=recommended_by)
                blance.blance = blance.blance + float(ref)
                blance.save()
            except:
                pass
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('-id',)


class OrderDetailsSupplier(models.Model):
    supplier = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True)
    product = models.ForeignKey(
        Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, blank=True, null=True)
    order_supplier = models.ForeignKey(
        OrderSupplier, on_delete=models.CASCADE, blank=True, null=True)
    order_details = models.ForeignKey(
        OrderLine, on_delete=models.CASCADE, blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField()
    size = models.CharField(max_length=10, blank=True, null=True)
    weight = models.DecimalField(
        default=0, max_digits=10, decimal_places=3, verbose_name=_("WEIGHT"))

    def __str__(self):
        return f"Order Details ID:{self.id}-user:{self.order.user}-product id:{self.product.id}-order id:{self.order.id}"

    class Meta:
        ordering = ('-id',)

    def order_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.product.PRDImage.url))

    order_photo.short_description = "image"
    order_photo.allow_tags = True

    # def save(self, *args, **kwargs):
    #     order_details = OrderDetails.objects.all().filter(order=self.order , supplier = self.supplier)
    #     print(order_details)
    #     f_total = 0
    #     w_total = 0
    #     for sub in order_details:
    #         f_total += sub.price * sub.quantity
    #         w_total += sub.weight * sub.quantity
    #         total = f_total
    #         weight = w_total
    #     obj_order_supplier = OrderSupplier.objects.get(
    #         id=self.order_supplier.id)
    #     obj_order_supplier.amount = total
    #     obj_order_supplier.save()
    #     super().save(*args, **kwargs)
