from django.shortcuts import render, get_object_or_404
from utlis.archive import BasicArchiveView
from .models import Product, ProductImage, ProductRating ,Category
from django.http import JsonResponse
from project import settings
from django.db.models import Sum
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.models import Profile
from .serializers import ProductSerializer, ProductRatingSerializer, ProductRatingVendorSerializer, \
    ProductRatingVendorUpdateSerializer,CategorySerializer
from rest_framework import generics
from django.db.models import Q
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from .permissions import IsVendor, IsCustomer, IsOwner

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
# Create your views here.


class CategoryList(ListCreateAPIView):
    queryset = Category.objects.root_nodes()
    serializer_class = CategorySerializer


class CategoryDetail(RetrieveUpdateDestroyAPIView):
    # permission_classes = (IsOwnerOrReadOnly,)
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ListProductAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    # def get_queryset(self, *args, **kwargs):
    #
    #     if self.request.GET.get('vendor_id') is None:
    #         return Product.objects.filter(PRDISactive=True)
    #     try:
    #         vendor_id_query = self.request.GET.get('vendor_id')
    #         user = Profile.objects.get(id=vendor_id_query)
    #         return Product.objects.filter(Q(product_vendor=user) & Q(PRDISactive=True))
    #     except:
    #         raise NotFound(detail="Not found", code=404)


class RetrieveProductAPIView(generics.RetrieveAPIView):
    """This endpoint allows to get product by id"""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer



class ListProductAPIView(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self, *args, **kwargs):
        if self.request.GET.get('vendor_id') is None:
            return Product.objects.filter(Q(status='published') & Q(archived=False)).order_by('-id')
        try:
            vendor_id_query = self.request.GET.get('vendor_id')
            user = Profile.objects.get(id=vendor_id_query)
            return Product.objects.filter(Q(product_vendor=user) & Q(status='published') & Q(archived=False)).order_by(
                '-id')
        except:
            raise NotFound(detail="Not found", code=404)


class RetrieveProductAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(Q(status='published') & Q(archived=False))
    serializer_class = ProductSerializer


class CreateProductAPIView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated, IsVendor)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        serializer.save(product_vendor=self.request.user.profile_user)


class UpdateProductAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = (IsAuthenticated, IsVendor, IsOwner)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class DeleteProductAPIView(BasicArchiveView):
    model = Product
    permission_classes = (IsAuthenticated, IsVendor, IsOwner)


class VendorProductList(generics.ListCreateAPIView):
    model = Product
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, IsVendor)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user.profile_user
        return Product.objects.filter(product_vendor=user).order_by('-id')


class VendorProductDetails(generics.RetrieveAPIView):
    model = Product
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated, IsVendor)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user.profile_user
        return Product.objects.filter(product_vendor=user)


class ProductRatingList(generics.ListAPIView):
    serializer_class = ProductRatingSerializer
    model = ProductRating

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductRating.objects.filter(Q(product=product_id) & Q(active=True)).order_by('-rating_date')


class ProductRatingCreate(generics.CreateAPIView):
    serializer_class = ProductRatingSerializer
    model = ProductRating
    permission_classes = (IsAuthenticated, IsCustomer)
    queryset = ProductRating.objects.filter(active=True)

    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        product = Product.objects.get(id=product_id)
        serializer.save(client_name=self.request.user.profile_user)
        serializer.save(product=product)


class ProductRatingDetail(generics.RetrieveAPIView):
    serializer_class = ProductRatingSerializer
    model = ProductRating
    queryset = ProductRating.objects.filter(active=True)


class ProductRatingDelete(generics.DestroyAPIView):
    serializer_class = ProductRatingSerializer
    model = ProductRating
    permission_classes = (IsAuthenticated, IsCustomer)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user.profile_user
        return ProductRating.objects.filter(Q(client_name=user) & Q(active=True))


class VendorProductRatingList(generics.ListAPIView):
    model = ProductRating
    serializer_class = ProductRatingVendorSerializer
    permission_classes = (IsAuthenticated, IsVendor)

    def get_queryset(self, *args, **kwargs):
        user = self.request.user.profile_user
        product_id = self.kwargs['product_id']
        return ProductRating.objects.order_by('-rating_date').filter(Q(vendor=user) & Q(product=product_id))


class VendorProductRatingDetail(generics.RetrieveUpdateDestroyAPIView):
    model = ProductRating
    serializer_class = ProductRatingVendorSerializer

    def get_serializer_class(self):
        serializer_class = self.serializer_class
        if self.request.method == 'PUT':
            serializer_class = ProductRatingVendorUpdateSerializer
        return serializer_class

    def get_queryset(self, *args, **kwargs):
        user = self.request.user.profile_user
        product_id = self.kwargs['product_id']
        return ProductRating.objects.order_by('-rating_date').filter(Q(vendor=user) & Q(product=product_id))

# def product_details(request, slug):
#     if not request.session.has_key('currency'):
#         request.session['currency'] = settings.DEFAULT_CURRENCY
#
#     product_detail = get_object_or_404(Product, PRDSlug=slug, PRDISactive=True)
#     product_image = ProductImage.objects.all().filter(PRDIProduct=product_detail)
#     related_products_minicategor = product_detail.product_minicategor
#     related_products = Product.objects.all().filter(
#         product_minicategor=related_products_minicategor, PRDISactive=True)
#     supplier_Products = Product.objects.all().filter(product_vendor=product_detail.product_vendor,
#                                                      product_minicategor=related_products_minicategor, PRDISactive=True)
#
#     # related = ProductAlternative.objects.all().filter(PALNProduct=product_detail)
#     # related_products = product_detail.alternative_products.all()
#
#     product_feedback = ProductRating.objects.all().filter(
#         PRDIProduct=product_detail, active=True)
#     feedback_sum = ProductRating.objects.all().filter(
#         PRDIProduct=product_detail, active=True).aggregate(Sum('rate'))
#     feedbak_number = product_feedback.count()
#
#     try:
#
#         average_rating = int(feedback_sum["rate__sum"]) / feedbak_number
#
#         start_1_sum = ProductRating.objects.all().filter(
#             PRDIProduct=product_detail, active=True, rate=1).count()
#
#         start_2_sum = ProductRating.objects.all().filter(
#             PRDIProduct=product_detail, active=True, rate=2).count()
#
#         start_3_sum = ProductRating.objects.all().filter(
#             PRDIProduct=product_detail, active=True, rate=3).count()
#
#         start_4_sum = ProductRating.objects.all().filter(
#             PRDIProduct=product_detail, active=True, rate=4).count()
#
#         start_5_sum = ProductRating.objects.all().filter(
#             PRDIProduct=product_detail, active=True, rate=5).count()
#
#         start_1 = (start_1_sum / feedbak_number) * 100
#         start_2 = (start_2_sum / feedbak_number) * 100
#         start_3 = (start_3_sum / feedbak_number) * 100
#         start_4 = (start_4_sum / feedbak_number) * 100
#         start_5 = (start_5_sum / feedbak_number) * 100
#
#     except:
#         average_rating = 0
#         start_1 = 0
#         start_2 = 0
#         start_3 = 0
#         start_4 = 0
#         start_5 = 0
#
#     context = {
#         'product_detail': product_detail,
#         'product_image': product_image,
#         'related_products': related_products,
#         'supplier_Products': supplier_Products,
#         # 'related_products': related_products,
#         'product_feedback': product_feedback,
#         'average_rating': average_rating,
#         'feedbak_number': feedbak_number,
#         "start_1": start_1,
#         "start_2": start_2,
#         "start_3": start_3,
#         "start_4": start_4,
#         "start_5": start_5,
#
#     }
#     return render(request, 'products/shop-product-vendor.html', context)
#
#
# def product_search(request):
#     context = None
#     if not request.session.has_key('currency'):
#         request.session['currency'] = settings.DEFAULT_CURRENCY
#
#     if request.method == 'POST':
#         try:
#             word = request.POST['search-product']
#         except:
#             word = "a"
#         request.session["search_product"] = word
#
#         try:
#             category_select = request.POST['category-select']
#         except:
#             category_select = "All Categories"
#         request.session["search_category_select"] = category_select
#
#         if category_select == "All Categories":
#             qs = Product.objects.all().filter(
#                 product_name__icontains=word, PRDISDeleted=False, PRDISactive=True)
#             request.session["products_count"] = qs.count()
#             paginator = Paginator(qs, 12)
#             page = request.GET.get('page')
#             try:
#                 qs = paginator.page(page)
#             except PageNotAnInteger:
#                 qs = paginator.page(1)
#             except EmptyPage:
#                 qs = paginator.page(paginator.num_page)
#             print("page:", page)
#         else:
#             qs = Product.objects.all().filter(
#                 product_name__icontains=word, PRDISDeleted=False, PRDISactive=True,
#                 product_supercategory__name=category_select)
#             request.session["products_count"] = qs.count()
#             paginator = Paginator(qs, 12)
#             page = request.GET.get('page')
#             try:
#                 qs = paginator.page(page)
#             except PageNotAnInteger:
#                 qs = paginator.page(1)
#             except EmptyPage:
#                 qs = paginator.page(paginator.num_page)
#             print("page:", page)
#
#         context = {
#             'qs': qs,
#             'page': page,
#         }
#     # if request.GET.get('page') != "1" :
#     if "search_product" in request.session.keys() and "search_product" in request.session.keys():
#         if request.session["search_category_select"] == "All Categories":
#             qs = Product.objects.all().filter(
#                 product_name__icontains=request.session["search_product"], PRDISDeleted=False, PRDISactive=True)
#
#             paginator = Paginator(qs, 12)
#             page = request.GET.get('page')
#             try:
#                 qs = paginator.page(page)
#             except PageNotAnInteger:
#                 qs = paginator.page(1)
#             except EmptyPage:
#                 qs = paginator.page(paginator.num_page)
#             print("page:", page)
#         else:
#             qs = Product.objects.all().filter(
#                 product_name__icontains=request.session["search_product"], PRDISDeleted=False, PRDISactive=True,
#                 product_supercategory__name=request.session["search_category_select"])
#             # print(qs)
#             paginator = Paginator(qs, 12)
#             page = request.GET.get('page')
#             try:
#                 qs = paginator.page(page)
#             except PageNotAnInteger:
#                 qs = paginator.page(1)
#             except EmptyPage:
#                 qs = paginator.page(paginator.num_page)
#             print("page:", page)
#
#         context = {
#             'qs': qs,
#             'page': page,
#         }
#
#     return render(request, 'products/product-search.html', context)
#
#
# def product_rating(request):
#     if request.method == "POST" and request.user.is_authenticated and not request.user.is_anonymous:
#         product_id = request.POST.get("product_id")
#         product_rate = request.POST.get("product_rate")
#         # print(type(product_rate))
#         message = request.POST.get("client_message")
#         client = Profile.objects.get(user=request.user)
#         if request.is_ajax():
#             product = Product.objects.get(id=product_id)
#
#             if ProductRating.objects.all().filter(PRDIProduct=product, client_name__user=request.user).exists():
#                 old_rating = ProductRating.objects.get(
#                     PRDIProduct=product, client_name__user=request.user)
#                 old_rating.vendor = product.product_vendor
#                 # old_rating.rate = product_rate
#                 old_rating.client_name = client
#                 old_rating.client_comment = message
#                 old_rating.save()
#
#                 product_feedback = ProductRating.objects.all().filter(
#                     PRDIProduct=product, active=True)
#                 feedback_sum = ProductRating.objects.all().filter(
#                     PRDIProduct=product, active=True).aggregate(Sum('rate'))
#                 feedbak_number = product_feedback.count()
#                 try:
#                     if feedback_sum != None or feedback_sum != 0:
#                         average_rating = round((int(feedback_sum["rate__sum"]) / feedbak_number) * 20)
#                         product.feedbak_average = average_rating
#                         product.feedbak_number = feedbak_number
#                         product.save()
#
#                 except:
#                     pass
#
#                 # send_mail(
#                 #     "You received a message from {}".format(name),
#                 #     f'{message}',
#                 #     f'{settings.EMAIL_SENDGRID}',
#                 #     [f'{email}'],
#                 #     fail_silently=False,
#                 # )
#             else:
#                 ProductRating.objects.create(
#                     PRDIProduct=product,
#                     vendor=product.product_vendor,
#                     rate=product_rate,
#                     client_name=client,
#
#                     client_comment=message,
#                 )
#
#                 product_feedback = ProductRating.objects.all().filter(
#                     PRDIProduct=product, active=True)
#                 feedback_sum = ProductRating.objects.all().filter(
#                     PRDIProduct=product, active=True).aggregate(Sum('rate'))
#                 feedbak_number = product_feedback.count()
#                 try:
#                     if feedback_sum != None or feedback_sum != 0:
#                         average_rating = round((int(feedback_sum["rate__sum"]) / feedbak_number * 20))
#                         product.feedbak_average = average_rating
#                         product.feedbak_number = feedbak_number
#                         product.save()
#
#                 except:
#                     product.feedbak_average = int(product_rate) * 20
#                     product.feedbak_number = 1
#                     product.save()
#                     # send_mail(
#                 #     "You received a message from {}".format(name),
#                 #     f'{message}',
#                 #     f'{settings.EMAIL_SENDGRID}',
#                 #     [f'{email}'],
#                 #     fail_silently=False,
#                 # )
#             return JsonResponse({"succes": True, "product_id": product_id, "product_rate": product_rate, }, safe=False)
#         return JsonResponse({"succes": False, }, safe=False)
