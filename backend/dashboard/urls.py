from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('dashboard/user/', views.user_dashboard_view, name='user_dashboard'),
    path('dashboard/admin/', views.admin_dashboard_view, name='admin_dashboard'),
    path('dashboard/admin/orders/<int:pk>/status/', views.admin_update_order_status, name='admin_order_status_update'),
]
