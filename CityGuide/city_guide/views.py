from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from city_guide.models import Attraction, Ticket
from django.template import loader
from django.views import generic
from django.views.generic import View
from django.contrib.auth import authenticate, login, logout
from .forms import UserForm

# Our views.

def index(request):
    template = loader.get_template('city_guide/index.html')
    return HttpResponse(template.render())
def logoutUser(request):
    logout(request)
    return redirect('city_guide:index')

class AttractionsView(generic.ListView):
    template_name = 'city_guide/attractions.html'
    context_object_name = 'attractions_obj'

    def get_queryset(self):
        return Attraction.objects.order_by('-name')

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
        