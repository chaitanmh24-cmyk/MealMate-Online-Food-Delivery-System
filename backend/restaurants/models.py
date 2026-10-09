from django.db import models

class Cuisine(models.Model):
    name = models.CharField(max_length=80, unique=True, db_index=True)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Cuisine"
        verbose_name_plural = "Cuisines"
        ordering = ['name']

    def __str__(self):
        return self.name

class Restaurant(models.Model):
    RESTAURANT_TYPE_CHOICES = (
        ('Veg', 'Pure Veg'),
        ('Non-Veg', 'Non-Veg'),
        ('Both', 'Both Veg & Non-Veg'),
    )

    name = models.CharField(max_length=150, db_index=True)
    restaurant_type = models.CharField(
        max_length=10,
        choices=RESTAURANT_TYPE_CHOICES,
        default='Both',
        db_index=True,
        verbose_name="Restaurant Type"
    )
    address = models.TextField()
    city = models.CharField(max_length=100, db_index=True, default='Bengaluru')
    cuisines = models.ManyToManyField(Cuisine, related_name='restaurants', blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=4.2)
    image = models.URLField(max_length=500, blank=True, default='')
    is_active = models.BooleanField(default=True, verbose_name="Open / Accepting Orders")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Restaurant"
        verbose_name_plural = "Restaurants"
        ordering = ['-rating', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['city']),
            models.Index(fields=['restaurant_type']),
        ]

    def __str__(self):
        return f"{self.name} ({self.get_restaurant_type_display()}, {self.city})"
