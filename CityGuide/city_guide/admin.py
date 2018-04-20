from django.contrib import admin
from .models import Attraction, Category, Ticket, TicketType, Attraction_Category, Cart, Order, Tour, Photo, Profile

# Register your models here.

admin.site.register(Category)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Attraction)
admin.site.register(Attraction_Category)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(Tour)
admin.site.register(Photo)
admin.site.register(Profile)
