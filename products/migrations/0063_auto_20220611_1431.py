# Generated by Django 3.1.2 on 2022-06-11 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0062_auto_20220505_0512'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='product_image',
            field=models.ImageField(default='products/product.jpg', max_length=500, upload_to='products/imgs/', verbose_name='Product Image'),
        ),
    ]
