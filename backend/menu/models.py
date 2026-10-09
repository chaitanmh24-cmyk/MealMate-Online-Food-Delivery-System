from django.db import models
from django.core.exceptions import ValidationError
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default='')
    icon = models.CharField(max_length=10, blank=True, default='🍽️')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class FoodItem(models.Model):
    FOOD_TYPE_CHOICES = (
        ('Veg', 'Veg'),
        ('Non-Veg', 'Non-Veg'),
    )

    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.CASCADE,
        related_name='food_items',
        null=False,
        blank=False,
        verbose_name="Restaurant"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='food_items',
        verbose_name="Category"
    )
    cuisine = models.ForeignKey(
        'restaurants.Cuisine',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='food_items',
        verbose_name="Cuisine"
    )
    name = models.CharField(max_length=150, db_index=True, verbose_name="Food Name")
    description = models.TextField(blank=True, default='')
    price = models.DecimalField(max_digits=8, decimal_places=2, db_index=True, verbose_name="Price (₹)")
    food_type = models.CharField(
        max_length=10,
        choices=FOOD_TYPE_CHOICES,
        default='Veg',
        db_index=True,
        verbose_name="Type (Veg/Non-Veg)"
    )
    image = models.URLField(max_length=500, blank=True, default='')
    is_available = models.BooleanField(default=True, db_index=True, verbose_name="Available")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Food Item"
        verbose_name_plural = "Food Items"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['price']),
            models.Index(fields=['food_type']),
            models.Index(fields=['is_available']),
            models.Index(fields=['restaurant', 'is_available']),
        ]

    def clean(self):
        super().clean()
        if self.restaurant_id:
            from restaurants.models import Restaurant
            try:
                restaurant = self.restaurant
            except Restaurant.DoesNotExist:
                return

            # Strict business rule: Pure-Veg restaurant cannot offer Non-Veg items
            if restaurant.restaurant_type == 'Veg' and self.food_type == 'Non-Veg':
                raise ValidationError({
                    'food_type': f"Business Rule Violation: Restaurant '{restaurant.name}' is registered as Pure-Veg and cannot have Non-Veg items."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - ₹{self.price} ({self.restaurant.name})"
