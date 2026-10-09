from django.db import models
from django.conf import settings

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cart'
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='active_carts'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart"
        verbose_name_plural = "Carts"

    def __str__(self):
        return f"Cart of {self.user.username}"

    @property
    def total_amount(self):
        return sum(item.subtotal for item in self.items.select_related('food_item').all())

    @property
    def total_items_count(self):
        return sum(item.quantity for item in self.items.all())

    def clear(self):
        self.items.all().delete()
        self.restaurant = None
        self.save(update_fields=['restaurant', 'updated_at'])

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items'
    )
    food_item = models.ForeignKey(
        'menu.FoodItem',
        on_delete=models.CASCADE,
        related_name='cart_items'
    )
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cart Item"
        verbose_name_plural = "Cart Items"
        unique_together = ('cart', 'food_item')

    def __str__(self):
        return f"{self.quantity}x {self.food_item.name} in Cart #{self.cart.id}"

    @property
    def subtotal(self):
        return self.food_item.price * self.quantity
