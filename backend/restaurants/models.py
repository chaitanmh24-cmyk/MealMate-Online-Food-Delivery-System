from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    VEG_CHOICES = (
        ('Veg', 'Pure Vegetarian'),
        ('Non-Veg', 'Non-Vegetarian'),
        ('Both', 'Veg & Non-Veg'),
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True, help_text='Full address or area of the restaurant')
    veg_nonveg = models.CharField(max_length=10, choices=VEG_CHOICES, default='Both')
    image = models.URLField(max_length=1024, blank=True, null=True, help_text='Paste a valid image URL (https://...)')
    status = models.BooleanField(default=True)  # True = Active, False = Inactive
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='food_items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='food_items')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    veg_nonveg = models.CharField(max_length=10, choices=(('Veg', 'Veg'), ('Non-Veg', 'Non-Veg')), default='Veg')
    cuisine_type = models.CharField(max_length=100, blank=True, null=True)
    image = models.URLField(max_length=1024, blank=True, null=True, help_text="Provide a valid image URL")
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} - {self.rating} stars"
