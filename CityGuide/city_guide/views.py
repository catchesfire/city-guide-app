from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction, Category, Ticket, TicketType, Attraction_Category
from django.template import loader
from django.views import View, generic
from itertools import chain

from .forms import FilterForm

def index(request):
    template = loader.get_template('city_guide/index.html')
    return HttpResponse(template.render())

class AttractionsView(generic.ListView):
    form_class = FilterForm
    template_name = 'city_guide/attractions.html'
    context_object_name = 'attractions_obj'
    form = None

    def get(self, request, **kwargs):
        form = self.form_class(request.GET)
        attractions = None
        time_min = 0
        time_max = 1000
        attr_ids = []
        attr_list = []

        attr_ids_1 = []

        if form.is_valid():
            category_ids = [cat_id for cat_id in request.GET.getlist('categories', Category.objects.all())] 
            price_min = request.GET.get('price_min', 0)
            price_max = request.GET.get('price_max', 1000)
            time_min = request.GET.get('time_min', 0)
            time_max = request.GET.get('time_max', 1000)

            for cat_id in category_ids:
                for obj in Attraction_Category.objects.filter(id_category=cat_id):
                    attr_list.append(obj)

                for obj in attr_list:
                    attr_ids.append(obj.id_attraction.id)
            
            for ticket in Ticket.objects.filter(price__gt=price_min).filter(price__lt=price_max):
                attr_ids_1.append(ticket.id_attraction.id)

            attractions = Attraction.objects.filter(id__in=attr_ids).filter(id__in=attr_ids_1).filter(time_minutes__gt=time_min).filter(time_minutes__lt=time_max).order_by('-name')
        else:
            attractions = Attraction.objects.all().order_by('-name')
            
        return render(request, self.template_name, {"form": form, "attractions_obj": attractions, "categories": Category.objects.all()})        


class AttracionView(generic.DetailView):
    model = Attraction
    template_name = 'city_guide/attraction.html'