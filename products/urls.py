from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.urls import reverse_lazy

app_name = 'products'
urlpatterns = [
    path("categories", views.CategoryList.as_view(), name="category_list"),
    path("categories/<int:pk>/", views.CategoryDetail.as_view(), name="category_detail"),
    path('products/', views.ListProductAPIView.as_view(), name='products-list'),  # public
    path('products/<int:pk>/', views.RetrieveProductAPIView.as_view(), name='retrieve-product'),  # public
    path('products/create', views.CreateProductAPIView.as_view(), name='create-product'),  # isVendor
    path('products/update/<int:pk>/', views.UpdateProductAPIView.as_view(), name='update-product'),  # isVendor
    path('products/delete/<int:pk>/', views.DeleteProductAPIView.as_view(), name='delete-product'),  # isVendor

    path('vendors/products/', views.VendorProductList.as_view(), name='products-vendor-list'),  # isVendor
    path('vendors/products/<int:pk>/', views.VendorProductDetails.as_view(), name='product-vendor-detail'),  # isVendor

    path('products/<int:product_id>/reviews/', views.ProductRatingList.as_view(), name='reviews-list'),  # public
    path('products/<int:product_id>/reviews/<int:pk>/', views.ProductRatingDetail.as_view(), name='reviews-detail'),
    # public
    path('products/<int:product_id>/reviews/create', views.ProductRatingCreate.as_view(), name='reviews-create'),
    # isCustomer
    path('products/<int:product_id>/reviews/<int:pk>/delete', views.ProductRatingDelete.as_view(), name='reviews-delete'),
    # isCustomer
    path('vendors/products/<int:product_id>/reviews/', views.VendorProductRatingList.as_view(),
         name='reviews-vendor-list'),  # isVendor
    path('vendors/products/<int:product_id>/reviews/<int:pk>/', views.VendorProductRatingDetail.as_view(),
         name='reviews-vendor-list'),  # isVendor

    # path('product/<int:pk>',
    #      views.ProductDelete.as_view(), name='product-del'),

]
# urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
