from django.urls import path
from django.contrib.auth.views import logout
from django.conf import settings
from . import views

app_name = 'city_guide'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.UserFormView.as_view(), name='register'),
    path('login/', views.UserLogFormView.as_view(), name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction')
]