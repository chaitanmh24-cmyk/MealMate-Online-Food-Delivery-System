from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.restaurant_list_view, name='restaurant_list'),
    path('<int:pk>/', views.restaurant_detail_view, name='restaurant_detail'),
]
