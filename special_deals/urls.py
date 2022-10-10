from django.conf.urls import url
from django.urls import path, include
from rest_framework.urlpatterns import format_suffix_patterns
from .views import (
    SpecialDealList,
    SpecialDealDetail,
    SpecialDealAllList,
    SpecialDealItemsList,
    SpecialDealItemsDetail
)

urlpatterns = [
    path('specialDeals-all/', SpecialDealAllList.as_view()),
    path('specialDeals/', SpecialDealList.as_view()),
    path('specialDeals/<int:pk>/', SpecialDealDetail.as_view()),
    path('specialDeals/items/', SpecialDealItemsList.as_view()),
    path('specialDeals/items/<int:pk>/', SpecialDealItemsDetail.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
