# Generated by Django 2.0.2 on 2018-06-03 10:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('city_guide', '0005_tour_route'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='route',
        ),
    ]
