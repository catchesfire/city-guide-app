import json
import copy
import urllib
from django.shortcuts import get_object_or_404, render, redirect, reverse
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from city_guide.models import Attraction, Category, Ticket, TicketType, Tour, Profile, Order, User, UserBreak
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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from .forms import FilterForm, SearchForm, SortForm, UserForm, OrderForm, ProfileForm, UserUpdateForm, TourCreateForm, AddBreakForm
from .mixins import ExemplaryPlannerMixin, NotUserMixin
from wkhtmltopdf.views import PDFTemplateResponse
import pdfkit
from django.http import HttpResponse


def index(request):
    tours = []
    all_tours = Tour.objects.filter(user_id = 1)

    
    if( 'form_message' in request.session ):
        message = request.session['form_message']
        messages.success(request, message )
        del request.session['form_message']
    
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
    return render(request, 'city_guide/index.html', {'tours': tours, 'page' : 'home'})

def logout_user(request):
    logout(request)

    request.session['form_message'] = "Wylogowano!"
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
                orders[attraction][ticket]['name'] = ticket.ticket_type
                total_cost += ticket.price * quantity
    form = TourCreateForm(None)

    return render(request, template_name, {'cart': orders, 'total_cost': total_cost, 'tour_create_form' : form})

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

            if str(attraction.id) not in cart:
                cart[str(attraction.id)] = {}

            if str(ticket.id) in cart[str(attraction.id)]:
                cart[str(attraction.id)][str(ticket.id)] += int(quantity)
            else:
                cart[str(attraction.id)][str(ticket.id)] = int(quantity)
            request.session['cart'] = cart
            request.session.modified = True

            data = {
                'status': 'ok'
            }

            return JsonResponse(data)

    data = {
        'status': 'error'
    }  

    return JsonResponse(data)

def cart_create(request, pk):
    cart = request.session.get('cart', {})
    tour = get_object_or_404(Tour, pk=pk)

    all_orders = tour.order_set.all()

    for order in all_orders:
        attraction = order.ticket.attraction
        attraction_id = str(attraction.id)
        ticket = order.ticket
        ticket_id = str(ticket.id)
        if attraction_id not in cart:
            cart[attraction_id] = {}
        cart[attraction_id][ticket_id] = order.quantity
    
    request.session['cart'] = cart
    request.session.modified = True
    
    return redirect('city_guide:cart')

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

def cart_order_delete(request):
    attr_id = request.GET.get('id', 0)
    cart = request.session.get('cart', {})

    for attraction_id, tickets in cart.items():
        if attraction_id == attr_id:
            del cart[str(attraction_id)]
            request.session['cart'] = cart
            request.session.modified = True
            data = {
                        'status' : 200,
                        'message' : "OK."
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
                orders[str(i)] = {}
                orders[str(i)]['attraction'] = attraction_id
                i += 1

            user_breaks = {}

            tour.attraction_order = json.dumps(orders)
            tour.user = request.user
            tour.save()

            for attraction_id, tickets in cart.items():
                for ticket_id, quantity in tickets.items():
                    ticket = Ticket.objects.get(pk = ticket_id)
                    order = Order(quantity=quantity, date=timezone.now(), tour=tour, ticket=ticket)
                    order.save()
            
            return redirect('city_guide:planner', pk=tour.id)
        return redirect('city_guide:cart')
    return redirect('city_guide:cart')

@login_required
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

@login_required
def planner_attraction_delete(request):
    if request.method == "GET":
        tour_id = request.GET.get("tour_id", 0)
        attr_id = request.GET.get("attr_id", 0)     
        tour = Tour.objects.get(pk=tour_id)
        all_orders = tour.order_set.all()

        for order in all_orders:      
            if int(order.ticket.attraction.id) == int(attr_id):
                order_instance = Order.objects.get(id=order.id)
                order_instance.delete()
                break
        all_orders = tour.order_set.all()        

        tour_dict = json.loads(tour.attraction_order)
        for key, orders in tour_dict.items():
            for t, attraction_id in orders.items():
                if t == "attraction" and attraction_id == attr_id:
                    del tour_dict[str(key)]
                    tour.attraction_order = json.dumps(tour_dict)
                    tour.save()
                    data = {
                        'status': 200,
                        'message': 'OK'
                    }
                    return JsonResponse(data)

    return redirect('planner:index')
    
@login_required
def planner_break_delete(request):
    if request.method == "GET":
        tour_id = request.GET.get("tour_id", 0)
        break_id = request.GET.get("break_id", 0)

        tour = Tour.objects.get(pk=tour_id)
        all_breaks = UserBreak.objects.filter(tour=tour)

        for br in all_breaks:      
            if int(br.id) == int(break_id):
                break_instance = UserBreak.objects.get(id=br.id)
                break_instance.delete()
                break

        tour_dict = json.loads(tour.attraction_order)
        for key, orders in tour_dict.items():
            for t, breakID in orders.items():
                if t == "break" and breakID == break_id:
                    del tour_dict[str(key)]
                    tour.attraction_order = json.dumps(tour_dict)
                    tour.save()
                    data = {
                        'status': 200,
                        'message': 'OK'
                    }
                    return JsonResponse(data)

    return redirect('planner:index')

@login_required
def planner_add_break(request, pk):
    try:
        tour = Tour.objects.get(id = pk)
    except:
        raise Http404("Tour doesn't exist.")

    if request.method == "POST" and request.is_ajax():
        user_break_form = AddBreakForm(request.POST)

        if user_break_form.is_valid():
            user_break = user_break_form.save(commit=False)
            user_break.tour = tour
            user_break.save()

            attraction_order = json.loads(tour.attraction_order)

            new_dict = {}
            new_dict['0'] = {}
            new_dict['0']['break'] = user_break.id
            for key, value in attraction_order.items():
                new_dict[str(int(key) + 1)] = attraction_order[key]

            tour.attraction_order = json.dumps(new_dict)
            tour.save()
            data = {
                'status' : 200,
                'message' : 'OK'
            }

            return JsonResponse(data)

        data = {
            'status': 400,
            'message': 'Wrong number'
        }
        return JsonResponse(data)
    return redirect('city_guide:index')

class AttractionsView(generic.ListView):
    filter_form_class = FilterForm
    search_form_class = SearchForm
    sort_form_class = SortForm
    template_name = 'city_guide/attractions.html'
    context_object_name = 'attractions_obj'

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
                        attr_ids = [attr.attraction.id for attr in Ticket.objects.all().order_by(key)]
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

    def get_context_data(self, **kwargs):
        context = super(AttractionsView, self).get_context_data(**kwargs)

        context['page'] = 'attraction'

        return context

@login_required
def tour_delete(request, pk):
    try:
        tour = Tour.objects.get(id=pk)
        if tour.user.id == request.user.id:
            tour.delete()
        else:
            return redirect('city_guide:index')
    except:
        raise Http404("Tour doesn't exsist.")

    request.session['form_message'] = ("Podróż została poprawnie usunięta.", "success")
    return redirect('city_guide:profile')

class AttracionView(generic.DetailView):
    model = Attraction
    template_name = 'city_guide/attraction.html'
    context_object_name = 'attraction_obj'

    def get_context_data(self, **kwargs):
        context = super(AttracionView, self).get_context_data(**kwargs)

        context['page'] = 'attraction'

        return context

class UserLogFormView(NotUserMixin, View):
    template_name = 'city_guide/login.html'
    redirect_url = 'city_guide:index'
    
    def get(self,request):
        return render(request, self.template_name)

    def post(self, request):
        username = request.POST['username']    
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            request.session['form_message'] = "Zalogowano!"
            return redirect('city_guide:index')
        else:
            messages.error(request, ('Nieprawidłowy login lub hasło.'))
            

        return render(request, self.template_name)    

@login_required
@transaction.atomic
def update_profile(request):

    user_form = UserUpdateForm(instance=request.user)
    profile_form = ProfileForm(instance=request.user.profile)
    password_form = PasswordChangeForm(request.user)
    tours = Tour.objects.filter(user=request.user)

    if( 'form_message' in request.session ):
        form_message = request.session['form_message']
        message = form_message[0]
        tag = form_message[1]

        if tag == "danger":
            messages.error(request, message)
        else:
            messages.success(request, message )

        del request.session['form_message']

    password_form.fields['old_password'].label = "Stare hasło"
    password_form.fields['new_password1'].label = "Nowe hasło"
    password_form.fields['new_password2'].label = "Potwierdź hasło"

    password_form.fields['old_password'].widget.attrs['class'] = 'form-control'
    password_form.fields['new_password1'].widget.attrs['class'] = 'form-control'
    password_form.fields['new_password2'].widget.attrs['class'] = 'form-control'
    
    timetab = {}
    costtab = {}

    for t in tours:
        all_orders = t.order_set.all()
        all_breaks = t.userbreak_set.all()
        total_time = 0
        total_cost = 0
        for o in all_orders:
            total_time += o.time()
            total_cost += o.cost()
        for b in all_breaks:
            total_time += b.time

        timetab[t.id] = t.min_to_hours(total_time)
        costtab[t.id] = t.add_currency(total_cost)



    return render(request, 'city_guide/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
        'tours': tours,
        'timetab': timetab,
        'costtab': costtab

        
    })

def profileView(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Twój profil został pomyslnie zmieniony!'))
            return redirect('city_guide:profile')
        else:
            messages.error(request, 'Nie udało się zmienić profilu.')

def passwordView(request):
    if request.method == 'POST':
        password_form = PasswordChangeForm(request.user, request.POST)
        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Twoje hasło zostało pomyslnie zmienione!')
            return redirect('city_guide:profile')
        else:
            messages.error(request, 'Nie udało się zmienić hasła.')
            return redirect('city_guide:profile')

class UserFormView(NotUserMixin, View):
    user_form_class = UserForm
    profile_form_class = ProfileForm
    template_name = 'city_guide/registration.html'
    redirect_url = 'city_guide:index'
    success_message = "Zarejestrowano!"  

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
            # ''' Begin reCAPTCHA validation '''
            recaptcha_response = request.POST.get('g-recaptcha-response')
            url = 'https://www.google.com/recaptcha/api/siteverify'
            values = {
                'secret': settings.GOOGLE_RECAPTCHA_SECRET_KEY,
                'response': recaptcha_response
            }
            data = urllib.parse.urlencode(values).encode()
            req =  urllib.request.Request(url, data=data)
            response = urllib.request.urlopen(req)
            result = json.loads(response.read().decode())


            # ''' End reCAPTCHA validation '
            if result['success']:
                user.set_password(password)
                user.save()
                user.profile.address = address
                user.profile.phone_number = phone
                user.profile.save()


                user = authenticate(username=username, password= password)

                if user is not None:
                    login(request, user)
                    request.session['form_message'] = "Zarejestrowano!"
                    return redirect('city_guide:index')
            else:
                messages.error(request, 'Nieprawidłwa reCAPTCHA. Spróbuj ponownie.')
            
        return render(request, self.template_name, {'user_form': user_form, 'profile_form': profile_form})

class PlannerView(ExemplaryPlannerMixin, generic.DetailView):
    login_url = '/login/'
    model = Tour
    context_object_name = 'tour'    
    
    waypoints = {}

    def render_to_response(self, context, **response_kwargs):
        """ Allow AJAX requests to be handled more gracefully """
        if self.request.is_ajax():
            return JsonResponse(self.waypoints, safe=False, **response_kwargs)
        else:
            return super(generic.DetailView,self).render_to_response(context, **response_kwargs)

    def get_context_data(self, **kwargs):
        context = super(PlannerView, self).get_context_data(**kwargs)
        self.waypoints = {}

        all_orders = self.object.order_set.all()
        all_breaks = self.object.userbreak_set.all()

        unsorted_orders = {}
        total_cost = 0

        for order in all_orders:
            unsorted_orders[order.ticket.attraction] = all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=order.ticket.attraction.id))
            total_cost += order.cost()

        unsorted_breaks = {}
        waypoints = self.waypoints

        orders = {}
        positions = json.loads(self.object.attraction_order)

        j = 0
        for i, types in positions.items():
            for type_name, attraction_id in types.items():
                if type_name == "attraction":
                    for attraction, ticket in unsorted_orders.items():
                        if int(attraction.id) == int(attraction_id):
                            orders[attraction] = {}
                            orders[attraction]['type'] = "attraction"
                            orders[attraction]['items'] = ticket
                            waypoints[str(j)] = {}
                            waypoints[str(j)]['lat'] = float(attraction.location_x)
                            waypoints[str(j)]['lng'] = float(attraction.location_y)
                            j += 1
                            break
                else:
                    user_break = self.object.userbreak_set.get(pk=attraction_id)
                    orders[user_break] = {}
                    orders[user_break]['type'] = 'break'
                    orders[user_break]['items'] = user_break
                    
        context['cart'] = orders
        context['waypoints'] = json.dumps(waypoints)

        def min_to_hours(time):
            hours = time // 60
            minutes = time - hours * 60

            return str(hours) + " godz. " + str(minutes) + " min"

        tot_time = 0
        for key, items in orders.items():
            if items['type'] == 'attraction':
                tot_time += key.time_minutes
            else:
                tot_time += key.time        

        context['total_time'] = min_to_hours(tot_time)
        context['total_cost'] = str(total_cost) + " PLN"
        context['tour'] = self.object
        context['break_form'] = AddBreakForm(None)
        
        return context

def raw_planner(request, pk):
    tour = Tour.objects.get(id=pk)
    all_orders = tour.order_set.all()

    return render(request, 'city_guide/pdf.html', {'orders': all_orders})

def planner_to_pdf(request, pk):
    tour = Tour.objects.get(id=pk)

    all_orders = tour.order_set.all()
    all_breaks = tour.userbreak_set.all()

    unsorted_orders = {}
    total_cost = 0

    for order in all_orders:
        unsorted_orders[order.ticket.attraction] = all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=order.ticket.attraction.id))
        total_cost += order.cost()

    orders = {}
    waypoints = {}
    positions = json.loads(tour.attraction_order)

    j = 0
    for i, types in positions.items():
        for type_name, attraction_id in types.items():
            if type_name == "attraction":
                for attraction, ticket in unsorted_orders.items():
                    if int(attraction.id) == int(attraction_id):
                        orders[attraction] = {}
                        orders[attraction]['type'] = "attraction"
                        orders[attraction]['items'] = ticket
                        waypoints[str(j)] = {}
                        waypoints[str(j)]['lat'] = float(attraction.location_x)
                        waypoints[str(j)]['lng'] = float(attraction.location_y)
                        j += 1
                        break
            else:
                user_break = tour.userbreak_set.get(pk=attraction_id)
                orders[user_break] = {}
                orders[user_break]['type'] = 'break'
                orders[user_break]['items'] = user_break
    
    def min_to_hours(time):
        hours = time // 60
        minutes = time - hours * 60

        return str(hours) + " godz. " + str(minutes) + " min"

    tot_time = 0
    for key, items in orders.items():
        if items['type'] == 'attraction':
            tot_time += key.time_minutes
        else:
            tot_time += key.time        

    tot_time = min_to_hours(tot_time)

    return render(request, 'city_guide/pdf.html', {'tour' : tour, 'total_cost': total_cost, 'total_time': tot_time, 'orders': orders, 'waypoints' : json.dumps(waypoints)})

class PDFView(View):
    template = 'city_guide/pdf.html'

    def get(self, request, pk):
        tour = Tour.objects.get(id=pk)
        all_orders = tour.order_set.all()
        all_breaks = tour.userbreak_set.all()

        unsorted_orders = {}
        total_cost = 0

        for order in all_orders:
            unsorted_orders[order.ticket.attraction] = all_orders.filter(ticket_id__in=Ticket.objects.filter(attraction_id=order.ticket.attraction.id))
            total_cost += order.cost()

        orders = {}
        waypoints = {}
        positions = json.loads(tour.attraction_order)

        j = 0
        for i, types in positions.items():
            for type_name, attraction_id in types.items():
                if type_name == "attraction":
                    for attraction, ticket in unsorted_orders.items():
                        if int(attraction.id) == int(attraction_id):
                            orders[attraction] = {}
                            orders[attraction]['type'] = "attraction"
                            orders[attraction]['items'] = ticket
                            waypoints[str(j)] = {}
                            waypoints[str(j)]['lat'] = float(attraction.location_x)
                            waypoints[str(j)]['lng'] = float(attraction.location_y)
                            j += 1
                            break
                else:
                    user_break = tour.userbreak_set.get(pk=attraction_id)
                    orders[user_break] = {}
                    orders[user_break]['type'] = 'break'
                    orders[user_break]['items'] = user_break
        
        def min_to_hours(time):
            hours = time // 60
            minutes = time - hours * 60

            return str(hours) + " godz. " + str(minutes) + " min"

        tot_time = 0
        for key, items in orders.items():
            if items['type'] == 'attraction':
                tot_time += key.time_minutes
            else:
                tot_time += key.time        

        tot_time = min_to_hours(tot_time)

        data = {
            'tour' : tour, 
            'total_cost': total_cost, 
            'total_time': tot_time, 
            'orders': orders, 
            'waypoints' : json.dumps(waypoints)
        }

        response = PDFTemplateResponse(request = request,
                                        template = self.template,
                                        filename = "test.pdf",
                                        context = data,
                                        show_content_in_browser=False,
                                        cmd_options= {
                                            'margin-top0': 10,
                                            'zoom': 1,
                                            'viewport-size': '1366x513',
                                            'javascript-delay': 1000,
                                            'footer-center': '[page]/[topage]',
                                            'no-stop-slow-scripts': True
                                            },
                                        )
        return response

def description(request):
    return render(request, 'city_guide/description.html', {'page': 'about'})
