from rest_framework import serializers
from .models import Restaurant, Category, FoodItem, Review
from users.serializers import UserSerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['user']

class FoodItemSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source='category.name')
    restaurant_name = serializers.ReadOnlyField(source='restaurant.name')
    restaurant_location = serializers.ReadOnlyField(source='restaurant.location')
    reviews = ReviewSerializer(many=True, read_only=True)

    class Meta:
        model = FoodItem
        fields = [
            'id', 'name', 'description', 'price', 'veg_nonveg',
            'cuisine_type', 'image', 'is_available',
            'restaurant', 'restaurant_name', 'restaurant_location',
            'category', 'category_name', 'reviews',
        ]

class RestaurantSerializer(serializers.ModelSerializer):
    food_items = FoodItemSerializer(many=True, read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    owner_name = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Restaurant
        fields = [
            'id', 'name', 'description', 'location', 'veg_nonveg',
            'image', 'status', 'created_at',
            'owner', 'owner_name', 'food_items', 'reviews',
        ]
        read_only_fields = ['owner']
