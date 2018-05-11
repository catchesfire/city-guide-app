from django import forms
from django.db.models import Max, Min
from city_guide.models import Attraction, Category, Ticket

class FilterForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)    
    price_min = forms.IntegerField(required=False)
    price_max = forms.IntegerField(required=False)
    time_min = forms.IntegerField(required=False)
    time_max = forms.IntegerField(required=False)
    
    # price_min = forms.IntegerField(min_value=Ticket.objects.all().aggregate(Min('price')), max_value=Ticket.objects.all().aggregate(Max('price')))
    # price_max = forms.IntegerField(min_value=Ticket.objects.all().aggregate(Min('price')), max_value=Ticket.objects.all().aggregate(Max('price')))
    # time_min = forms.IntegerField(min_value=Attraction.objects.all().aggregate(Min('time_minutes')), max_value=Attraction.objects.all().aggregate(Max('time_minutes')))
    # time_max = forms.IntegerField(min_value=Attraction.objects.all().aggregate(Min('time_minutes')), max_value=Attraction.objects.all().aggregate(Max('time_minutes')))

class SearchForm(forms.Form):
    search_fraze = forms.CharField(max_length=50)

class SortForm(forms.Form):
    sort_key = forms.CharField()

