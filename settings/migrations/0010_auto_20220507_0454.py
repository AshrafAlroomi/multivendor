# Generated by Django 3.1.2 on 2022-05-07 02:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('settings', '0009_sitesetting_site_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sitesetting',
            name='description',
            field=models.CharField(max_length=50, verbose_name='Site Description'),
        ),
    ]
