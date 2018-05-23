from django.urls import path
from django.contrib.auth.views import logout
from django.conf import settings
from . import views
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import csrf_exempt


app_name = 'city_guide'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.UserFormView.as_view(), name='register'),
    path('login/', views.UserLogFormView.as_view(), name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction'),
    path('cart', views.cartView, name="cart"),
    path('profile/', views.profileView, name='profile'),
    path('cart/details', views.cartDetails, name="cart_details"),
    path('cart/order/edit', views.cart_order_edit, name="cart_order_edit"),
    path('cart/add', views.AddToCart, name="cart_add"),
    path('attractions/filter', views.AttractionsView.as_view(), name="filter"),
    path('attractions/search', views.AttractionsView.as_view(), name="search"),
    path('attractions/sort', views.AttractionsView.as_view(), name="sort"),
    path('planner/<int:pk>', views.PlannerView.as_view(), name='planner')
]
