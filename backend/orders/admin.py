from django.contrib import admin
from .models import Order, OrderItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('food_item', 'food_name', 'price', 'quantity')

class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'user', 'restaurant', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at', 'restaurant')
    search_fields = ('order_number', 'user__username', 'user__email', 'contact_number')
    list_editable = ('status',)
    inlines = [OrderItemInline, PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'razorpay_order_id', 'razorpay_payment_id', 'status', 'amount', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('razorpay_order_id', 'razorpay_payment_id', 'order__order_number')
