from django.urls import path
from django.contrib.auth.views import logout
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views

app_name = 'city_guide'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.UserFormView.as_view(), name='register'),
    path('login/', views.UserLogFormView.as_view(), name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction'),
    path('cart', views.CartView.as_view(), name="cart"),
    path('attractions/filter', views.AttractionsView.as_view(), name="filter"),
    path('planner/<int:pk>', views.PlannerView.as_view(), name='planner')
]