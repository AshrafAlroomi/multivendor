# Generated by Django 3.1.2 on 2022-05-06 23:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contact', '0005_auto_20220506_0447'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='messageslist',
            options={'ordering': ('-id',), 'verbose_name': 'Message List', 'verbose_name_plural': 'Messages List'},
        ),
    ]