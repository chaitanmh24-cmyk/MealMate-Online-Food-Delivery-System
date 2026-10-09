from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserLoginForm, UserProfileUpdateForm
from .models import User

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome to MealMate, {user.first_name}! Your account has been created successfully.")
            return redirect('/')
        else:
            messages.error(request, "Please correct the errors below to register.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/signup.html', {'form': form, 'title': 'Create Your Account — MealMate'})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    next_url = request.GET.get('next', '/')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            user = form.user
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome back, {user.first_name or user.username}!")
            if user.is_staff and next_url == '/':
                return redirect('/admin/')
            return redirect(next_url if next_url else '/')
        else:
            messages.error(request, "Invalid credentials. Please verify your email/username and password.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url,
        'title': 'Sign In — MealMate'
    })

def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out. See you soon!")
    return redirect('/')

@login_required(login_url='/auth/login/')
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile details have been updated successfully!")
            return redirect('/auth/profile/')
        else:
            messages.error(request, "Failed to update profile. Please check the errors below.")
    else:
        form = UserProfileUpdateForm(instance=user)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'user': user,
        'title': 'My Profile — MealMate'
    })

def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        if email:
            messages.success(request, f"If an account exists with {email}, password recovery instructions have been sent.")
            return redirect('/auth/login/')
        else:
            messages.error(request, "Please enter your registered email address.")
    return render(request, 'accounts/forgot_password.html', {'title': 'Forgot Password — MealMate'})
