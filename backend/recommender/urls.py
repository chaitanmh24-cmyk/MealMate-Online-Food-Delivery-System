from django.urls import path
from . import views

app_name = 'recommender'

urlpatterns = [
    path('', views.recommendations_view, name='recommendations_list'),
    path('api/', views.recommendations_api, name='recommendations_api'),
]
