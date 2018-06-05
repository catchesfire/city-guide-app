from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import connection
from collections import namedtuple

import json
# from django.db.models.aggregates import Count

class Category(models.Model):
    name = models.CharField(max_length=25)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=75)
    location_x = models.DecimalField(max_digits=10,decimal_places=7)
    location_y = models.DecimalField(max_digits=10,decimal_places=7)
    time_minutes = models.IntegerField(default=0)
    description = models.TextField()
    age_restriction = models.CharField(max_length=25)
    opening_hours = models.CharField(max_length=100)
    main_photo = models.ImageField(upload_to='uploads/')

    categories = models.ManyToManyField(Category)

    def __str__(self):
        return self.name

class Photo(models.Model):
    photo = models.ImageField(upload_to='uploads/', height_field=1280, width_field=720)
    
    attraction = models.ForeignKey(Attraction, null=True, on_delete=models.SET_NULL)

class TicketType(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class Ticket(models.Model):
    price = models.IntegerField(default=0)

    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    attraction = models.ForeignKey(Attraction, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticket_type.__str__() + " " + str(self.price) + "zl"

class Tour(models.Model):
    name = models.CharField(max_length=50, verbose_name="Nazwa")
    description = models.CharField(max_length=500, verbose_name="Opis")
    attraction_order = models.TextField(default="{}")
    was_order_modified = models.BooleanField(default=False)

    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    def get_user_breaks(self):
        return json.loads(self.user_breaks)

    def min_to_hours(self, time):
        hours = time // 60
        minutes = time - hours * 60
        return str(hours) + " godz. " + str(minutes) + " min"

    def add_currency(self, value):
        return str(value) + " PLN"

class UserBreak(models.Model):
    name = models.CharField(max_length=30)
    time = models.IntegerField(default=1)

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)

class Order(models.Model):
    quantity = models.IntegerField(default=1)
    date = models.DateField(null=True, blank=True)

    tour = models.ForeignKey(Tour, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, null=True, on_delete=models.SET_NULL)

    def cost(self):
        return self.ticket.price * self.quantity
    
    def time(self):
        return self.ticket.attraction.time_minutes

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=100, blank=True, verbose_name="Adres")
    phone_number = models.CharField(max_length=12, blank=True, verbose_name="Nr telefonu")

    class Meta:
        verbose_name_plural = "Categories"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
