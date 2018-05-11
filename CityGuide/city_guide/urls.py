from django.urls import path
from . import views

app_name = 'city_guide'
urlpatterns = [
    path('', views.index, name='index'),
    path('attractions', views.AttractionsView.as_view(), name='attractions'),
    path('attractions/<int:pk>', views.AttracionView.as_view(), name='attraction'),
    path('planner/<int:pk>', views.PlannerView.as_view(), name='planner')
]