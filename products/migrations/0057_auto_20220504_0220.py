# Generated by Django 3.1.2 on 2022-05-04 00:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20220429_0555'),
        ('products', '0056_auto_20220503_2336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productrating',
            name='client_name',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Customer', to='accounts.profile', verbose_name='Client'),
        ),
        migrations.AlterField(
            model_name='productrating',
            name='vendor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='vendor', to='accounts.profile', verbose_name='Supplier'),
        ),
    ]
