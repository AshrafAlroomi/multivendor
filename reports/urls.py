from django.urls import path
from . import views


app_name = 'reports'
urlpatterns = [
    path('merchants/actual-customers/', views.ActualCustomer.as_view(), name='actual-customers'),
    path('merchants/top-ten-items/', views.TopTenProfitableDeals.as_view(), name='top-ten'),
    path('merchants/customers/', views.CustomersView.as_view(), name='customers'),
    path('merchants/total-sales/', views.TotalSalesPerformedMonthly.as_view(), name='total-sales'),
    path('merchants/item-sales/', views.SalesPerItem.as_view(), name='total-sales'),
]

