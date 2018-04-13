from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction
from django.template import loader
from django.views import generic

# Our views.

def index(request):
    template = loader.get_template('city_guide/index.html')
    return HttpResponse(template.render())

class AttractionsView(generic.ListView):
    template_name = 'city_guide/attractions.html'
    context_object_name = 'attracions_obj'

    def get_queryset(self):
        return Attraction.objects.order_by('-name')


class AttracionView(generic.DetailView):
    model = Attraction
    template_name = 'city_guide/attraction.html'