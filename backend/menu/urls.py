from django.urls import path
from . import views

app_name = 'menu'

urlpatterns = [
    # Public menu browsing
    path('', views.food_list_view, name='food_list'),
    path('search/', views.search_view, name='search'),
    path('<int:pk>/', views.food_detail_view, name='food_detail'),

    # Staff-only food item CRUD
    path('admin/food/', views.admin_food_list_view, name='admin_food_list'),
    path('admin/food/add/', views.admin_food_create_view, name='admin_food_create'),
    path('admin/food/<int:pk>/edit/', views.admin_food_update_view, name='admin_food_update'),
    path('admin/food/<int:pk>/delete/', views.admin_food_delete_view, name='admin_food_delete'),
]
