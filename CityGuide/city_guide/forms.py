from django import forms
from django.contrib.auth.models import User
from django.db.models import Max, Min
from city_guide.models import Attraction, Category, Ticket, Order
from django.utils import timezone

class FilterForm(forms.Form):
    categories = forms.ModelMultipleChoiceField(queryset=Category.objects.all(), widget=forms.CheckboxSelectMultiple, required=False)    
    price_min = forms.IntegerField(required=False)
    price_max = forms.IntegerField(required=False)
    time_min = forms.IntegerField(required=False)
    time_max = forms.IntegerField(required=False)


class SearchForm(forms.Form):
    search_fraze = forms.CharField(max_length=50, required=True)

class SortForm(forms.Form):
    sort_key = forms.CharField(max_length=50, required=False)

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class OrderForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100)
    date = forms.DateField(initial=timezone.now(), required=False)
    ticket_id = forms.IntegerField()

