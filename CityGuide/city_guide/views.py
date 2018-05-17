from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction, Category, Ticket, TicketType, Cart, Tour, Profile
from django.template import loader
from django.views import View, generic
from itertools import chain
from django.db.models import Q, Case, When
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import transaction

from .forms import FilterForm, SearchForm, SortForm, UserForm, OrderForm, ProfileForm

def index(request):
    return render(request, 'city_guide/index.html', {})


def logoutUser(request):
    logout(request)
    return redirect('city_guide:index')

def cartView(request):
    template_name = 'city_guide/cart.html'
    cart = Cart.objects.filter(user=request.user).last()
    all_orders = cart.order_set.all()

    orders = dict(
        [
            (attraction.ticket.attraction, all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=attraction.ticket.attraction.id))) for attraction in all_orders
        ]
    )

    return render(request, template_name, {'cart': orders})


class AttractionsView(generic.ListView):
    filter_form_class = FilterForm
    search_form_class = SearchForm
    sort_form_class = SortForm
    template_name = 'city_guide/attractions.html'
    context_object_name = 'attractions_obj'

    # @todo
    # naprawić widok kiedy jest tylko jedna kategoria
    # dobrze by było, gdyby form zapamietywał aktualne filtry
    # to później

    def get(self, request, **kwargs):
        filter_form = self.filter_form_class(request.GET)
        search_form = self.search_form_class(request.GET)
        sort_form = self.sort_form_class(request.GET)

        def GetAttractionsByCategory(category_ids_list):
            attr_ids = []
            attr_list = []

            for cat_id in category_ids_list:
                for obj in Category.objects.get(pk=cat_id).attraction_set.all():
                    attr_list.append(obj)

                for obj in attr_list:
                    attr_ids.append(obj.id)
            
            return attr_ids
        
        def GetAttractionsByPrice(price_min, price_max):
            attr_ids = []
            
            for ticket in Ticket.objects.filter(price__gt=price_min, price__lt=price_max):           
                attr_ids.append(ticket.attraction.id)
            
            return attr_ids

        if search_form.is_valid():
            search_fraze = request.GET.get('search_fraze', "")
            attractions = Attraction.objects.filter(Q(name__icontains=search_fraze) | Q(description__icontains=search_fraze))
            return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": attractions, "categories": Category.objects.all()}) 
        
        sort_keys = [ key for key in request.GET.getlist('sort_key', [])]
        if len(sort_keys) != 0:
            found = False
                         
            for key in sort_keys:
                if key:
                    if key == "price" or key == "-price":
                        attr_ids = [attr.id_attraction.id for attr in Ticket.objects.all().order_by(key)]
                        tickets_order = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(attr_ids)])
                        attractions = Attraction.objects.filter(id__in=attr_ids).order_by(tickets_order)
                    else:
                        attractions = Attraction.objects.all().order_by(key)

                    found = True
                    break

            if not found:
                attractions = Attraction.objects.all().order_by('name')
            
            return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": attractions, "categories": Category.objects.all()}) 
            
        if filter_form.is_valid():
            if request.GET.getlist('categories'):
                category_ids = [cat_id for cat_id in request.GET.getlist('categories')] 
            else:
                category_ids = [cat_id.id for cat_id in Category.objects.all()]
            
            price_min = request.GET.get('price_min', 0)
            price_max = request.GET.get('price_max', 1000)
            time_min = request.GET.get('time_min', 0)
            time_max = request.GET.get('time_max', 1000)

            attractions = Attraction.objects.filter(id__in=GetAttractionsByCategory(category_ids)).filter(id__in=GetAttractionsByPrice(price_min, price_max)).filter(time_minutes__gt=time_min, time_minutes__lt=time_max).order_by('name')
            return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": attractions, "categories": Category.objects.all()})             

        return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": Attraction.objects.all().order_by('name'), "categories": Category.objects.all()})        

class AttracionView(generic.DetailView):
    model = Attraction
    template_name = 'city_guide/attraction.html'
    context_object_name = 'attraction_obj'

class UserLogFormView(View):
    template_name = 'city_guide/login.html'
    
    def get(self,request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']    
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('city_guide:index')
        else:
            error = 'Invalid username or password.'

        return render(request, self.template_name, {'error_message' : error})    


@login_required
@transaction.atomic
def update_profile(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, _('Your profile was successfully updated!'))
            return redirect('settings:profile')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        user_form = UserForm(instance=request.user)
        user_form.address =  'cosssss'
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'city_guide/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

class UserFormView(View):
    user_form_class = UserForm
    profile_form_class = ProfileForm
    template_name = 'city_guide/registration.html'

    def get(self,request):
        user_form = self.user_form_class(None)
        profile_form = self.profile_form_class(None)
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

    def post(self,request):
        
        user_form = self.user_form_class(request.POST)
        profile_form = self.profile_form_class(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            profile = profile_form.save(commit=False)

            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            name = user_form.cleaned_data['first_name']
            lastName = user_form.cleaned_data['last_name']
            address = profile_form.cleaned_data['address']
            phone = profile_form.cleaned_data['phone_number']
            user.set_password(password)
            user.save()
            user.profile.address = address
            user.profile.phone_number = phone
            user.profile.save()

            cart = Cart.objects.create(user=user)
            cart.save()

            user = authenticate(username=username, password= password)

            if user is not None:
                login(request, user)
                return redirect('city_guide:index')
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

class PlannerView(generic.DetailView):
    model = Tour
    template_name = 'city_guide/planner.html'

class AddToCart(View):
    form_class = OrderForm
