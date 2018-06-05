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
    path('logout/', views.logout_user, name='logout'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction'),
    path('profile/', views.update_profile, name='profile'),
    path('profile/update', views.profileView, name='profile_update'),
    path('profile/change', views.passwordView, name='profile_change'),
    path('cart', views.cart, name="cart"),
    path('cart/details', views.cart_details, name="cart_details"),
    path('cart/order/edit', views.cart_order_edit, name="cart_order_edit"),
    path('cart/add', views.cart_add, name="cart_add"),
    path('attractions/filter', views.AttractionsView.as_view(), name="filter"),
    path('attractions/search', views.AttractionsView.as_view(), name="search"),
    path('attractions/sort', views.AttractionsView.as_view(), name="sort"),
    path('planner/<int:pk>', views.PlannerView.as_view(), name='planner'),
    path('planner/add', views.planner_add, name="planner_add"),
    path('planner/add-break/<int:pk>', views.planner_add_break, name="planner_add_break"),
    path('planner/edit/<int:pk>', views.planner_edit, name="planner_edit")
]
