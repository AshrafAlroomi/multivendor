from django.urls import path
from . import views

app_name = 'orders'
urlpatterns = [
    path('add_to_cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.cart, name='cart'),
    path('cart/<str:country>/', views.StatesJsonListView.as_view(), name="get-states"),
    path('order/remeve-product/<int:productdeatails_id>',views.remove_item, name="remove-item"),
    path('payment/', views.payment, name="payment"),
    path('payment_blance/', views.payment_blance, name="payment-blance"),
    path('payment_cash/', views.payment_cash, name="payment-cash"),
    path('order/cancel/', views.CancelView.as_view(), name='cancel'),
    path('order/success/', views.success, name='success'),
    path('create_checkout_session/', views.create_checkout_session, name='create_checkout_session'),
    path('orders/webhook/', views.my_webhook_view, name='my-webhook'),

    path('orders/', views.ListOrdersAPIView.as_view(), name='orders-list'),
    path('orders/<int:pk>/', views.DetailedOrderAPIView.as_view(), name='order-detail'),
    path('order-line/', views.ListOrderLineAPIView.as_view(), name='order-line-list'),
    path('order-line/<int:pk>/', views.DetailedOrderLineAPIView.as_view(), name='detail-order-line'),
    path('order-line/<int:pk>/update/', views.UpdateOrderLineAPIView.as_view(), name='update-order-line'),
    path('payments/', views.ListPaymentAPIView.as_view(), name='payments-list'),
    path('payments/<int:pk>/', views.DetailedPaymentAPIView.as_view(), name='payments-detail'),
    path('vendors/orders/', views.VendorListOrdersAPIView.as_view(), name='vendor-order-list'),
    path('vendors/orders/<int:pk>/', views.VendorDetailedOrderAPIView.as_view(), name='vendor-order-detail'),

]
