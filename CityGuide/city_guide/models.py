from django.db import models

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=25)

    def __str__(self):
        return self.name

class TicketType(models.Model):
    type_name = models.CharField(max_length=25)
    discount = models.IntegerField(default=0)

    def __str__(self):
        return self.type_name + " " + str(self.discount) + "%"

class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, on_delete=models.CASCADE)
    price = models.IntegerField(default=0)

    def __str__(self):
        return self.ticket_type.__str__() + " " + str(self.price) + "zl"

class Attraction(models.Model):
    name = models.CharField(max_length=75)
    location = models.CharField(max_length=1000)
    time_minutes = models.IntegerField(default=0)
    description = models.CharField(max_length=500)
    age_restriction = models.CharField(max_length=25)
    opening_hours = models.CharField(max_length=100)

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


    
