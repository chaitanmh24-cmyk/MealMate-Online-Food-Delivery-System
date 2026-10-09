from django.urls import path
from .views import signup_view, login_view, logout_view, profile_view, forgot_password_view

app_name = 'accounts'

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
]
