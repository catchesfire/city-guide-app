from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'city_guide'
urlpatterns = [
    path('', views.index, name='index'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction'),
    path('cart', views.CartView.as_view(), name="cart"),
    path('login', auth_views.login, name="login")
]