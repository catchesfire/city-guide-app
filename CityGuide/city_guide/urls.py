from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('attractions', views.attracions, name='attractions'),
    path('attractions/<int:atrr_id>', views.attracion, name='attraction')
]