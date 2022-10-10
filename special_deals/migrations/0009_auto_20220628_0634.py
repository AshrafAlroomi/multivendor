# Generated by Django 3.1.2 on 2022-06-28 06:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0063_auto_20220611_1431'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('special_deals', '0008_auto_20220627_1502'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpecialDealItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.IntegerField()),
                ('owner', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='SpecialDealItem', to=settings.AUTH_USER_MODEL)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.product')),
                ('specialDeal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='special_deals.specialdeal')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.DeleteModel(
            name='SpecialDealDetail',
        ),
    ]
