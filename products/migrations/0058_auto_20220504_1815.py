# Generated by Django 3.1.2 on 2022-05-04 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0057_auto_20220504_0220'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='feedbak_average',
            field=models.FloatField(blank=True, default=0, null=True, verbose_name='Feedbak average'),
        ),
        migrations.AddField(
            model_name='product',
            name='feedbak_number',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Feedbak number'),
        ),
    ]