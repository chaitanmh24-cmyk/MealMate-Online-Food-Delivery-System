from rest_framework import viewsets, permissions, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Cart, CartItem, Order, OrderItem, Payment
from .serializers import CartSerializer, CartItemSerializer, OrderSerializer, PaymentSerializer

class CartViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartSerializer

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart

    @action(detail=False, methods=['get'])
    def my_cart(self, request):
        cart = self.get_object()
        serializer = self.get_serializer(cart)
        return Response(serializer.data)

class CartItemViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CartItemSerializer

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)

    def perform_create(self, serializer):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        # Check if item already exists in cart, if so update quantity
        food_item = serializer.validated_data['food_item']
        quantity = serializer.validated_data.get('quantity', 1)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, food_item=food_item)
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        else:
            cart_item.quantity = quantity
            cart_item.save()

class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSerializer

    def get_queryset(self):
        if self.request.user.role == 'Admin':
            return Order.objects.all()
        elif self.request.user.role == 'RestaurantOwner':
            return Order.objects.filter(restaurant__owner=self.request.user)
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # We need to calculate total amount from cart before placing order.
        cart = Cart.objects.get(user=self.request.user)
        items = cart.items.all()
        if not items:
            raise serializers.ValidationError("Cart is empty")

        total = sum(item.quantity * item.food_item.price for item in items)
        
        # In a real app we might handle multiple restaurants. Here we assume all items are from the same restaurant for simplicity.
        restaurant = items[0].food_item.restaurant
        
        order = serializer.save(user=self.request.user, total_amount=total, restaurant=restaurant)

        # Move items from cart to order
        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                food_item=cart_item.food_item,
                quantity=cart_item.quantity,
                price=cart_item.food_item.price
            )
        
        # Clear cart
        cart.items.all().delete()
