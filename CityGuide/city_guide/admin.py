from django.contrib import admin
from .models import Attraction, Category, Ticket, TicketType

# Register your models here.

admin.site.register(Category)
admin.site.register(TicketType)
admin.site.register(Ticket)
admin.site.register(Attraction)