import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError
from accounts.models import User
from restaurants.models import Cuisine, Restaurant
from menu.models import Category, FoodItem
from cart.models import Cart, CartItem
from orders.models import Order, OrderItem, Payment
from recommender.models import SearchHistory

@pytest.mark.django_db
def test_user_creation_and_mobile_validation():
    # Valid user
    user = User.objects.create_user(
        username='rahul_test',
        email='rahul@example.com',
        password='StrongPassword123!',
        mobile_number='9876543210',
        gender='M'
    )
    user.full_clean()
    assert user.email == 'rahul@example.com'
    assert user.mobile_number == '9876543210'

    # Invalid mobile (starts with 1, only 5 digits)
    invalid_user = User(
        username='bad_user',
        email='bad@example.com',
        mobile_number='12345',
        gender='M'
    )
    with pytest.raises(ValidationError):
        invalid_user.full_clean()

@pytest.mark.django_db
def test_veg_restaurant_business_rule():
    veg_rest = Restaurant.objects.create(
        name='Shanthi Sagar',
        restaurant_type='Veg',
        address='Indiranagar',
        city='Bengaluru'
    )
    cat = Category.objects.create(name='Main Course')

    # Allowed: Veg food in Pure Veg restaurant
    veg_item = FoodItem.objects.create(
        restaurant=veg_rest,
        category=cat,
        name='Paneer Butter Masala',
        price=Decimal('220.00'),
        food_type='Veg'
    )
    assert veg_item.pk is not None

    # Forbidden: Non-Veg food in Pure Veg restaurant must raise ValidationError
    with pytest.raises(ValidationError):
        FoodItem.objects.create(
            restaurant=veg_rest,
            category=cat,
            name='Chicken Tikka',
            price=Decimal('290.00'),
            food_type='Non-Veg'
        )

@pytest.mark.django_db
def test_order_item_price_snapshot():
    rest = Restaurant.objects.create(name='Meghana Foods', restaurant_type='Both', address='Koramangala')
    cat = Category.objects.create(name='Biryani')
    user = User.objects.create_user(username='test_buyer', email='buyer@example.com', password='PassWord123!', mobile_number='9876543211')
    
    item = FoodItem.objects.create(
        restaurant=rest,
        category=cat,
        name='Chicken Biryani',
        price=Decimal('310.00'),
        food_type='Non-Veg'
    )

    order = Order.objects.create(
        user=user,
        restaurant=rest,
        delivery_address='Flat 402, Embassy Heights',
        contact_number='9876543211',
        total_amount=Decimal('310.00')
    )

    order_item = OrderItem.objects.create(
        order=order,
        food_item=item,
        food_name=item.name,
        price=item.price, # snapshot
        quantity=1
    )

    # Now edit menu item price to 380.00
    item.price = Decimal('380.00')
    item.save()

    # Old order item price must remain 310.00
    order_item.refresh_from_db()
    assert order_item.price == Decimal('310.00')
