from django.shortcuts import render, redirect
from .models import Order, OrderLine, Payment, Coupon, Country, OrderSupplier, OrderDetailsSupplier
from products.models import Product
from django.contrib import messages
from django.utils import timezone
from decimal import Context, Decimal
from accounts.models import Profile
from settings.models import SiteSetting
import stripe
from django.conf import settings
from django.views.generic import TemplateView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.http import HttpResponseRedirect
from django.views import View
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
import requests
from bs4 import BeautifulSoup
import datetime
from django_countries import countries as allcountries

from .serializers import OrderSerializer, OrderLineSerializer, PaymentSerializer, OrderLineVendorSerializer
from rest_framework import generics
from .permissions import IsCustomer, IsVendor, IsAccepted
from rest_framework.permissions import IsAuthenticated


class ListOrdersAPIView(generics.ListCreateAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DetailedOrderAPIView(generics.RetrieveUpdateDestroyAPIView):
    model = Order
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(user=user)


class ListOrderLineAPIView(generics.ListCreateAPIView):
    model = OrderLine
    serializer_class = OrderLineSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return OrderLine.objects.filter(order__user=user)


class DetailedOrderLineAPIView(generics.RetrieveDestroyAPIView):
    model = OrderLine
    serializer_class = OrderLineSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return OrderLine.objects.filter(order__user=user)


class UpdateOrderLineAPIView(generics.RetrieveUpdateAPIView):
    model = OrderLine
    serializer_class = OrderLineSerializer
    permission_classes = (IsAuthenticated, IsCustomer, IsAccepted)

    def get_queryset(self):
        user = self.request.user
        return OrderLine.objects.filter(order__user=user)


class ListPaymentAPIView(generics.ListCreateAPIView):
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(order__user=user)


class DetailedPaymentAPIView(generics.RetrieveUpdateDestroyAPIView):
    model = Payment
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self):
        user = self.request.user
        return Payment.objects.filter(order__user=user)


class VendorListOrdersAPIView(generics.ListAPIView):
    model = OrderLine
    serializer_class = OrderLineVendorSerializer
    permission_classes = (IsAuthenticated, IsVendor)

    def get_queryset(self):
        user = self.request.user.profile_user
        return OrderLine.objects.filter(product__product_vendor=user)


class VendorDetailedOrderAPIView(generics.RetrieveUpdateDestroyAPIView):
    model = OrderLine
    serializer_class = OrderLineVendorSerializer
    permission_classes = (IsAuthenticated, IsVendor)

    def get_queryset(self):
        user = self.request.user.profile_user
        return OrderLine.objects.filter(product__product_vendor=user)


ts = datetime.datetime.now().timestamp()
time = round(ts * 1000)


def add_to_cart(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    if "qyt" in request.POST and "product_id" in request.POST and "product_Price" in request.POST and request.user.is_authenticated and not request.user.is_anonymous:

        product_id = request.POST['product_id']
        qyt = int(request.POST['qyt'])
        size = None
        if "size" in request.POST:
            size = request.POST['size']
            # print(request.POST['size'])
        product = Product.objects.get(id=product_id)

        if qyt <= 0 and product.available == 0:
            messages.warning(request, 'This product is out of stock !')
            return redirect('orders:cart')

        if product.available < qyt and product.available == 0:
            messages.warning(request, 'This product is out of stock !')
            return redirect('orders:cart')

        if qyt <= 0 and product.available != 0:
            qyt = 1

        if product.available < qyt and product.available != 0:
            qyt = product.available

        order = Order.objects.all().filter(user=request.user, is_finished=False)
        if not Product.objects.all().filter(id=product_id).exists():
            return HttpResponse(f"this product not found !")

        if order:
            old_orde = Order.objects.get(user=request.user, is_finished=False)
            # old_orde_supplier = OrderSupplier.objects.get(
            #     user=request.user, is_finished=False, order=old_orde)
            # print("old_orde_supplier:", old_orde_supplier)
            if OrderLine.objects.all().filter(order=old_orde,
                                              product=product).exists() and OrderDetailsSupplier.objects.all().filter(
                    order=old_orde, product=product).exists():
                item = OrderLine.objects.get(
                    order=old_orde, product=product)
                item_supplier = OrderDetailsSupplier.objects.get(
                    order=old_orde, product=product)
                # for i in items:
                if item.quantity >= product.available:
                    qyt = item.quantity
                    # i.quantity = int(qyt)
                    # i.save()
                    messages.warning(
                        request, f"You can't add more from this product, available only : {qyt}")
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

                elif qyt < product.available:
                    qyt = qyt + item.quantity
                    if qyt > product.available:
                        qyt = product.available

                    item.quantity = int(qyt)
                    item_supplier.quantity = int(qyt)
                    item.save()
                    item_supplier.save()

                    # code for total amount main order
                    order_details_main = OrderLine.objects.all().filter(order=old_orde)
                    f_total = 0
                    w_total = 0
                    weight = 0
                    for sub in order_details_main:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total

                    old_orde.sub_total = f_total
                    old_orde.weight = weight
                    old_orde.amount = total
                    old_orde.save()

                    # code for total amount supplier order
                    old_order_supplier = OrderSupplier.objects.get(
                        user=request.user, is_finished=False, order=old_orde, vendor=product.product_vendor)
                    order_supplier = OrderDetailsSupplier.objects.all().filter(
                        order_supplier=old_order_supplier)
                    weight = 0
                    f_total = 0
                    w_total = 0
                    for sub in order_supplier:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total
                    old_order_supplier.weight = weight
                    old_order_supplier.amount = total
                    old_order_supplier.save()

                # if i.size != size:
                #     order_details = OrderLine.objects.create(
                #         supplier=product.product_vendor.user,
                #         product=product,
                #         order=old_orde,
                #         price=product.PRDPrice,
                #         quantity=qyt,
                #         size=size,
                #         weight=product.PRDWeight

                #     )
                #     break

                else:
                    item.quantity = int(qyt)
                    item_supplier.quantity = int(qyt)
                    # i.supplier = product.product_vendor.user
                    item.save()
                    item_supplier.save()

                    # code for total amount main order
                    order_details_main = OrderLine.objects.all().filter(order=old_orde)
                    f_total = 0
                    w_total = 0
                    weight = 0
                    for sub in order_details_main:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total

                    old_orde.sub_total = f_total
                    old_orde.weight = weight
                    old_orde.amount = total
                    old_orde.save()

                    # code for total amount supplier order
                    old_order_supplier = OrderSupplier.objects.get(
                        user=request.user, is_finished=False, order=old_orde, vendor=product.product_vendor)
                    order_supplier = OrderDetailsSupplier.objects.all().filter(
                        order_supplier=old_order_supplier)

                    f_total = 0
                    w_total = 0
                    weight = 0
                    for sub in order_supplier:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total
                    old_order_supplier.weight = weight
                    old_order_supplier.amount = total
                    old_order_supplier.save()

            else:
                order_details = OrderLine.objects.create(
                    supplier=product.product_vendor.user,
                    product=product,
                    order=old_orde,
                    price=product.PRDPrice,
                    quantity=qyt,
                    size=size,
                    weight=product.PRDWeight
                )
                # code for total amount main order

                order_details_main = OrderLine.objects.all().filter(order=old_orde)
                weight = 0
                f_total = 0
                w_total = 0
                for sub in order_details_main:
                    f_total += sub.price * sub.quantity
                    w_total += sub.weight * sub.quantity
                    total = f_total
                    weight = w_total

                old_orde.sub_total = f_total
                old_orde.weight = weight
                old_orde.amount = total
                old_orde.save()
                # add product for old order supplier
                if OrderSupplier.objects.all().filter(
                        user=request.user, is_finished=False, vendor=product.product_vendor).exists():
                    old_order_supplier = OrderSupplier.objects.get(
                        user=request.user, is_finished=False, order=old_orde, vendor=product.product_vendor)
                    order_details_supplier = OrderDetailsSupplier.objects.create(
                        supplier=product.product_vendor.user,
                        product=product,
                        order=old_orde,
                        order_supplier=old_order_supplier,
                        order_details=order_details,
                        price=product.PRDPrice,
                        quantity=qyt,
                        size=size,
                        weight=product.PRDWeight
                    )

                    # code for total amount supplier order
                    order__supplier = OrderDetailsSupplier.objects.all().filter(
                        order_supplier=old_order_supplier)
                    f_total = 0
                    w_total = 0
                    weight = 0
                    for sub in order__supplier:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total
                    old_order_supplier.weight = weight
                    old_order_supplier.amount = total
                    old_order_supplier.save()

                else:
                    # order for  new supllier
                    new_order_supplier = OrderSupplier()
                    new_order_supplier.user = request.user
                    new_order_supplier.email_client = request.user.email
                    new_order_supplier.vendor = product.product_vendor
                    new_order_supplier.order = old_orde
                    new_order_supplier.save()
                    order_details_supplier = OrderDetailsSupplier.objects.create(
                        supplier=product.product_vendor.user,
                        product=product,
                        order=old_orde,
                        order_supplier=new_order_supplier,
                        order_details=order_details,
                        price=product.PRDPrice,
                        quantity=qyt,
                        size=size,
                        weight=product.PRDWeight
                    )

                    order_supplier = OrderDetailsSupplier.objects.all().filter(
                        order_supplier=new_order_supplier)
                    weight = 0
                    f_total = 0
                    w_total = 0
                    for sub in order_supplier:
                        f_total += sub.price * sub.quantity
                        w_total += sub.weight * sub.quantity
                        total = f_total
                        weight = w_total
                    new_order_supplier.weight = weight
                    new_order_supplier.amount = total
                    new_order_supplier.save()

            messages.success(request, 'product has been added to cart !')
            # return redirect('orders:cart')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        else:
            # order for all
            new_order = Order()
            new_order.user = request.user
            new_order.email_client = request.user.email
            new_order.save()
            # will edite
            # new_order.supplier = product.product_vendor.user
            # new_order.vendors.add(product.product_vendor)

            # order for supllier
            new_order_supplier = OrderSupplier()
            new_order_supplier.user = request.user
            new_order_supplier.email_client = request.user.email
            new_order_supplier.vendor = product.product_vendor
            new_order_supplier.order = new_order
            new_order_supplier.save()

            order_details = OrderLine.objects.create(
                supplier=product.product_vendor.user,
                product=product,
                order=new_order,
                price=product.PRDPrice,
                quantity=qyt,
                size=size,
                weight=product.PRDWeight
            )

            order_details_supplier = OrderDetailsSupplier.objects.create(
                supplier=product.product_vendor.user,
                product=product,
                order=new_order,
                order_supplier=new_order_supplier,
                order_details=order_details,
                price=product.PRDPrice,
                quantity=qyt,
                size=size,
                weight=product.PRDWeight
            )
            # code for total amount main order

            order_details_main = OrderLine.objects.all().filter(order=new_order)
            f_total = 0
            w_total = 0
            weight = 0
            for sub in order_details_main:
                f_total += sub.price * sub.quantity
                w_total += sub.weight * sub.quantity
                total = f_total
                weight = w_total

            new_order.sub_total = f_total
            new_order.weight = weight
            new_order.amount = total
            new_order.save()
            # code for total amount supplier order
            order_details__supplier = OrderDetailsSupplier.objects.all().filter(
                order_supplier=new_order_supplier)
            f_total = 0
            w_total = 0
            weight = 0
            for sub in order_details__supplier:
                f_total += sub.price * sub.quantity
                w_total += sub.weight * sub.quantity
                total = f_total
                weight = w_total
            new_order_supplier.weight = weight
            new_order_supplier.amount = total
            new_order_supplier.save()

            messages.success(request, 'product has been added to cart !')
            # return redirect('orders:cart')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        messages.warning(
            request, 'You must first log in to your account to purchase the product')
        return redirect('accounts:login')


def cart(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    if "code" in request.POST and request.user.is_authenticated and not request.user.is_anonymous:
        now = timezone.now()
        code = request.POST['code']
        request.session['code'] = code
        coupon = None
        if Coupon.objects.all().filter(code=code, active=True):
            coupon = Coupon.objects.get(code=code, active=True)
            request.session['coupon_id'] = coupon.id
            messages.success(
                request, 'Discount code has been added successfully ')

        else:
            messages.warning(
                request, 'The discount code is not available or has expired ')
            request.session['coupon_id'] = None
            # request.session['code'] = None
        return redirect('orders:cart')

    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')

    context = None
    PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
    if request.user.is_authenticated and not request.user.is_anonymous:
        # countries = Country.objects.all().filter().order_by('-name_country')
        countries = allcountries
        first_country = Country.objects.all(
        ).filter().order_by('-name_country')[0:1]
        # states = State.objects.filter(country=first_country)
        if Order.objects.all().filter(user=request.user, is_finished=False):
            blance = Profile.objects.get(user=request.user).blance
            order = Order.objects.get(user=request.user, is_finished=False)
            order_details = OrderLine.objects.all().filter(order=order)

            coupon_id = None
            value = None
            total = None
            weight = None
            code = None
            f_total = 0
            w_total = 0
            for sub in order_details:
                f_total += sub.price * sub.quantity
                w_total += sub.weight * sub.quantity
                total = f_total
                weight = w_total

            if request.session.get("coupon_id"):
                coupon_id = request.session.get("coupon_id")
                code = request.session.get("code")
                if Coupon.objects.all().filter(id=coupon_id):
                    discount = Coupon.objects.get(id=coupon_id).discount
                    value = (discount / Decimal("100")) * f_total
                    total = f_total - value
                    # print(total)

                    # order = Order.objects.all().filter(user=request.user, is_finished=False)
                    if order:
                        old_orde = Order.objects.get(
                            user=request.user, is_finished=False)
                        old_orde.amount = total
                        old_orde.discount = value
                        old_orde.sub_total = f_total
                        # old_orde = weight
                        old_orde.coupon = Coupon.objects.get(id=coupon_id)
                        old_orde.save()

                # else:
                #     total = f_total
                #     coupon_id = None
            else:
                # total = f_total
                # coupon_id = None
                old_orde = Order.objects.get(
                    user=request.user, is_finished=False)
                old_orde.amount = total
                old_orde.discount = 0
                old_orde.sub_total = f_total
                old_orde.weight = weight
                old_orde.coupon = None
                old_orde.save()

                # print(total)

            # if "coupon_id" in request.session.keys():
            #     del request.session["coupon_id"]

            context = {
                "order": order,
                "order_details": order_details,
                "total": total,
                "f_total": f_total,
                "coupon_id": coupon_id,
                "value": value,
                "code": code,
                "blance": blance,
                "PUBLIC_KEY": PUBLIC_KEY,
                "countries": countries,
                # "states": states,
                "weight": weight,
            }
    return render(request, "orders/shop-cart.html", context)


class StatesJsonListView(View):
    def get(self, *args, **kwargs):
        country = kwargs.get('country')

        states = None
        # country_id = Country.objects.get(country_code=country)

        # qs = list(State.objects.all().filter(country=country_id).values())
        if settings.ARAMEX_USERNAME != "":
            print("true")
            data = {
                'ClientInfo': {
                    "UserName": f"{settings.ARAMEX_USERNAME}",
                    "Password": f"{settings.ARAMEX_PASSWORD}",
                    "Version": f"{settings.ARAMEX_VERSION}",
                    "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                    "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                    "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                    "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                    "Source": f"{settings.ARAMEX_SOURCE}"

                },
                "Transaction": None,

                "CountryCode": f"{country}"
            }

            url = 'https://ws.aramex.net/ShippingAPI.V2/Location/Service_1_0.svc/xml/FetchStates'
            r = requests.post(url, json=data)
            content = r.text
            soup = BeautifulSoup(content, 'html.parser')
            # print(soup)
            cities_list = []
            cities_tags = soup.find_all("name")
            for city in cities_tags:
                cities_list.append(city.text)
                # print(city.text)
            # print(len(cities_list))

            if len(cities_list) > 0 and len(country) > 0:
                states = cities_list
            else:
                url = 'https://ws.aramex.net/ShippingAPI.V2/Location/Service_1_0.svc/xml/FetchCities'
                r = requests.post(url, json=data)
                # print(r.text)
                content = r.text
                soup = BeautifulSoup(content, 'html.parser')
                cities_tags = soup.find_all("a:string")
                for city in cities_tags:
                    cities_list.append(city.text)
                states = cities_list[0:1000]
                # print(len(cities_list))
        else:
            print("false")
            states = False

        return JsonResponse({"success": True, "data": states}, safe=False)
        # return JsonResponse({"success": False, }, safe=False)


def remove_item(request, productdeatails_id):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    if request.user.is_authenticated and not request.user.is_anonymous and productdeatails_id:
        item_id = OrderLine.objects.get(id=productdeatails_id)

        if item_id.order.user.id == request.user.id:

            item = OrderLine.objects.all().filter(order_id=item_id.order_id).count()
            if item - 1 == 0:
                order = Order.objects.all().filter(user=request.user, is_finished=False)
                if order:
                    old_orde = Order.objects.get(
                        user=request.user, is_finished=False)
                    old_orde.delete()
                    if "coupon_id" in request.session.keys():
                        del request.session["coupon_id"]
                    messages.warning(request, ' Order has been deleted ')
                    return redirect('orders:cart')
            else:

                all_orders = Order.objects.all().filter(user=request.user, is_finished=False)
                for x in all_orders:

                    order = Order.objects.get(id=x.id)

                    # if OrderLine.objects.all().filter(order=order) == item_id.id and OrderDetails.objects.all().filter(order=order).exists():
                    if OrderLine.objects.all().filter(order=order).exists():
                        old_orde = Order.objects.get(
                            user=request.user, is_finished=False)

                        item_supplier = OrderDetailsSupplier.objects.get(
                            order_details=item_id)

                        obj_order_supplier = OrderSupplier.objects.get(
                            user=request.user, is_finished=False, order=old_orde,
                            vendor=item_supplier.product.product_vendor)

                        item_supplier = OrderDetailsSupplier.objects.all().filter(
                            order_supplier=obj_order_supplier).count()

                        if item_supplier - 1 == 0:

                            obj_order_supplier.delete()
                            item_id.delete()

                            messages.warning(
                                request, ' Order has been deleted ')
                            return redirect('orders:cart')

                        else:
                            item_id.delete()
                            # code for total order supplier
                            order_details__supplier = OrderDetailsSupplier.objects.all().filter(
                                order_supplier=obj_order_supplier)
                            f_total = 0
                            w_total = 0
                            weight = 0
                            for sub in order_details__supplier:
                                f_total += sub.price * sub.quantity
                                w_total += sub.weight * sub.quantity
                                total = f_total
                                weight = w_total
                            obj_order_supplier.weight = weight
                            obj_order_supplier.amount = total
                            obj_order_supplier.save()
                            messages.warning(
                                request, ' product has been deleted ')
                            # Logically the product is already deleted because of the relationship
                            # item_supplier = OrderDetailsSupplier.objects.get(
                            #     order_details=item_id)
                            # item_supplier.delete()
                            return redirect('orders:cart')
                    else:
                        messages.warning(
                            request, "product You can't delete it !")
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    messages.warning(request, "product You can't delete it !")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def payment(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    context = None
    try:
        shipping = SiteSetting.objects.all().first().shipping
    except:
        shipping = 0

    if settings.STRIPE_PUBLIC_KEY == "" or settings.STRIPE_PUBLIC_KEY == None:
        PUBLIC_KEY = False
    else:
        PUBLIC_KEY = settings.STRIPE_PUBLIC_KEY
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')

    # if "vodafone_cash" in request.POST and "pubg_username" in request.POST and "pubg_id" in request.POST and "notes" in request.POST and request.user.is_authenticated and not request.user.is_anonymous:
    if request.method == 'POST' and request.user.is_authenticated and not request.user.is_anonymous:

        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        country = request.POST['country']
        try:
            state = request.POST['state']
        except:
            messages.warning(
                request, 'Please contact us because this country is not in our shipping list')
            return redirect(request.META.get('HTTP_REFERER'))

        street_address = request.POST['street']

        ZIP = request.POST['ZIP']
        city = request.POST['city']
        email_address = request.POST['email_address']
        phone = request.POST['phone']

        # return HttpResponse(f"your info is request")
        state_obj = state
        country_obj = dict(allcountries)[str(country)]
        country_code = country
        if country_code == 'JO':
            product_group = "DOM"
            product_type = "OND"
        else:
            product_group = "EXP"
            product_type = "PPX"
        # country_obj = Country.objects.get(
        #     country_code=country)
        # country_code = country_obj.country_code
        order_weight = Order.objects.get(
            user=request.user, is_finished=False).weight
        # print(order_weight)
        if settings.ARAMEX_USERNAME != "":
            data = {
                'ClientInfo': {
                    "UserName": f"{settings.ARAMEX_USERNAME}",
                    "Password": f"{settings.ARAMEX_PASSWORD}",
                    "Version": f"{settings.ARAMEX_VERSION}",
                    "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                    "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                    "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                    "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                    "Source": f"{settings.ARAMEX_SOURCE}"

                },
                "Transaction": None,
                "DestinationAddress": {
                    "Line1": "",
                    "Line2": "",
                    "Line3": "",
                    "PostCode": ZIP,
                    "City": state,
                    "CountryCode": country_code
                },
                "OriginAddress": {
                    "Line1": "",
                    "Line2": "",
                    "Line3": "",
                    "PostCode": "",
                    "City": "Amman",
                    "CountryCode": "JO"
                },
                "ShipmentDetails": {
                    "Dimensions": None,
                    "DescriptionOfGoods": "",
                    "GoodsOriginCountry": "",
                    "PaymentOptions": "",
                    "PaymentType": "P",
                    "ProductGroup": product_group,
                    "ProductType": product_type,
                    "ActualWeight": {
                        "Value": float(order_weight),
                        "Unit": "KG"
                    },
                    "ChargeableWeight": None,
                    "NumberOfPieces": "1"

                }
            }

            url = 'https://ws.aramex.net/ShippingAPI.V2/RateCalculator/Service_1_0.svc/json/CalculateRate'
            r = requests.post(url, json=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            try:
                if soup.code.string == "ERR01" or soup.code.string == "ERR52" or soup.code.string == "ERR61" or soup.code.string == "ERR04":
                    messages.warning(request, f'{soup.message.string}')
                    return redirect('orders:cart')
            except:
                pass
            shipping = float(soup.value.string) * 1.41
            # print(shipping)
            currency_code = soup.currencycode.string

        order = Order.objects.all().filter(user=request.user, is_finished=False)

        if order:
            old_orde = Order.objects.get(user=request.user, is_finished=False)
            # if settings.ARAMEX_USERNAME != "" :
            old_orde.amount = float(old_orde.amount) + shipping
            old_orde.shipping = shipping
            old_orde.save()
            request.session['order_id'] = old_orde.id
            order_details = OrderLine.objects.all().filter(order=old_orde)
            try:
                if Payment.objects.all().filter(order=old_orde):
                    payment_info = Payment.objects.get(order=old_orde)
                    payment_info.delete()
            except:
                pass
            order_payment = Payment.objects.create(

                order=old_orde,
                first_name=first_name,
                last_name=last_name,
                country=country_obj,
                country_code=country_code,
                state=state_obj,
                street_address=street_address,
                post_code=ZIP,
                # by_blance=notes,
                City=city,
                Email_Address=email_address,
                phone=phone,
            )
            # old_orde.is_finished = True
            # old_orde.status = "جارى التنفيذ"
            # old_orde.save()

            if "coupon_id" in request.session.keys():
                del request.session["coupon_id"]

            try:
                blance = float(Profile.objects.get(user=request.user).blance)
            except:
                blance = 0
            order_amount = float(old_orde.amount)
            if Payment.objects.all().filter(order=old_orde):
                payment_info = Payment.objects.get(order=old_orde)
            context = {
                "order": old_orde,
                "payment_info": payment_info,
                "order_details": order_details,
                "PUBLIC_KEY": PUBLIC_KEY,
                "blance": blance,
                "order_amount": order_amount,

            }
            messages.success(
                request, ' Your Billing Details information has been saved')
            return render(request, "orders/shop-checkout.html", context)

    if request.user.is_authenticated and not request.user.is_anonymous:
        # if Order.objects.all().filter(user=request.user, is_finished=False):
        #     order = Order.objects.get(user=request.user, is_finished=False)

        #     order_details = OrderDetails.objects.all().filter(order=order)
        #     blance = Profile.objects.get(user=request.user).blance
        #     context = {
        #         "order": order,
        #         "order_details": order_details,
        #         "PUBLIC_KEY": PUBLIC_KEY,
        #         "blance": blance,

        #     }
        #     return render(request, "orders/payment.html", context)
        return redirect('orders:cart')

    messages.success(request, ' There is no order for you to buy it ')
    return redirect("products:homepage")


def payment_blance(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')

    order = Order.objects.all().filter(user=request.user, is_finished=False)

    if order:
        old_orde = Order.objects.get(user=request.user, is_finished=False)
        Consignee_id = old_orde.user.id
        Consignee_email = old_orde.user.email
        profile = Profile.objects.get(user=request.user)
        if float(old_orde.amount) <= float(profile.blance):
            # print(f"{old_orde.amount} - {profile.blance}")

            # order_payment = Payment.objects.create(

            #     order=old_orde,
            #     by_blance=True
            # )
            payment_method = Payment.objects.get(order=old_orde)
            payment_method.payment_method = "Blance"
            payment_method.save()

            if settings.ARAMEX_USERNAME != "":
                if payment_method.country_code == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                    product_group = "DOM"
                    product_type = "OND"
                else:
                    product_group = "EXP"
                    product_type = "PPX"
                data = {
                    "ClientInfo": {
                        "UserName": f"{settings.ARAMEX_USERNAME}",
                        "Password": f"{settings.ARAMEX_PASSWORD}",
                        "Version": f"{settings.ARAMEX_VERSION}",
                        "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                        "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                        "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                        "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                        "Source": f"{settings.ARAMEX_SOURCE}"

                    },

                    "LabelInfo": {
                        "ReportID": 9201,
                        "ReportType": "URL"
                    },
                    "Shipments": [
                        {
                            "Reference1": f"{old_orde}",
                            "Reference2": "",
                            "Reference3": "",
                            "Shipper": {
                                "Reference1": f"{old_orde}",
                                "Reference2": "",
                                "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                "PartyAddress": {
                                    "Line1": "Oman",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": "Oman",
                                    "StateOrProvinceCode": "",
                                    "PostCode": "",
                                    "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": None,
                                    "BuildingName": None,
                                    "Floor": None,
                                    "Apartment": None,
                                    "POBox": None,
                                    "Description": "alithemes.com product"
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": "alithemes.com store",
                                    "Title": "",
                                    "CompanyName": "alithemes.com",
                                    "PhoneNumber1": "1111111111",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": "1111111111111",
                                    "EmailAddress": "mail@alithemes.com",
                                    "Type": ""
                                }
                            },
                            "Consignee": {
                                "Reference1": f"{Consignee_id}",
                                "Reference2": f"{Consignee_email}",
                                "AccountNumber": f"{Consignee_id}",
                                "PartyAddress": {
                                    "Line1": f"{payment_method.street_address}",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": f"{payment_method.City}",
                                    "StateOrProvinceCode": f"{payment_method.state}",
                                    "PostCode": f"{payment_method.post_code}",
                                    "CountryCode": f"{payment_method.country_code}",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": "",
                                    "BuildingName": "",
                                    "Floor": "",
                                    "Apartment": "",
                                    "POBox": None,
                                    "Description": "Please contact me when the shipment arrives"
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": f"{payment_method.first_name} {payment_method.last_name}",
                                    "Title": f"{payment_method.last_name}",
                                    "CompanyName": "",
                                    "PhoneNumber1": f"{payment_method.phone}",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": f"{payment_method.phone}",
                                    "EmailAddress": f"{payment_method.Email_Address}",
                                    "Type": ""
                                }
                            },
                            "ThirdParty": {
                                "Reference1": "",
                                "Reference2": "",
                                "AccountNumber": "",
                                "PartyAddress": {
                                    "Line1": "",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": "",
                                    "StateOrProvinceCode": "",
                                    "PostCode": "",
                                    "CountryCode": "",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": None,
                                    "BuildingName": None,
                                    "Floor": None,
                                    "Apartment": None,
                                    "POBox": None,
                                    "Description": None
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": "",
                                    "Title": "",
                                    "CompanyName": "",
                                    "PhoneNumber1": "",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": "",
                                    "EmailAddress": "",
                                    "Type": ""
                                }
                            },
                            "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                            "DueDate": str('/Date(' + str(time) + ')/'),
                            "Comments": "",
                            "PickupLocation": "",
                            "OperationsInstructions": "",
                            "AccountingInstrcutions": "",
                            "Details": {
                                "Dimensions": None,
                                "ActualWeight": {
                                    "Unit": "KG",
                                    "Value": float(old_orde.weight)
                                },
                                "ChargeableWeight": None,
                                "DescriptionOfGoods": None,
                                "GoodsOriginCountry": "IN",
                                "NumberOfPieces": 1,
                                "ProductGroup": product_group,
                                "ProductType": product_type,
                                "PaymentType": "P",
                                "PaymentOptions": "",
                                "CustomsValueAmount": None,
                                "CashOnDeliveryAmount": None,
                                "InsuranceAmount": None,
                                "CashAdditionalAmount": None,
                                "CashAdditionalAmountDescription": "",
                                "CollectAmount": None,
                                "Services": "",
                                "Items": []
                            },
                            "Attachments": [],
                            "ForeignHAWB": "",
                            "TransportType ": 0,
                            "PickupGUID": "",
                            "Number": None,
                            "ScheduledDelivery": None
                        }
                    ],
                    "Transaction": None

                }

                url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
                r = requests.post(url, json=data)
                soup = BeautifulSoup(r.content, 'html.parser')
                # print(soup)
                old_orde.tracking_no = soup.id.string
                old_orde.rpt_cache = soup.labelurl.string

            old_orde.is_finished = True
            old_orde.status = "Underway"
            old_orde.save()
            profile.blance = float(profile.blance) - float(old_orde.amount)
            profile.save()

            obj_order_suppliers = OrderSupplier.objects.all().filter(
                user=request.user, order=old_orde)
            for obj_order_supplier in obj_order_suppliers:
                # order_details__supplier = OrderDetailsSupplier.objects.all().filter(
                #     order_supplier=obj_order_supplier, order=old_orde)
                # f_total = 0
                # w_total = 0
                # weight = 0
                # for sub in order_details__supplier:
                #     f_total += sub.price * sub.quantity
                #     w_total += sub.weight * sub.quantity
                #     total = f_total
                #     weight = w_total
                supplier = Profile.objects.get(id=obj_order_supplier.vendor.id)
                supplier.blance = float(
                    supplier.blance) + float(obj_order_supplier.amount)
                supplier.save()

            if "coupon_id" in request.session.keys():
                del request.session["coupon_id"]
            # messages.success(
            #     request, ' Great, you have completed your purchase, we will work to complete your order from our side')

            return redirect("orders:success")
        else:
            messages.warning(
                request, 'You do not have enough credit to purchase this product')
            return redirect("orders:payment")
    messages.warning(request, ' There is no order for you to buy it')
    return redirect("home:index")


def payment_cash(request):
    if not request.user.is_authenticated and request.user.is_anonymous:
        return redirect('accounts:login')

    order = Order.objects.all().filter(user=request.user, is_finished=False)

    if order:
        old_orde = Order.objects.get(user=request.user, is_finished=False)
        Consignee_id = old_orde.user.id
        Consignee_email = old_orde.user.email
        profile = Profile.objects.get(user=request.user)

        payment_method = Payment.objects.get(order=old_orde)
        payment_method.payment_method = "Cash"
        payment_method.save()

        if settings.ARAMEX_USERNAME != "":
            if payment_method.country_code == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                product_group = "DOM"
                product_type = "OND"
            else:
                product_group = "EXP"
                product_type = "PPX"
            data = {
                "ClientInfo": {
                    "UserName": f"{settings.ARAMEX_USERNAME}",
                    "Password": f"{settings.ARAMEX_PASSWORD}",
                    "Version": f"{settings.ARAMEX_VERSION}",
                    "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                    "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                    "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                    "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                    "Source": f"{settings.ARAMEX_SOURCE}"

                },

                "LabelInfo": {
                    "ReportID": 9201,
                    "ReportType": "URL"
                },
                "Shipments": [
                    {
                        "Reference1": f"{old_orde}",
                        "Reference2": "",
                        "Reference3": "",
                        "Shipper": {
                            "Reference1": f"{old_orde}",
                            "Reference2": "",
                            "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                            "PartyAddress": {
                                "Line1": "Oman",
                                "Line2": "",
                                "Line3": "",
                                "City": "Oman",
                                "StateOrProvinceCode": "",
                                "PostCode": "",
                                "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                "Longitude": 0,
                                "Latitude": 0,
                                "BuildingNumber": None,
                                "BuildingName": None,
                                "Floor": None,
                                "Apartment": None,
                                "POBox": None,
                                "Description": "alithemes.com product"
                            },
                            "Contact": {
                                "Department": "",
                                "PersonName": "alithemes.com store",
                                "Title": "",
                                "CompanyName": "alithemes.com",
                                "PhoneNumber1": "1111111111",
                                "PhoneNumber1Ext": "",
                                "PhoneNumber2": "",
                                "PhoneNumber2Ext": "",
                                "FaxNumber": "",
                                "CellPhone": "1111111111111",
                                "EmailAddress": "mail@alithemes.com",
                                "Type": ""
                            }
                        },
                        "Consignee": {
                            "Reference1": f"{Consignee_id}",
                            "Reference2": f"{Consignee_email}",
                            "AccountNumber": f"{Consignee_id}",
                            "PartyAddress": {
                                "Line1": f"{payment_method.street_address}",
                                "Line2": "",
                                "Line3": "",
                                "City": f"{payment_method.City}",
                                "StateOrProvinceCode": f"{payment_method.state}",
                                "PostCode": f"{payment_method.post_code}",
                                "CountryCode": f"{payment_method.country_code}",
                                "Longitude": 0,
                                "Latitude": 0,
                                "BuildingNumber": "",
                                "BuildingName": "",
                                "Floor": "",
                                "Apartment": "",
                                "POBox": None,
                                "Description": "Please contact me when the shipment arrives"
                            },
                            "Contact": {
                                "Department": "",
                                "PersonName": f"{payment_method.first_name} {payment_method.last_name}",
                                "Title": f"{payment_method.last_name}",
                                "CompanyName": "",
                                "PhoneNumber1": f"{payment_method.phone}",
                                "PhoneNumber1Ext": "",
                                "PhoneNumber2": "",
                                "PhoneNumber2Ext": "",
                                "FaxNumber": "",
                                "CellPhone": f"{payment_method.phone}",
                                "EmailAddress": f"{payment_method.Email_Address}",
                                "Type": ""
                            }
                        },
                        "ThirdParty": {
                            "Reference1": "",
                            "Reference2": "",
                            "AccountNumber": "",
                            "PartyAddress": {
                                "Line1": "",
                                "Line2": "",
                                "Line3": "",
                                "City": "",
                                "StateOrProvinceCode": "",
                                "PostCode": "",
                                "CountryCode": "",
                                "Longitude": 0,
                                "Latitude": 0,
                                "BuildingNumber": None,
                                "BuildingName": None,
                                "Floor": None,
                                "Apartment": None,
                                "POBox": None,
                                "Description": None
                            },
                            "Contact": {
                                "Department": "",
                                "PersonName": "",
                                "Title": "",
                                "CompanyName": "",
                                "PhoneNumber1": "",
                                "PhoneNumber1Ext": "",
                                "PhoneNumber2": "",
                                "PhoneNumber2Ext": "",
                                "FaxNumber": "",
                                "CellPhone": "",
                                "EmailAddress": "",
                                "Type": ""
                            }
                        },
                        "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                        "DueDate": str('/Date(' + str(time) + ')/'),
                        "Comments": "",
                        "PickupLocation": "",
                        "OperationsInstructions": "",
                        "AccountingInstrcutions": "",
                        "Details": {
                            "Dimensions": None,
                            "ActualWeight": {
                                "Unit": "KG",
                                "Value": float(old_orde.weight)
                            },
                            "ChargeableWeight": None,
                            "DescriptionOfGoods": None,
                            "GoodsOriginCountry": "IN",
                            "NumberOfPieces": 1,
                            "ProductGroup": product_group,
                            "ProductType": product_type,
                            "PaymentType": "P",
                            "PaymentOptions": "",
                            "CustomsValueAmount": None,
                            "CashOnDeliveryAmount": None,
                            "InsuranceAmount": None,
                            "CashAdditionalAmount": None,
                            "CashAdditionalAmountDescription": "",
                            "CollectAmount": None,
                            "Services": "",
                            "Items": []
                        },
                        "Attachments": [],
                        "ForeignHAWB": "",
                        "TransportType ": 0,
                        "PickupGUID": "",
                        "Number": None,
                        "ScheduledDelivery": None
                    }
                ],
                "Transaction": None

            }

            url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
            r = requests.post(url, json=data)
            soup = BeautifulSoup(r.content, 'html.parser')
            old_orde.tracking_no = soup.id.string
            old_orde.rpt_cache = soup.labelurl.string

        old_orde.is_finished = True
        old_orde.status = "Underway"
        old_orde.save()
        # code for set supplier's balance
        # order_details = OrderDetails.objects.all().filter(order=old_orde)
        # for order_detail in order_details:
        # item_supplier_details = OrderDetailsSupplier.objects.all().filter(
        #     order=old_orde)
        # for item_supplier in item_supplier_details:
        obj_order_suppliers = OrderSupplier.objects.all().filter(
            user=request.user, order=old_orde)
        for obj_order_supplier in obj_order_suppliers:
            # order_details__supplier = OrderDetailsSupplier.objects.all().filter(
            #     order_supplier=obj_order_supplier, order=old_orde)
            # f_total = 0
            # w_total = 0
            # weight = 0
            # for sub in order_details__supplier:
            #     f_total += sub.price * sub.quantity
            #     w_total += sub.weight * sub.quantity
            #     total = f_total
            #     weight = w_total
            supplier = Profile.objects.get(id=obj_order_supplier.vendor.id)
            supplier.blance = float(
                supplier.blance) + float(obj_order_supplier.amount)
            supplier.save()

        if "coupon_id" in request.session.keys():
            del request.session["coupon_id"]
        # messages.success(
        #     request, 'Great, you have completed your purchase, we will work to complete your order from our side')

        return redirect("orders:success")

    # return redirect("orders:payment")
    messages.warning(request, ' There is no order for you to buy it ')
    # return redirect("products:homepage")
    return redirect('home:index')


stripe.api_key = settings.STRIPE_SECRET_KEY


def create_checkout_session(request):
    # product_id = self.kwargs["pk"]
    #     product = Product.objects.get(id=product_id)
    domain = f"https://{settings.YOUR_DOMAIN}/"
    order = Order.objects.get(user=request.user, is_finished=False)
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': int(float(order.amount) * 100),
                        'product_data': {
                            'name': f"Order Number :{order.id}",
                            'images': [
                                'https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e/Chevrolet-logo.png/2560px-Chevrolet-logo.png'],
                        },
                    },
                    'quantity': 1,
                },
            ],
            metadata={
                "order_id": order.id,

            },
            mode='payment',
            success_url=domain + 'order/success/',
            cancel_url=domain + 'orders/cancel/',
        )
        return JsonResponse({
            'id': checkout_session.id
        })
    except Exception as e:
        send_mail(
            'Order  has not been completed , ',
            ' {}'.format(e),
            f'{settings.EMAIL_SENDGRID}',
            ['mafia.shooter1996@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse(str(e))


@require_POST
@csrf_exempt
def my_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # print(" Invalid payload")
        send_mail(
            'Order  has not been completed , Invalid payload',
            ' {}'.format(e),
            f'{settings.EMAIL_SENDGRID}',
            ['mafia.shooter1996@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError as e:
        # print("Invalid signature")
        send_mail(
            'Order  has not been completed , Invalid signature',
            ' {}'.format(e),
            f'{settings.EMAIL_SENDGRID}',
            ['mafia.shooter1996@gmail.com'],
            fail_silently=False,
        )
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        if session.payment_status == "paid":
            customer_email = session["customer_details"]["email"]
            order_id = session["metadata"]["order_id"]
            request.session['order_id'] = order_id

            order = Order.objects.all().filter(id=order_id, is_finished=False)

            if order:
                old_orde = Order.objects.get(id=order_id, is_finished=False)
                Consignee_id = old_orde.user.id
                Consignee_email = old_orde.user.email
                payment_method = Payment.objects.get(order=old_orde)
                payment_method.payment_method = "Stripe"
                payment_method.save()

                if settings.ARAMEX_USERNAME != "":
                    if payment_method.country_code == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                        product_group = "DOM"
                        product_type = "OND"
                    else:
                        product_group = "EXP"
                        product_type = "PPX"
                    data = {
                        "ClientInfo": {
                            "UserName": f"{settings.ARAMEX_USERNAME}",
                            "Password": f"{settings.ARAMEX_PASSWORD}",
                            "Version": f"{settings.ARAMEX_VERSION}",
                            "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                            "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                            "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                            "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                            "Source": f"{settings.ARAMEX_SOURCE}"

                        },

                        "LabelInfo": {
                            "ReportID": 9201,
                            "ReportType": "URL"
                        },
                        "Shipments": [
                            {
                                "Reference1": f"{old_orde}",
                                "Reference2": "",
                                "Reference3": "",
                                "Shipper": {
                                    "Reference1": f"{old_orde}",
                                    "Reference2": "",
                                    "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                    "PartyAddress": {
                                        "Line1": "Oman",
                                        "Line2": "",
                                        "Line3": "",
                                        "City": "Oman",
                                        "StateOrProvinceCode": "",
                                        "PostCode": "",
                                        "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                        "Longitude": 0,
                                        "Latitude": 0,
                                        "BuildingNumber": None,
                                        "BuildingName": None,
                                        "Floor": None,
                                        "Apartment": None,
                                        "POBox": None,
                                        "Description": "alithemes.com product"
                                    },
                                    "Contact": {
                                        "Department": "",
                                        "PersonName": "alithemes.com store",
                                        "Title": "",
                                        "CompanyName": "alithemes.com",
                                        "PhoneNumber1": "1111111111",
                                        "PhoneNumber1Ext": "",
                                        "PhoneNumber2": "",
                                        "PhoneNumber2Ext": "",
                                        "FaxNumber": "",
                                        "CellPhone": "1111111111111",
                                        "EmailAddress": "mail@alithemes.com",
                                        "Type": ""
                                    }
                                },
                                "Consignee": {
                                    "Reference1": f"{Consignee_id}",
                                    "Reference2": f"{Consignee_email}",
                                    "AccountNumber": f"{Consignee_id}",
                                    "PartyAddress": {
                                        "Line1": f"{payment_method.street_address}",
                                        "Line2": "",
                                        "Line3": "",
                                        "City": f"{payment_method.City}",
                                        "StateOrProvinceCode": f"{payment_method.state}",
                                        "PostCode": f"{payment_method.post_code}",
                                        "CountryCode": f"{payment_method.country_code}",
                                        "Longitude": 0,
                                        "Latitude": 0,
                                        "BuildingNumber": "",
                                        "BuildingName": "",
                                        "Floor": "",
                                        "Apartment": "",
                                        "POBox": None,
                                        "Description": "Please contact me when the shipment arrives"
                                    },
                                    "Contact": {
                                        "Department": "",
                                        "PersonName": f"{payment_method.first_name} {payment_method.last_name}",
                                        "Title": f"{payment_method.last_name}",
                                        "CompanyName": "",
                                        "PhoneNumber1": f"{payment_method.phone}",
                                        "PhoneNumber1Ext": "",
                                        "PhoneNumber2": "",
                                        "PhoneNumber2Ext": "",
                                        "FaxNumber": "",
                                        "CellPhone": f"{payment_method.phone}",
                                        "EmailAddress": f"{payment_method.Email_Address}",
                                        "Type": ""
                                    }
                                },
                                "ThirdParty": {
                                    "Reference1": "",
                                    "Reference2": "",
                                    "AccountNumber": "",
                                    "PartyAddress": {
                                        "Line1": "",
                                        "Line2": "",
                                        "Line3": "",
                                        "City": "",
                                        "StateOrProvinceCode": "",
                                        "PostCode": "",
                                        "CountryCode": "",
                                        "Longitude": 0,
                                        "Latitude": 0,
                                        "BuildingNumber": None,
                                        "BuildingName": None,
                                        "Floor": None,
                                        "Apartment": None,
                                        "POBox": None,
                                        "Description": None
                                    },
                                    "Contact": {
                                        "Department": "",
                                        "PersonName": "",
                                        "Title": "",
                                        "CompanyName": "",
                                        "PhoneNumber1": "",
                                        "PhoneNumber1Ext": "",
                                        "PhoneNumber2": "",
                                        "PhoneNumber2Ext": "",
                                        "FaxNumber": "",
                                        "CellPhone": "",
                                        "EmailAddress": "",
                                        "Type": ""
                                    }
                                },
                                "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                                "DueDate": str('/Date(' + str(time) + ')/'),
                                "Comments": "",
                                "PickupLocation": "",
                                "OperationsInstructions": "",
                                "AccountingInstrcutions": "",
                                "Details": {
                                    "Dimensions": None,
                                    "ActualWeight": {
                                        "Unit": "KG",
                                        "Value": float(old_orde.weight)
                                    },
                                    "ChargeableWeight": None,
                                    "DescriptionOfGoods": None,
                                    "GoodsOriginCountry": "IN",
                                    "NumberOfPieces": 1,
                                    "ProductGroup": product_group,
                                    "ProductType": product_type,
                                    "PaymentType": "P",
                                    "PaymentOptions": "",
                                    "CustomsValueAmount": None,
                                    "CashOnDeliveryAmount": None,
                                    "InsuranceAmount": None,
                                    "CashAdditionalAmount": None,
                                    "CashAdditionalAmountDescription": "",
                                    "CollectAmount": None,
                                    "Services": "",
                                    "Items": []
                                },
                                "Attachments": [],
                                "ForeignHAWB": "",
                                "TransportType ": 0,
                                "PickupGUID": "",
                                "Number": None,
                                "ScheduledDelivery": None
                            }
                        ],
                        "Transaction": None

                    }

                    url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
                    r = requests.post(url, json=data)
                    # print(type(r.content) )
                    soup = BeautifulSoup(r.content, 'html.parser')
                    # print(soup)
                    old_orde.tracking_no = soup.id.string
                    old_orde.rpt_cache = soup.labelurl.string

                # delete available
                products_details = OrderLine.objects.all().filter(order=old_orde)
                for pro in products_details:
                    product_order = Product.objects.get(
                        id=pro.product.id)
                    if product_order.available > 0:
                        product_order.available = product_order.available - pro.quantity
                        product_order.save()

                old_orde.is_finished = True
                old_orde.status = "Underway"
                old_orde.save()

                # code for set supplier's balance
                obj_order_suppliers = OrderSupplier.objects.all().filter(order=old_orde)
                for obj_order_supplier in obj_order_suppliers:
                    supplier = Profile.objects.get(
                        id=obj_order_supplier.vendor.id)
                    supplier.blance = float(
                        supplier.blance) + float(obj_order_supplier.amount)
                    supplier.save()

                send_mail(
                    'Great! Order ID{}. has been successfully purchased'.format(
                        order_id),
                    ' we will work to complete your order from our side.',
                    f'{settings.EMAIL_SENDGRID}',
                    [f'{customer_email}'],
                    fail_silently=False,
                )
                if "coupon_id" in request.session.keys():
                    del request.session["coupon_id"]

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        order_id = session["metadata"]["order_id"]
        order = Order.objects.all().filter(id=order_id, is_finished=False)
        request.session['order_id'] = order_id
        if order:
            old_orde = Order.objects.get(id=order_id, is_finished=False)
            Consignee_id = old_orde.user.id
            Consignee_email = old_orde.user.email
            payment_method = Payment.objects.get(order=old_orde)
            payment_method.payment_method = "Stripe"
            payment_method.save()

            if settings.ARAMEX_USERNAME != "":
                if payment_method.country_code == settings.ARAMEX_ACCOUNTCOUNTRYCODE:
                    product_group = "DOM"
                    product_type = "OND"
                else:
                    product_group = "EXP"
                    product_type = "PPX"
                data = {
                    "ClientInfo": {
                        "UserName": f"{settings.ARAMEX_USERNAME}",
                        "Password": f"{settings.ARAMEX_PASSWORD}",
                        "Version": f"{settings.ARAMEX_VERSION}",
                        "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                        "AccountPin": f"{settings.ARAMEX_ACCOUNTPIN}",
                        "AccountEntity": f"{settings.ARAMEX_ACCOUNTENTITY}",
                        "AccountCountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                        "Source": f"{settings.ARAMEX_SOURCE}"

                    },

                    "LabelInfo": {
                        "ReportID": 9201,
                        "ReportType": "URL"
                    },
                    "Shipments": [
                        {
                            "Reference1": f"{old_orde}",
                            "Reference2": "",
                            "Reference3": "",
                            "Shipper": {
                                "Reference1": f"{old_orde}",
                                "Reference2": "",
                                "AccountNumber": f"{settings.ARAMEX_ACCOUNTNUMBER}",
                                "PartyAddress": {
                                    "Line1": "Oman",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": "Oman",
                                    "StateOrProvinceCode": "",
                                    "PostCode": "",
                                    "CountryCode": f"{settings.ARAMEX_ACCOUNTCOUNTRYCODE}",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": None,
                                    "BuildingName": None,
                                    "Floor": None,
                                    "Apartment": None,
                                    "POBox": None,
                                    "Description": "alithemes.com product"
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": "alithemes.com store",
                                    "Title": "",
                                    "CompanyName": "alithemes.com",
                                    "PhoneNumber1": "1111111111",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": "1111111111111",
                                    "EmailAddress": "mail@alithemes.com",
                                    "Type": ""
                                }
                            },
                            "Consignee": {
                                "Reference1": f"{Consignee_id}",
                                "Reference2": f"{Consignee_email}",
                                "AccountNumber": f"{Consignee_id}",
                                "PartyAddress": {
                                    "Line1": f"{payment_method.street_address}",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": f"{payment_method.City}",
                                    "StateOrProvinceCode": f"{payment_method.state}",
                                    "PostCode": f"{payment_method.post_code}",
                                    "CountryCode": f"{payment_method.country_code}",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": "",
                                    "BuildingName": "",
                                    "Floor": "",
                                    "Apartment": "",
                                    "POBox": None,
                                    "Description": "Please contact me when the shipment arrives"
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": f"{payment_method.first_name} {payment_method.last_name}",
                                    "Title": f"{payment_method.last_name}",
                                    "CompanyName": "",
                                    "PhoneNumber1": f"{payment_method.phone}",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": f"{payment_method.phone}",
                                    "EmailAddress": f"{payment_method.Email_Address}",
                                    "Type": ""
                                }
                            },
                            "ThirdParty": {
                                "Reference1": "",
                                "Reference2": "",
                                "AccountNumber": "",
                                "PartyAddress": {
                                    "Line1": "",
                                    "Line2": "",
                                    "Line3": "",
                                    "City": "",
                                    "StateOrProvinceCode": "",
                                    "PostCode": "",
                                    "CountryCode": "",
                                    "Longitude": 0,
                                    "Latitude": 0,
                                    "BuildingNumber": None,
                                    "BuildingName": None,
                                    "Floor": None,
                                    "Apartment": None,
                                    "POBox": None,
                                    "Description": None
                                },
                                "Contact": {
                                    "Department": "",
                                    "PersonName": "",
                                    "Title": "",
                                    "CompanyName": "",
                                    "PhoneNumber1": "",
                                    "PhoneNumber1Ext": "",
                                    "PhoneNumber2": "",
                                    "PhoneNumber2Ext": "",
                                    "FaxNumber": "",
                                    "CellPhone": "",
                                    "EmailAddress": "",
                                    "Type": ""
                                }
                            },
                            "ShippingDateTime": str('/Date(' + str(time) + ')/'),
                            "DueDate": str('/Date(' + str(time) + ')/'),
                            "Comments": "",
                            "PickupLocation": "",
                            "OperationsInstructions": "",
                            "AccountingInstrcutions": "",
                            "Details": {
                                "Dimensions": None,
                                "ActualWeight": {
                                    "Unit": "KG",
                                    "Value": float(old_orde.weight)
                                },
                                "ChargeableWeight": None,
                                "DescriptionOfGoods": None,
                                "GoodsOriginCountry": "IN",
                                "NumberOfPieces": 1,
                                "ProductGroup": product_group,
                                "ProductType": product_type,
                                "PaymentType": "P",
                                "PaymentOptions": "",
                                "CustomsValueAmount": None,
                                "CashOnDeliveryAmount": None,
                                "InsuranceAmount": None,
                                "CashAdditionalAmount": None,
                                "CashAdditionalAmountDescription": "",
                                "CollectAmount": None,
                                "Services": "",
                                "Items": []
                            },
                            "Attachments": [],
                            "ForeignHAWB": "",
                            "TransportType ": 0,
                            "PickupGUID": "",
                            "Number": None,
                            "ScheduledDelivery": None
                        }
                    ],
                    "Transaction": None

                }

                url = 'https://ws.aramex.net/ShippingAPI.V2/Shipping/Service_1_0.svc/json/CreateShipments'
                r = requests.post(url, json=data)
                # print(type(r.content) )
                soup = BeautifulSoup(r.content, 'html.parser')
                # print(soup)
                old_orde.tracking_no = soup.id.string
                old_orde.rpt_cache = soup.labelurl.string

            # delete available
            products_details = OrderLine.objects.all().filter(order=old_orde)
            for pro in products_details:
                product_order = Product.objects.get(
                    id=pro.product.id)
                if product_order.available > 0:
                    product_order.available = product_order.available - pro.quantity
                    product_order.save()

            old_orde.is_finished = True
            old_orde.status = "Underway"
            old_orde.save()

            # code for set supplier's balance
            obj_order_suppliers = OrderSupplier.objects.all().filter(order=old_orde)
            for obj_order_supplier in obj_order_suppliers:
                supplier = Profile.objects.get(
                    id=obj_order_supplier.vendor.id)
                supplier.blance = float(
                    supplier.blance) + float(obj_order_supplier.amount)
                supplier.save()

            send_mail(
                'Order ID {}. has been successfully purchased'.format(
                    order_id),
                ' we will work to complete your order from our side.',
                f'{settings.EMAIL_SENDGRID}',
                [f'{customer_email}'],
                fail_silently=False,
            )

            if "coupon_id" in request.session.keys():
                del request.session["coupon_id"]

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']
        customer_email = session["customer_details"]["email"]
        order_id = session["metadata"]["order_id"]
        request.session['order_id'] = order_id

        send_mail(
            'Order NO. {}. has not been completed , payment_failed'.format(
                order_id),
            f'{settings.EMAIL_SENDGRID}',
            [f'{customer_email}'],
            fail_silently=False,
        )

    # Send an email to the customer asking them to retry their order

    return HttpResponse(status=200)


def success(request):
    if not request.session.has_key('currency'):
        request.session['currency'] = settings.DEFAULT_CURRENCY

    order_id = request.session.get("order_id")
    order = Order.objects.all().filter(
        user=request.user, id=order_id, is_finished=True)
    # print(order_id)
    if order:
        order_success = Order.objects.get(
            user=request.user, id=order_id, is_finished=True)
        order_details_success = OrderLine.objects.filter(
            order=order_success)
        payment_info = Payment.objects.get(order=order_success)
        # print(payment_info)
        context = {
            "order_success": order_success,
            "order_details_success": order_details_success,
            "payment_info": payment_info,
        }
        send_mail(
            'Order No {}. has been successfully purchased'.format(
                order_id),
            ' we will work to complete your order from our side.',
            f'{settings.EMAIL_SENDGRID}',
            [f'{payment_info.Email_Address}', f'{request.user.email}'],
            fail_silently=False,
        )
        messages.success(
            request, ' Great!, you have completed your purchase, we will work to complete your order from our side')
        return render(request, "orders/success.html", context)
    else:
        send_mail(
            'Order id {}. has not been completed'.format(
                order_id),
            'Sorry, the payment has not been completed. Please contact technical support. It is very important.',
            f'{settings.EMAIL_SENDGRID}',
            [f'{request.user.email}', ],
            fail_silently=False,
        )
        messages.success(
            request,
            ' Sorry, the payment has not been completed. Please contact technical support. It is very important')
        return redirect('orders:cancel')


class CancelView(TemplateView):
    template_name = "orders/cancel.html"
