from django.contrib import admin
from .models import Attraction, Category, Ticket, TicketType, Order, Tour, Photo, Profile, UserBreak

# Register your models here.

admin.site.register(Category)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Attraction)
admin.site.register(Order)
admin.site.register(Tour)
admin.site.register(Photo)
admin.site.register(Profile)
admin.site.register(UserBreak)