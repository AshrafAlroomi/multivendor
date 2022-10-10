from django.db import models
from categories.models import SubCategory, MainCategory, SuperCategory, MiniCategory
from django.utils.text import slugify
from django.urls import reverse
from .utils import code_generator, create_shortcode
from django.db.models.signals import pre_save
from django.utils.safestring import mark_safe
from django.core.validators import MinValueValidator, MaxValueValidator
from io import BytesIO
from PIL import Image
from django.core.files import File
from django.conf import settings
try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField
from accounts.models import Profile
from utlis.archive import ArchiveModel, ArchiveDeleter
from djmoney.models.fields import MoneyField

# Create your models here.


from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=50, unique=True)
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    category_image = models.ImageField(
        upload_to='categories/imgs/', verbose_name=_("Category Image"), blank=True, null=True,
        help_text=_("Please use our recommended dimensions: 120px X 120px"))
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_update = models.DateTimeField(auto_now=True, blank=True, null=True)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name




def compress(image):
    im = Image.open(image)
    # create a BytesIO object
    im_io = BytesIO()
    if im.mode in ("RGBA", "P"):
        im = im.convert("RGB")
    if im.width > 1100 or im.height > 1100:
        out_size = (1100, 1100)
        im.thumbnail(out_size)
    # save image to BytesIO object
    im.save(im_io, format="webp", quality=20, optimize=True)
    # create a django-friendly Files object
    new_image = File(im_io, name=image.name)
    return new_image


class Product(ArchiveDeleter, ArchiveModel, models.Model):
    category = TreeForeignKey('Category', null=True, blank=True, on_delete=models.CASCADE, )
    product_vendor = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name=_("Product Vendor"), limit_choices_to={'status': 'vendor'},
        related_name='product_vendor')
    product_name = models.CharField(max_length=150, verbose_name=_("Name"))
    short_description = models.TextField(verbose_name=_("Short Description"))
    description = RichTextField(blank=True, null=True,
                                        verbose_name=_("Full Description"))

    product_image = models.ImageField(
        upload_to='products/imgs/', default='products/placeholder.png', max_length=500, verbose_name=_("Product Image"))

    regular_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        verbose_name=_("Regular Price"),
        default_currency='SAR',
    )

    sale_price = MoneyField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        blank=True,
        null=True,
        verbose_name=_("Sale Price"),
        default_currency='SAR',
    )

    additional_image_1 = models.ImageField(
        upload_to='products/imgs/product_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_1"), )

    additional_image_2 = models.ImageField(
        upload_to='products/imgs/product_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_2"), )

    additional_image_3 = models.ImageField(
        upload_to='products/imgs/product_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_3"), )

    additional_image_4 = models.ImageField(
        upload_to='products/imgs/product_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_4"), )

    feedback_average = models.PositiveIntegerField(default=0,
                                                  blank=True, null=True, verbose_name=_("Feedback average"))
    feedback_number = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("Feedback number"))

    length = models.FloatField(
        blank=True, null=True, verbose_name=_("length"))
    width = models.FloatField(
        blank=True, null=True, verbose_name=_("Width"))
    height = models.FloatField(
        blank=True, null=True, verbose_name=_("Height"))

    weight = models.DecimalField(default=0,
                                 max_digits=10, decimal_places=3, blank=True, null=True,
                                 verbose_name=_("SET WEIGHT_KG"))

    pieces = models.PositiveIntegerField(
        default=0, blank=True, null=True, verbose_name=_("pieces/set"))

    stock_quantity = models.PositiveIntegerField(
        default=0 , verbose_name=_("Stock quantity"))

    SKU = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("SKU"))

    is_sale = models.BooleanField(
        default=False, verbose_name=_("Sale"))

    New = 'New'
    Hot = 'Hot'

    promotional_select = [
        (New, 'New'),
        (Hot, 'Hot'),

    ]
    promotional = models.CharField(
        max_length=13,
        choices=promotional_select,
        default=New, blank=True, null=True,
    )

    published = 'published'
    draft = 'draft'

    Status_select = [
        (published, 'published'),
        (draft, 'draft'),
    ]

    status = models.CharField(
        max_length=13,
        choices=Status_select,
        default=published, blank=True, null=True,
    )

    product_tags = models.CharField(
        max_length=100, verbose_name=_("Tags"), blank=True, null=True)

    product_slug = models.SlugField(max_length=150,
                                    blank=True, null=True, allow_unicode=True, unique=True, verbose_name=_("Slug"))

    published_date = models.DateField(blank=True, null=True, )
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True, )
    updated = models.DateTimeField(auto_now=True, blank=True, null=True, )


    __original_product_image_name = None
    __original_additional_image_1_name = None
    __original_additional_image_2_name = None
    __original_additional_image_3_name = None
    __original_additional_image_4_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_product_image_name = self.product_image
        self.__original_additional_image_1_name = self.additional_image_1
        self.__original_additional_image_2_name = self.additional_image_2
        self.__original_additional_image_3_name = self.additional_image_3
        self.__original_additional_image_4_name = self.additional_image_4

    class meta:

        ordering = ('-date',)
        verbose_name = _("Product")
        verbose_name_plural = _("Products")

    def get_absolute_url(self):
        return reverse('products:product_detail', kwargs={'slug': self.product_slug})

    def __str__(self):
        return self.product_name

    def product_photo(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.product_image.url))

    product_photo.short_description = "image"
    product_photo.allow_tags = True

    def preview_image_1(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.additional_image_1.url))

    preview_image_1.short_description = "image 1"
    preview_image_1.allow_tags = True

    def preview_image_2(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.additional_image_2.url))

    preview_image_2.short_description = "image 2"
    preview_image_2.allow_tags = True

    def preview_image_3(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.additional_image_3.url))

    preview_image_3.short_description = "image 3"
    preview_image_3.allow_tags = True

    def preview_image_4(self):
        return mark_safe('<img src="{}" width="100" />'.format(self.additional_image_4.url))

    preview_image_4.short_description = "image 4"
    preview_image_4.allow_tags = True

    def save(self, *args, **kwargs):
        # main image
        if self.product_image != self.__original_product_image_name:
            # call the compress function
            new_image = compress(self.product_image)
            # set self.image to new_image
            self.product_image = new_image

        if self.pk is None and self.product_image:
            # call the compress function
            new_image = compress(self.product_image)
            # set self.image to new_image
            self.product_image = new_image

        # additional_image_1
        if self.additional_image_1 != self.__original_additional_image_1_name:
            # call the compress function
            new_image_1 = compress(self.additional_image_1)
            # set self.image to new_image
            self.additional_image_1 = new_image_1

        if self.pk is None and self.additional_image_1:
            # call the compress function
            new_image_1 = compress(self.additional_image_1)
            # set self.image to new_image
            self.additional_image_1 = new_image_1

        # additional_image_2
        if self.additional_image_2 != self.__original_additional_image_2_name:
            # call the compress function
            new_image_2 = compress(self.additional_image_2)
            # set self.image to new_image
            self.additional_image_2 = new_image_2

        if self.pk is None and self.additional_image_2:
            # call the compress function
            new_image_2 = compress(self.additional_image_2)
            # set self.image to new_image
            self.additional_image_2 = new_image_2

        # additional_image_3
        if self.additional_image_3 != self.__original_additional_image_3_name:
            # call the compress function
            new_image_3 = compress(self.additional_image_3)
            # set self.image to new_image
            self.additional_image_3 = new_image_3

        if self.pk is None and self.additional_image_3:
            # call the compress function
            new_image_3 = compress(self.additional_image_3)
            # set self.image to new_image
            self.additional_image_3 = new_image_3

        # additional_image_4
        if self.additional_image_4 != self.__original_additional_image_4_name:
            # call the compress function
            new_image_4 = compress(self.additional_image_4)
            # set self.image to new_image
            self.additional_image_4 = new_image_4

        if self.pk is None and self.additional_image_4:
            # call the compress function
            new_image_4 = compress(self.additional_image_4)
            # set self.image to new_image
            self.additional_image_4 = new_image_4

        super().save(*args, **kwargs)
        self.__original_product_image_name = self.product_image
        self.__original_additional_image_1_name = self.additional_image_1
        self.__original_additional_image_2_name = self.additional_image_2
        self.__original_additional_image_3_name = self.additional_image_3
        self.__original_additional_image_4_name = self.additional_image_4


def pre_save_post_receiver(sender, instance, *args, **kwargs):
    if not instance.product_slug or instance.product_slug is None or instance.product_slug == "":
        instance.product_slug = slugify(instance.product_name, allow_unicode=True)
        qs_exists = Product.objects.filter(product_slug=instance.product_slug).exists()
        if qs_exists:
            instance.product_slug = create_shortcode(instance)


pre_save.connect(pre_save_post_receiver, sender=Product)


class ProductImage(models.Model):
    def upload_file_name(self, filename):
        return f'products/imgs/{self.PRDIProduct.product_slug}/'

    PRDIProduct = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("product"))
    PRDIImage = models.ImageField(
        upload_to='products/imgs/product_imgs/', max_length=500, verbose_name=_("Image"))

    def __str__(self):
        return str(self.PRDIProduct)

    class Meta:
        ordering = ('id',)

    def save(self, *args, **kwargs):
        # call the compress function
        new_image = compress(self.PRDIImage)
        # set self.image to new_image
        self.PRDIImage = new_image
        # save
        super().save(*args, **kwargs)


class ProductRating(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, verbose_name=_("Product"), blank=True, null=True)
    vendor = models.ForeignKey(
        Profile, on_delete=models.CASCADE, verbose_name=_("Vendor"), related_name='vendor', blank=True, null=True,
        limit_choices_to={'status': 'vendor'})
    rate = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], blank=True, null=True, )
    client_name = models.ForeignKey(
        Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='Customer', verbose_name=_("Client"),
        limit_choices_to={'status': 'customer'})
    client_comment = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Comment"))
    active = models.BooleanField(default=True, )
    rating_date = models.DateTimeField(
        auto_now_add=True, blank=True, null=True, )
    rating_update = models.DateTimeField(auto_now=True, blank=True, null=True, )

    def __str__(self):
        return str(self.PRDIProduct)
