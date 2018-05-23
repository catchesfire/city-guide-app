from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from city_guide.models import Attraction, Category, Ticket, TicketType, Cart, Tour, Profile, Order
from django.template import loader
from django.views import View, generic
from itertools import chain
from django.db.models import Q, Case, When
from django.contrib.auth import authenticate, login, logout
from django.utils import timezone

from .forms import FilterForm, SearchForm, SortForm, UserForm, OrderForm

def index(request):
    return render(request, 'city_guide/index.html', {})

def logoutUser(request):
    logout(request)
    return redirect('city_guide:index')

def cartDetails(request):
    if request.is_ajax():
        cart = Cart.objects.filter(user=request.user).last()
        orders = cart.order_set.all()

        data = {
            'count' : orders.count()
        }

        return JsonResponse(data)
    return redirect('city_guide:cart')

def cartView(request):
    template_name = 'city_guide/cart.html'
    cart = Cart.objects.filter(user=request.user).last()
    all_orders = cart.order_set.all()

    orders = dict(
        [
            (attraction.ticket.attraction, all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=attraction.ticket.attraction.id))) for attraction in all_orders
        ]
    )

    total_cost = 0

    for order in all_orders:
        total_cost += order.cost()
        

    return render(request, template_name, {'cart': orders, 'total_cost': total_cost})

def cart_order_edit(request):
    order_id = request.GET.get('id', 0)
    try:
        order = Order.objects.get(pk=order_id)
    except:
        raise Http404("Order doesn't exist.")
    
    if request.is_ajax():
        quantity = request.GET.get('quantity', 0)
        
        order.quantity = int(quantity)
        if order.quantity >= 0:
            order.save()
            data = {
                'status' : 200,
                'message' : 'Item has been changed.'
            }
        else:
            data = {
                'status': 400,
                'message': "Amount can't be negative."
            }
        return JsonResponse(data)
    return redirect('city_guide:cart')

def profileView(request):
    profile = Profile.objects.get(user=request.user)

    return render(request, 'city_guide/profile.html', {'profile': profile})

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
            
            for ticket in Ticket.objects.filter(price__gte=price_min, price__lte=price_max):           
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

            attractions = Attraction.objects.filter(id__in=GetAttractionsByCategory(category_ids)).filter(id__in=GetAttractionsByPrice(price_min, price_max)).filter(time_minutes__gte=time_min, time_minutes__lte=time_max).order_by('name')
            return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": attractions, "categories": Category.objects.all()})             

        return render(request, self.template_name, {"filter_form": filter_form, "attractions_obj": Attraction.objects.all().order_by('name'), "categories": Category.objects.all()})

def AddToCart(request):
    order_form_class = OrderForm

    if request.method == 'POST' and request.is_ajax():
        order_form = order_form_class(request.POST)

        if order_form.is_valid():
            quantity = request.POST.get('quantity', 1)
            date = request.POST.get('date', timezone.now())
            ticket_id = request.POST.get('ticket_id', 1)
            cart = Cart.objects.filter(user=request.user).last()
            ticket = Ticket.objects.get(pk=ticket_id)

            new_order, created = cart.order_set.get_or_create(ticket_id=ticket_id)            

            if created:
                new_order.date = date
                new_order.quantity = quantity
                new_order.cart = cart
                new_order.ticket = ticket
            else:
                new_order.quantity += int(quantity)
            
            data = {
                'status': 'ok'
            }

            new_order.save()

            return JsonResponse(data)

    data = {
        'status': 'error'
    }  

    return JsonResponse(data)


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
    context_object_name = 'tour'    


    def get_context_data(self, **kwargs):
        print(self.request)
        context = super(PlannerView, self).get_context_data(**kwargs)
        context['tour'] = self.object
        all_orders = Cart.objects.filter(user=self.request.user).last().order_set.all()

        orders = dict(
            [
                (attraction.ticket.attraction, all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=attraction.ticket.attraction.id))) for attraction in Cart.objects.filter(user=self.request.user).last().order_set.all()
            ]
        )
        context['cart'] = orders

        def min_to_hours(time):
            hours = time // 60
            minutes = time - hours * 60

            return str(hours) + " godz. " + str(minutes) + " min"

        tot_time = 0
        for attraction in orders.keys():
            tot_time += attraction.time_minutes

        tot_cost = 0
        for order in all_orders:
            tot_cost += order.cost()

        context['total_time'] = min_to_hours(tot_time)
        context['total_cost'] = tot_cost

        return context