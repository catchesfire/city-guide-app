from django import forms
from django.contrib.auth.models import User
from django.db.models import Max, Min
from city_guide.models import Attraction, Category, Ticket, Order, Profile, Tour, UserBreak
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
    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = "Imię"
        self.fields['last_name'].label = "Nazwisko"
        self.fields['email'].label = "E-mail*"
        self.fields['username'].label = "Login*"
        self.fields['password'].label = "Hasło*"

    password = forms.CharField(widget=forms.PasswordInput(attrs={'class' : 'form-control'}), min_length=6)
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class' : 'form-control'}),required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name' ]
        widgets = {
            'username' : forms.TextInput(attrs={'class' : 'form-control'}),
            'email' : forms.EmailInput(attrs={'class' : 'form-control'}),
            'first_name' : forms.TextInput(attrs={'class' : 'form-control'}),
            'last_name' : forms.TextInput(attrs={'class' : 'form-control'})

        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('address', 'phone_number')
        widgets = {
            'address': forms.TextInput(attrs={'class' : 'form-control'}),
            'phone_number': forms.NumberInput(attrs={'class' : 'form-control'})
        }

class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].label = "Imię"
        self.fields['last_name'].label = "Nazwisko"
        self.fields['email'].label = "E-mail"

    class Meta:
        model = User
        fields = [ 'first_name', 'last_name', 'email' ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class' : 'form-control'}),
            'last_name': forms.TextInput(attrs={'class' : 'form-control'}),
            'email': forms.EmailInput(attrs={'class' : 'form-control'})
        }


class OrderForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=100)
    date = forms.DateField(initial=timezone.now(), required=False)
    ticket_id = forms.IntegerField()

class TourCreateForm(forms.ModelForm):
    
    class Meta:
        model = Tour
        fields = [ 'name', 'description']
        widgets = {
            'name' : forms.TextInput(attrs={'class' : 'form-control'}),
            'description' : forms.Textarea(attrs={'class' : 'form-control'})
        }

class AddBreakForm(forms.ModelForm):
    class Meta:
        model = UserBreak
        fields = [ 'name', 'time' ]
        widgets = {
            'name' : forms.TextInput(attrs={'class': 'form-control'}),
            'time' : forms.NumberInput(attrs={'class': 'form-control'})
        }