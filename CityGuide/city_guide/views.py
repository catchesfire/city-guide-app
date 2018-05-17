from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction, Category, Ticket, TicketType, Cart, Tour
from django.template import loader
from django.views import View, generic
from itertools import chain
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

from .forms import FilterForm, SearchForm, SortForm, UserForm

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
    # opakować sortowanie w forma
    # naprawić widok kiedy jest tylko jedna kategoria
    # jak get nic nie zwróci, to nie wyświetla się navbar
    # dobrze by było, gdyby form zapamietywał aktualne filtry

    def get(self, request, **kwargs):
        filter_form = self.filter_form_class(request.GET)
        search_form = self.search_form_class(request.GET)
        sort_form = self.sort_form_class(request.GET)

        def GetAttractionsByCategory(category_ids_list):
            attr_ids = []
            attr_list = []

            for cat_id in category_ids_list:
                print(cat_id)
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
        
        elif sort_form.is_valid():
            pass # narazie nic

        elif filter_form.is_valid():
            if request.GET.getlist('categories'):
                category_ids = [cat_id for cat_id in request.GET.getlist('categories')]
            else:
                category_ids = [cat_id.id for cat_id in Category.objects.all()] 
            price_min = request.GET.get('price_min', 0)
            price_max = request.GET.get('price_max', 1000)
            time_min = request.GET.get('time_min', 0)
            time_max = request.GET.get('time_max', 1000)

            attractions = Attraction.objects.filter(id__in=GetAttractionsByCategory(category_ids)).filter(id__in=GetAttractionsByPrice(price_min, price_max)).filter(time_minutes__gt=time_min, time_minutes__lt=time_max).order_by('name')
        else:
            attractions = Attraction.objects.all().order_by('-name')
            
        return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": attractions, "categories": Category.objects.all()})        


class AttracionView(generic.DetailView):
    model = Attraction
    template_name = 'city_guide/attraction.html'
    context_object_name = 'attraction_obj'



# class CartView(generic.ListView):
#     model = Cart
#     template_name = 'city_guide/cart.html'
#     context_object_name = 'cart'

#     def get_queryset(self):
#         return Cart.objects.filter(id_user=self.request.user).last()

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


class UserFormView(View):
    form_class = UserForm
    template_name = 'city_guide/registration.html'

    def get(self,request):
        form = self.form_class(None)
        return render(request, self.template_name, {'form': form})

    def post(self,request):
        
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save(commit=False)

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user.set_password(password)
            user.save()

            user = authenticate(username=username, password= password)

            if user is not None:
                login(request, user)
                return redirect('city_guide:index')
        return render(request, self.template_name, {'form': form})
        

class PlannerView(generic.DetailView):
    model = Tour
    template_name = 'city_guide/planner.html'
