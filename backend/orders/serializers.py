from rest_framework import serializers
from .models import Cart, CartItem, Order, OrderItem, Payment
from restaurants.serializers import FoodItemSerializer, RestaurantSerializer
from users.serializers import AddressSerializer

class CartItemSerializer(serializers.ModelSerializer):
    food_item_details = FoodItemSerializer(source='food_item', read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'cart', 'food_item', 'food_item_details', 'quantity']
        read_only_fields = ['cart']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'created_at']
        read_only_fields = ['user']

    def get_total_price(self, obj):
        return sum(item.quantity * item.food_item.price for item in obj.items.all())

class OrderItemSerializer(serializers.ModelSerializer):
    food_item_details = FoodItemSerializer(source='food_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'food_item', 'food_item_details', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    delivery_address_details = AddressSerializer(source='delivery_address', read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'restaurant', 'delivery_address', 'delivery_address_details', 'total_amount', 'status', 'created_at', 'items']
        read_only_fields = ['user', 'total_amount', 'status', 'restaurant']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
