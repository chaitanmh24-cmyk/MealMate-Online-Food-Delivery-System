from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list_view, name='order_list'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('<int:pk>/', views.order_detail_view, name='order_detail'),
    path('<int:pk>/payment/', views.payment_page_view, name='payment_page'),
    path('payment/verify/', views.payment_verify_view, name='payment_verify'),
    path('payment/fail/', views.payment_fail_view, name='payment_fail'),
    path('<int:pk>/success/', views.order_success_view, name='order_success'),
    path('<int:pk>/cancel/', views.cancel_order_view, name='cancel_order'),
]
