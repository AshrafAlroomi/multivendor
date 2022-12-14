# Generated by Django 3.1.2 on 2022-05-06 23:50

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_name', models.CharField(max_length=150, verbose_name='Page Name')),
                ('content', ckeditor.fields.RichTextField(blank=True, null=True, verbose_name='Content')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
