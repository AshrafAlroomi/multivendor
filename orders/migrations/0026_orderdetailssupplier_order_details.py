# Generated by Django 3.2.12 on 2022-03-23 18:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0025_auto_20220323_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetailssupplier',
            name='order_details',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.orderdetails'),
        ),
    ]
