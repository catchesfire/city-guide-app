from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from city_guide.models import Attraction, Category, Ticket, TicketType, Tour, Profile, Order, User
from django.template import loader
from django.views import View, generic
from itertools import chain
from django.db.models import Q, Case, When
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.hashers  import check_password
from django.contrib.auth.forms import PasswordChangeForm
from .forms import FilterForm, SearchForm, SortForm, UserForm, OrderForm, ProfileForm, UserUpdateForm, TourCreateForm

import json

def index(request):
    tours = []
    all_tours = Tour.objects.filter(user_id = 1)
    if all_tours.count() > 3:
        all_tours = all_tours[:3]
    
    def min_to_hours(time):
        hours = time // 60
        minutes = time - hours * 60
        return str(hours) + " godz. " + str(minutes) + " min"

    for tour in all_tours:
        all_orders = tour.order_set.all()

        grouped_orders = {}

        for order in all_orders:
            grouped_orders[order.ticket.attraction] = all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id = order.ticket.attraction.id))

        total_time = 0
        
        attractions = []

        for attraction in grouped_orders:
            attractions.append(attraction)
            total_time += attraction.time_minutes

        total_cost = 0
        for order in all_orders:
            total_cost += order.cost()

        tours.append({
            'tour': tour,
            'cost': str(total_cost) + " PLN",
            'time': min_to_hours(total_time),
            'attractions': attractions
        })

    return render(request, 'city_guide/index.html', {'tours': tours})

def logout_user(request):
    logout(request)
    return redirect('city_guide:index')

def cart_details(request):
    if request.is_ajax():
        cart = request.session.get('cart', {})

        data = {
            'count' : len(cart)
        }

        return JsonResponse(data)
    return redirect('city_guide:cart')

def cart(request):
    template_name = 'city_guide/cart.html'

    cart = request.session.get('cart', {})

    orders = {}
    total_cost = 0

    for attraction_id, tickets in cart.items():
        attraction = Attraction.objects.get(pk=attraction_id)
        if tickets:
            orders[attraction] = {}
        for ticket_id, quantity in tickets.items():
            if quantity > 0:
                ticket = Ticket.objects.get(pk = ticket_id)
                orders[attraction][ticket] = {}
                orders[attraction][ticket]['id'] = ticket.id
                orders[attraction][ticket]['quantity'] = quantity
                orders[attraction][ticket]['cost'] = ticket.price * quantity
                total_cost += ticket.price * quantity
    print(cart)
    # cart = Cart.objects.filter(user=request.user).last()
    # all_orders = cart.order_set.all()

    # orders = dict(
    #     [
    #         (attraction.ticket.attraction, all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=attraction.ticket.attraction.id))) for attraction in all_orders
    #     ]
    # )

    # total_cost = 0

    # for attraction, orders in cart.items():
    #     for order in orders:
    #         total_cost += order.cost()

    form = TourCreateForm(None)

    return render(request, template_name, {'cart': orders, 'total_cost': total_cost, 'tour_create_form' : form})

def cart_order_edit(request):
    tid = request.GET.get('id', 0)
    quantity = request.GET.get('quantity', 0)
    quantity = int(quantity)
    cart = request.session.get('cart', {})

    for attraction_id, tickets in cart.items():
        for ticket_id in tickets:
            if ticket_id == tid:
                if quantity > 0:
                    cart[str(attraction_id)][str(ticket_id)] = quantity
                    request.session['cart'] = cart
                    request.session.modified = True
                    data = {
                        'status' : 200,
                        'message' : 'An item has been changed.'
                    }
                else:
                    if str(attraction_id) in cart:
                        if str(ticket_id) in cart[str(attraction_id)]:
                            del cart[str(attraction_id)][str(ticket_id)]
                            if not cart[str(attraction_id)]:
                                del cart[str(attraction_id)]
                            request.session['cart'] = cart
                            request.session.modified = True
                    data = {
                        'status' : 400,
                        'message' : "Amount can't be negative."
                    }
                return JsonResponse(data)

    return redirect('city_guide:cart')

@login_required
def planner_add(request):
    if request.method == "POST":
        form = TourCreateForm(request.POST)

        if form.is_valid():
            tour = form.save(commit=False)
            cart = request.session.get('cart', {})

            orders = {}

            i = 0
            for attraction_id in cart:
                orders[str(i)] = attraction_id
                i += 1

            tour.attraction_order = json.dumps(orders)
            tour.user = request.user
            tour.save()

            for attraction_id, tickets in cart.items():
                for ticket_id, quantity in tickets.items():
                    ticket = Ticket.objects.get(pk = ticket_id)
                    order = Order(quantity=quantity, date=timezone.now(), tour=tour, ticket=ticket)
                    order.save()
            
            return redirect('city_guide:cart')
        return redirect('city_guide:cart')
    return redirect('city_guide:cart')

def planner_edit(request, pk):

    try:
        tour = Tour.objects.get(id=pk)
    except:
        raise Http404("Tour doesn't exist.")

    if request.is_ajax():
        order = json.loads(request.GET.get("order", ""))
        tour.attraction_order = json.dumps(order)
        tour.was_order_modified = True
        tour.save()

        data = {
            'status': 200,
            'message': 'OK'
        }
        return JsonResponse(data)

    return redirect('city_guide:index')



def profile(request):
    profile = Profile.objects.get(user=request.user)

#     return render(request, 'city_guide/profile.html', {'profile': profile})

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

def cart_add(request):
    order_form_class = OrderForm

    if request.method == 'POST' and request.is_ajax():
        order_form = order_form_class(request.POST)

        if order_form.is_valid():

            cart = request.session.get('cart', {})

            quantity = request.POST.get('quantity', 1)
            ticket_id = request.POST['ticket_id']
            ticket = Ticket.objects.get(pk = ticket_id)
            attraction = ticket.attraction

            if str(attraction.id) in cart:
                cart[str(attraction.id)][str(ticket.id)] += int(quantity)
            else:
                cart[str(attraction.id)] = {}
                cart[str(attraction.id)][str(ticket.id)] = int(quantity)
            request.session['cart'] = cart
            request.session.modified = True

            data = {
                'status': 'ok'
            }

            # new_order.save()

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


@login_required
@transaction.atomic
def update_profile(request):

    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    password_form = PasswordChangeForm(request.user)
    tours = Tour.objects.filter(user=request.user)

    print(password_form.fields)
    password_form.fields['old_password'].label = "Stare hasło"
    password_form.fields['new_password1'].label = "Nowe hasło"
    password_form.fields['new_password2'].label = "Potrwierdź nowe hasło"

    password_form.fields['old_password'].widget.attrs['class'] = 'form-control'
    
    # for tour in tours:

    #     for order in Cart.objects.filter(user=request.user).last().order_set.all():




    return render(request, 'city_guide/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'tours': tours

        
    })

def profileView(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            print(":::::")
            messages.success(request, ('Your profile was successfully updated!'))
            return redirect('city_guide:profile')
        # else:
            # messages.error(request, _('Please correct the error below.'))

def passwordView(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('city_guide:profile')
        else:
            messages.error(request, 'Please correct the error below.')
            return redirect('city_guide:profile')
            
# to do
# captcha
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


            user = authenticate(username=username, password= password)

            if user is not None:
                login(request, user)
                return redirect('city_guide:index')
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

class PlannerView(generic.DetailView):
    model = Tour
    template_name = 'city_guide/planner.html'
    context_object_name = 'tour'    


    def get_context_data(self, **kwargs):
        context = super(PlannerView, self).get_context_data(**kwargs)
        cart = self.request.session.get('cart', {})

        total_cost = 0

        unsorted_orders = {}

        for attraction_id, tickets in cart.items():
            attraction = Attraction.objects.get(pk=attraction_id)
            if tickets:
                unsorted_orders[attraction] = {}
            for ticket_id, quantity in tickets.items():
                if quantity > 0:
                    ticket = Ticket.objects.get(pk = ticket_id)
                    unsorted_orders[attraction][ticket] = {}
                    unsorted_orders[attraction][ticket]['id'] = ticket.id
                    unsorted_orders[attraction][ticket]['quantity'] = quantity
                    unsorted_orders[attraction][ticket]['cost'] = ticket.price * quantity
                    total_cost += ticket.price * quantity

        orders = {}

        positions = json.loads(self.object.attraction_order)

        for i, position in positions.items():
            for attraction, tickets in unsorted_orders.items():
                if int(attraction.id) == int(position):
                    orders[attraction] = tickets
                    break

        print(orders)

        context['cart'] = orders

        def min_to_hours(time):
            hours = time // 60
            minutes = time - hours * 60

            return str(hours) + " godz. " + str(minutes) + " min"

        tot_time = 0
        for attraction in orders.keys():
            tot_time += attraction.time_minutes

        context['total_time'] = min_to_hours(tot_time)
        context['total_cost'] = total_cost
        context['tour'] = self.object

        return context
        
