# Generated by Django 2.0.2 on 2018-05-30 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('city_guide', '0005_auto_20180524_1045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tour',
            name='date_from',
        ),
        migrations.RemoveField(
            model_name='tour',
            name='date_to',
        ),
        migrations.AlterField(
            model_name='tour',
            name='description',
            field=models.CharField(max_length=500, verbose_name='Opis'),
        ),
        migrations.AlterField(
            model_name='tour',
            name='name',
            field=models.CharField(max_length=50, verbose_name='Nazwa'),
        ),
    ]