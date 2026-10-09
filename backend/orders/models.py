import uuid
from django.db import models
from django.conf import settings

class Order(models.Model):
    STATUS_CHOICES = (
        ('Placed', 'Order Placed'),
        ('Preparing', 'Preparing Food'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=32, unique=True, db_index=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )
    restaurant = models.ForeignKey(
        'restaurants.Restaurant',
        on_delete=models.PROTECT,
        related_name='orders'
    )
    delivery_address = models.TextField(verbose_name="Delivery Address")
    delivery_city = models.CharField(max_length=100, default='Bengaluru')
    contact_number = models.CharField(max_length=15, verbose_name="Contact Number")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Placed',
        db_index=True,
        verbose_name="Order Status"
    )
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Order"
        verbose_name_plural = "Orders"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"MM-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order #{self.order_number} ({self.status}) - ₹{self.total_amount}"

    @property
    def can_cancel(self):
        """Order can only be cancelled BEFORE the 'Preparing' stage (i.e. only when Placed)."""
        return self.status == 'Placed'

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )
    food_item = models.ForeignKey(
        'menu.FoodItem',
        on_delete=models.PROTECT,
        related_name='order_items'
    )
    food_name = models.CharField(max_length=150, verbose_name="Item Name Snapshot")
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Price Snapshot (₹)",
        help_text="Historical price snapshot so future price edits do not affect old orders"
    )
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Order Item"
        verbose_name_plural = "Order Items"

    def __str__(self):
        return f"{self.quantity}x {self.food_name} @ ₹{self.price} in #{self.order.order_number}"

    @property
    def subtotal(self):
        return self.price * self.quantity

class Payment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Success', 'Success'),
        ('Failed', 'Payment Failed'),
        ('Cancelled', 'Payment Cancelled'),
    )

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name='payment'
    )
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True, db_index=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='Pending',
        db_index=True
    )
    payment_method = models.CharField(max_length=50, default='Razorpay')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

    def __str__(self):
        return f"Payment for #{self.order.order_number} - {self.status} (₹{self.amount})"
