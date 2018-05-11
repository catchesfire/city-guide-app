from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction, Category, Ticket, TicketType, Attraction_Category, Cart
from django.template import loader
from django.views import View, generic
from itertools import chain
from django.db.models import Q

from .forms import FilterForm, SearchForm, SortForm

def index(request):
    return render(request, 'city_guide/index.html', {})

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
                for obj in Attraction_Category.objects.filter(id_category=cat_id):
                    attr_list.append(obj)

                for obj in attr_list:
                    attr_ids.append(obj.id_attraction.id)
            
            return attr_ids
        
        def GetAttractionsByPrice(price_min, price_max):
            attr_ids = []
            
            for ticket in Ticket.objects.filter(price__gt=price_min, price__lt=price_max):           
                attr_ids.append(ticket.id_attraction.id)
            
            return attr_ids

        if search_form.is_valid():
            search_fraze = request.GET.get('search_fraze', "")
            attractions = Attraction.objects.filter(Q(name__icontains=search_fraze) | Q(description__icontains=search_fraze))
        
        elif sort_form.is_valid():
            pass # narazie nic

        elif filter_form.is_valid():
            category_ids = [cat_id for cat_id in request.GET.getlist('categories', Category.objects.all())] 
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

class CartView(generic.ListView):
    model = Cart
    template_name = 'city_guide/cart.html'
    context_object_name = 'cart'

    def get_queryset(self):
        return Cart.objects.filter(id_user=self.request.user).last()
