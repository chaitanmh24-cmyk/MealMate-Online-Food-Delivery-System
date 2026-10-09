import re
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'})
    )
    mobile_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit Mobile Number'})
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Delivery address (street, locality)'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        initial='Bengaluru',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create strong password'})
    )
    confirm_password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm password'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'gender', 'address', 'city']

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email address already exists.")
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number').strip()
        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9.")
        if User.objects.filter(mobile_number=mobile).exists():
            raise ValidationError("An account with this mobile number already exists.")
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password:
            if password != confirm_password:
                self.add_error('confirm_password', "Passwords do not match.")
            else:
                try:
                    validate_password(password)
                except ValidationError as e:
                    self.add_error('password', e)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        # Use email prefix or sanitized name as username
        base_username = self.cleaned_data['email'].split('@')[0]
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        user.username = username
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    username_or_email = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email address or Username', 'autofocus': True})
    )
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )

    def clean(self):
        cleaned_data = super().clean()
        identifier = cleaned_data.get('username_or_email', '').strip()
        password = cleaned_data.get('password')

        if identifier and password:
            # Check if identifier is email
            user_obj = None
            if '@' in identifier:
                user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj:
                    user = authenticate(username=user_obj.username, password=password)
                else:
                    user = None
            else:
                user = authenticate(username=identifier, password=password)

            if not user:
                raise ValidationError("Invalid login credentials. Please check your username/email and password.")
            if not user.is_active:
                raise ValidationError("This account is inactive. Please contact support.")
            self.user = user
        return cleaned_data


class UserProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    mobile_number = forms.CharField(
        max_length=10,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    gender = forms.ChoiceField(
        choices=User.GENDER_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'mobile_number', 'gender', 'address', 'city']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = self.instance.email
        self.original_mobile = self.instance.mobile_number

    def clean_email(self):
        email = self.cleaned_data.get('email').strip().lower()
        if email != self.original_email and User.objects.filter(email=email).exists():
            raise ValidationError("This email is already in use by another account.")
        return email

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number').strip()
        if not re.match(r'^[6-9]\d{9}$', mobile):
            raise ValidationError("Enter a valid 10-digit Indian mobile number.")
        if mobile != self.original_mobile and User.objects.filter(mobile_number=mobile).exists():
            raise ValidationError("This mobile number is already in use by another account.")
        return mobile
