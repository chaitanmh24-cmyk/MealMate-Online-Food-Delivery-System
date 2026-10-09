from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

indian_mobile_validator = RegexValidator(
    regex=r'^[6-9]\d{9}$',
    message="Enter a valid 10-digit Indian mobile number starting with 6, 7, 8, or 9."
)

class User(AbstractUser):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('N', 'Prefer not to say'),
    )

    email = models.EmailField(unique=True, verbose_name="Email Address", db_index=True)
    mobile_number = models.CharField(
        max_length=10,
        unique=True,
        validators=[indian_mobile_validator],
        verbose_name="Mobile Number",
        db_index=True
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        default='N',
        verbose_name="Gender"
    )
    address = models.TextField(blank=True, default='', verbose_name="Default Delivery Address")
    city = models.CharField(max_length=100, blank=True, default='Bengaluru', verbose_name="City")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    REQUIRED_FIELDS = ['email', 'mobile_number']

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['mobile_number']),
        ]

    def __str__(self):
        return f"{self.username} ({self.email})"

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name if name else self.username
