from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from city_guide.models import Attraction
from django.template import loader

# Our views.

def index(request):
    return HttpResponse("Hello World!")

def attracions(request):
    attracions_obj = Attraction.objects.order_by('-name')
    template = loader.get_template('city_guide/attractions.html')

    context = {
        'attracions_obj': attracions_obj,
    }

    return render(request, 'city_guide/attractions.html', context)

def attracion(request, atrr_id):
    atrr = get_object_or_404(Attraction, pk=atrr_id)
    return render(request, 'city_guide/attraction.html', {'attracion': atrr})