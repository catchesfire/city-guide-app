from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class Attraction(models.Model):
    name = models.CharField(max_length=75)
    location = models.CharField(max_length=1000)
    time_minutes = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    age_restriction = models.CharField(max_length=25)
    opening_hours = models.CharField(max_length=100)

class Attraction_Category(models.Model):
    id_attracion = models.ForeignKey(Attraction, on_delete=models.CASCADE)
    id_category = models.ForeignKey(Category, on_delete=models.CASCADE)    

class TicketType(models.Model):
    type_name = models.CharField(max_length=25)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return self.type_name + " " + str(self.discount) + "%"    

class Ticket(models.Model):
    price = models.IntegerField(default=0)
    
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    id_attracion = models.ForeignKey(Attraction, on_delete=models.CASCADE)

    def __str__(self):
        return self.ticket_type.__str__() + " " + str(self.price) + "zl"

class Cart(models.Model):
    id_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

class Order(models.Model):
    quantity = models.IntegerField(default=1)
    date = models.DateField()

    id_cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    id_ticket = models.ForeignKey(Ticket, null=True, on_delete=models.SET_NULL)

class Tour(models.Model):
    discount = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    route = models.CharField(max_length=1000)
    date_from = models.DateField()
    date_to = models.DateField()

    id_user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

class Profile(models.Model):
    name = models.CharField(max_length=20)
    lastname = models.CharField(max_length=40)
    address = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=12)
    mail = models.EmailField()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()