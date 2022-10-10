from django.db import models
from products.models import Product
from django.utils.translation import ugettext_lazy as _
from PIL import Image
from io import BytesIO
from django.core.files import File
from django.contrib.auth.models import User


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


class SpecialDeal(models.Model):
    ordinal = models.IntegerField(
        blank=True, null=True, verbose_name=_("ordinal"))
    owner = models.ForeignKey(
        'auth.User', blank=True, null=True, related_name='special_deals', on_delete=models.CASCADE)  # new

    name = models.CharField(max_length=150, verbose_name=_("Name"))
    # DESCRIPTION
    description = models.TextField(verbose_name=_("Short Description"))
    price = models.FloatField(
        blank=True, null=True, verbose_name=_("price"))

    special_deal_image = models.ImageField(
        upload_to='specialDeals/imgs/', default='specialDeals/specialDeal.jpg', max_length=500,
        verbose_name=_("specialDeal Image"))

    additional_image_1 = models.ImageField(
        upload_to='specialDeals/imgs/specialDeal_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_1"), )

    additional_image_2 = models.ImageField(
        upload_to='specialDeals/imgs/specialDeal_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_2"), )

    additional_image_3 = models.ImageField(
        upload_to='specialDeals/imgs/specialDeal_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_3"), )

    additional_image_4 = models.ImageField(
        upload_to='specialDeals/imgs/specialDeal_imgs/', blank=True, null=True, max_length=500,
        verbose_name=_("Additional  Image_4"), )
    price = models.FloatField(
        blank=True, null=True, verbose_name=_("Price"))

    valid_form = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField()
    date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date_update = models.DateTimeField(auto_now=True, blank=True, null=True)
    __original_special_deal_image_name = None
    __original_additional_image_1_name = None
    __original_additional_image_2_name = None
    __original_additional_image_3_name = None
    __original_additional_image_4_name = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_special_deal_image_name = self.special_deal_image
        self.__original_additional_image_1_name = self.additional_image_1
        self.__original_additional_image_2_name = self.additional_image_2
        self.__original_additional_image_3_name = self.additional_image_3
        self.__original_additional_image_4_name = self.additional_image_4
        # self.user=args['user']

    class meta:

        ordering = ('ordinal',)
        verbose_name = _("SpecialDeal")
        verbose_name_plural = _("SpecialDeal")

    def save(self, *args, **kwargs):
        # main image
        if self.special_deal_image != self.__original_special_deal_image_name:
            # call the compress function
            new_image = compress(self.special_deal_image)
            # set self.image to new_image
            self.special_deal_image = new_image

        if self.pk is None and self.special_deal_image:
            # call the compress function
            new_image = compress(self.special_deal_image)
            # set self.image to new_image
            self.special_deal_image = new_image

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
        self.__original_special_deal_image_name = self.special_deal_image
        self.__original_additional_image_1_name = self.additional_image_1
        self.__original_additional_image_2_name = self.additional_image_2
        self.__original_additional_image_3_name = self.additional_image_3
        self.__original_additional_image_4_name = self.additional_image_4
    def __str__(self):
        return self.name


class SpecialDealItem(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    specialDeal = models.ForeignKey(SpecialDeal, related_name='items', on_delete=models.CASCADE,verbose_name = "specialDeal")
    quantity = models.IntegerField()
    owner = models.ForeignKey(
        'auth.User', related_name='SpecialDealItem', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['created']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
