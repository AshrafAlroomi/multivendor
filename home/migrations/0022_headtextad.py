# Generated by Django 3.1.2 on 2022-05-05 22:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_auto_20220429_0555'),
    ]

    operations = [
        migrations.CreateModel(
            name='HeadTextAd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ad_title', models.CharField(blank=True, max_length=100, null=True, verbose_name='Title')),
                ('ad_URL', models.URLField(blank=True, null=True)),
            ],
        ),
    ]
