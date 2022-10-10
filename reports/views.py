from rest_framework.views import APIView
from orders.models import OrderLine
from rest_framework.response import Response
from django.db.models import Min, Sum, Value, Count
from django.db.models import Q
import pandas as pd
from .utils import is_valid_date
from django.db.models import F
from django.db import models
from django.db.models.functions import TruncMonth, Cast, Substr, TruncDate, TruncYear
from orders.permissions import IsVendor
from rest_framework.permissions import IsAuthenticated
from rest_framework.settings import api_settings
from django.db.models.functions import ExtractYear


# Create your views here.
class ActualCustomer(APIView):
    model = OrderLine
    permission_classes = (IsAuthenticated, IsVendor)

    def get(self, request, *args, **kwargs):
        filter_by = self.request.GET.get('filter')
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        validated_start_date = is_valid_date(start_date)[0]
        validated_end_date = is_valid_date(end_date)[0]
        vendor = self.request.user.profile_user
        filters = Q(product__product_vendor=vendor) & Q(status='COMPLETE')
        if start_date and end_date:
            filters &= Q(order__order_date__range=[validated_start_date, validated_end_date])
        if filter_by == 'day':
            qs = OrderLine.objects.filter(filters) \
                .annotate(Date=TruncDate('order__order_date')).values("Date").annotate(
                Customers=Count("order__user", distinct=True)).order_by("-Customers")
        elif filter_by == 'month':
            qs = OrderLine.objects.filter(filters) \
                .annotate(month=Substr(
                Cast(TruncMonth('order__order_date', output_field=models.DateField()), output_field=models.CharField()),
                1,
                7)).values("month").annotate(
                Customers=Count("order__user", distinct=True)).order_by("-Customers")
        else:
            qs = OrderLine.objects.filter(filters) \
                .annotate(Year=ExtractYear('order__order_date')).values("Year").annotate(
                Customers=Count("order__user", distinct=True)).order_by("-Customers")

        count = qs.aggregate(T_customers=Sum('Customers'))
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        result = paginator.paginate_queryset(qs, request, view=self)
        return paginator.get_paginated_response({
            'Total customers': count,
            'data': result,
        })


class TopTenProfitableDeals(APIView):
    model = OrderLine
    permission_classes = (IsAuthenticated, IsVendor)

    def get(self, request, *args, **kwargs):
        vendor = self.request.user.profile_user
        qs = OrderLine.objects.filter(Q(product__product_vendor=vendor) & Q(status='COMPLETE')) \
                 .values(Product_id=F('product__id')) \
                 .annotate(Product=Min('product__product_name'),
                           Total_revenue=Sum(F('quantity') * F('price'), output_field=models.FloatField()),
                           Sales=Sum('quantity'), Stock=F('product__stock_quantity'), Price=F('price'),
                           Main_photo=F('product__product_image')) \
                 .order_by('-Total_revenue')[:10]
        return Response(qs)


class CustomersView(APIView):
    model = OrderLine
    permission_classes = (IsAuthenticated, IsVendor)

    def get(self, request, *args, **kwargs):
        vendor = self.request.user.profile_user
        qs = OrderLine.objects.filter(product__product_vendor=vendor).values('order__user').annotate(id=Min('id'))
        queryset = qs.values(Client=F('order__user__username'), Email=F('order__user__email'),
                             Phone_number=F('order__user__profile_user__mobile_number'))
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        result = paginator.paginate_queryset(queryset, request, view=self)
        return paginator.get_paginated_response(result)


class TotalSalesPerformedMonthly(APIView):
    model = OrderLine
    permission_classes = (IsAuthenticated, IsVendor)

    def get(self, request, *args, **kwargs):
        vendor = self.request.user.profile_user
        qs = OrderLine.objects.filter(Q(product__product_vendor=vendor) & Q(status='COMPLETE')).values(Month=Substr(
            Cast(TruncMonth('order__order_date', output_field=models.DateField()), output_field=models.CharField()), 1,
            7)) \
            .annotate(id=Min('id'), Sales=Sum(F('quantity') * F('price'), output_field=models.FloatField())) \
            .order_by('-Month') \
            .values('Month', 'Sales')

        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        result = paginator.paginate_queryset(qs, request, view=self)
        return paginator.get_paginated_response(result)


class SalesPerItem(APIView):
    model = OrderLine
    permission_classes = (IsAuthenticated, IsVendor)

    def get(self, request, *args, **kwargs):
        vendor = self.request.user.profile_user
        date = self.request.GET.get('date')
        validated_date = is_valid_date(date)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')

        filters = Q(product__product_vendor=vendor) & Q(status='COMPLETE')
        if validated_date[2] == 'day':
            filters &= Q(order__order_date__date=validated_date[0])
        elif validated_date[2] == 'month':
            filters &= Q(order__order_date__month=validated_date[0].month) & Q(
                order__order_date__year=validated_date[0].year)
        if start_date and end_date:
            filters &= Q(order__order_date__range=[start_date, end_date])

        qs = OrderLine.objects.filter(filters) \
            .values(Product_id=F('product__id')) \
            .annotate(Product=Min('product__product_name'),
                      Date=Value(validated_date[1], output_field=models.CharField()),
                      Revenue=Sum(F('quantity') * F('price'), output_field=models.FloatField()),
                      Units=Sum('quantity'),
                      ) \
            .order_by('-Revenue')
        pagination_class = api_settings.DEFAULT_PAGINATION_CLASS
        paginator = pagination_class()
        result = paginator.paginate_queryset(qs, request, view=self)
        return paginator.get_paginated_response(result)
