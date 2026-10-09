"""
Phase 5 Tests — Cart, Orders, Razorpay Payment, and Cancellation Flow.

Covers:
  - Cart single-restaurant enforcement (MixedRestaurantError / HTTP 409)
  - Cart add, update, remove, clear (fetch API endpoints and service)
  - Cart subtotal and total calculations
  - Order creation and price snapshot (immutability against future FoodItem edits)
  - Razorpay payment creation & verification (success advances status to Preparing)
  - Razorpay payment failure handling
  - Cancellation business rule (allowed only in 'Placed' status)
  - IDOR protection (users cannot view/cancel other users' orders)
"""
import pytest
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Cuisine
from menu.models import FoodItem, Category
from cart.models import Cart, CartItem
from cart.cart_service import (
    get_or_create_cart, add_to_cart, update_cart_item,
    remove_from_cart, clear_cart, MixedRestaurantError
)
from orders.models import Order, OrderItem, Payment
from orders.order_service import place_order, verify_payment, fail_payment, cancel_order

User = get_user_model()


def make_user(username="cartuser", mobile="9333333331"):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com",
        password="TestPassword@123", mobile_number=mobile
    )


def make_restaurant(name="Spice Haven", rtype="Both"):
    return Restaurant.objects.create(
        name=name, restaurant_type=rtype,
        address="100 Main St", city="Bengaluru"
    )


def make_category(name="Mains", slug="mains"):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug})
    return cat


def make_food(restaurant, category, name="Paneer Biryani", price="250.00"):
    return FoodItem.objects.create(
        restaurant=restaurant, category=category,
        name=name, price=Decimal(price), food_type="Veg", is_available=True
    )


# ---------------------------------------------------------------------------
# Cart Service & Business Rules
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCartService:
    def setup_method(self):
        self.user = make_user("cart_tester_1", "9444444441")
        self.rest1 = make_restaurant("Rest A")
        self.rest2 = make_restaurant("Rest B")
        self.cat = make_category()
        self.food1 = make_food(self.rest1, self.cat, "Dosa", "100.00")
        self.food2 = make_food(self.rest1, self.cat, "Idli", "60.00")
        self.food_other = make_food(self.rest2, self.cat, "Burger", "150.00")

    def test_add_to_cart_success(self):
        res = add_to_cart(self.user, self.food1.id, quantity=2)
        cart = get_or_create_cart(self.user)
        assert res['cart_count'] == 2
        assert cart.restaurant == self.rest1
        assert cart.total_amount == Decimal("200.00")

    def test_add_multiple_items_same_restaurant(self):
        add_to_cart(self.user, self.food1.id, quantity=1)
        add_to_cart(self.user, self.food2.id, quantity=2)
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 3
        assert cart.total_amount == Decimal("220.00")  # 100 + 2*60

    def test_single_restaurant_rule_raises_error(self):
        add_to_cart(self.user, self.food1.id, quantity=1)
        with pytest.raises(MixedRestaurantError):
            add_to_cart(self.user, self.food_other.id, quantity=1)

    def test_update_cart_quantity(self):
        add_to_cart(self.user, self.food1.id, quantity=1)
        update_cart_item(self.user, self.food1.id, quantity=5)
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 5
        assert cart.total_amount == Decimal("500.00")

    def test_update_quantity_zero_removes_item(self):
        add_to_cart(self.user, self.food1.id, quantity=1)
        res = update_cart_item(self.user, self.food1.id, quantity=0)
        assert res['removed'] is True
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 0
        assert cart.restaurant is None

    def test_remove_from_cart(self):
        add_to_cart(self.user, self.food1.id, quantity=2)
        remove_from_cart(self.user, self.food1.id)
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 0

    def test_clear_cart(self):
        add_to_cart(self.user, self.food1.id, quantity=2)
        clear_cart(self.user)
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 0
        assert cart.restaurant is None


# ---------------------------------------------------------------------------
# Cart API Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestCartEndpoints:
    def setup_method(self):
        self.client = Client()
        self.user = make_user("api_cart_user", "9444444442")
        self.rest1 = make_restaurant("API Rest 1")
        self.rest2 = make_restaurant("API Rest 2")
        self.cat = make_category()
        self.food1 = make_food(self.rest1, self.cat, "Noodles", "120.00")
        self.food2 = make_food(self.rest2, self.cat, "Pasta", "180.00")
        self.client.force_login(self.user)

    def test_cart_detail_page_loads(self):
        resp = self.client.get(reverse('cart:cart_detail'))
        assert resp.status_code == 200

    def test_cart_add_endpoint(self):
        resp = self.client.post(
            reverse('cart:cart_add'),
            data={'food_item_id': self.food1.id, 'quantity': 2},
            content_type='application/json'
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data['ok'] is True
        assert data['cart_count'] == 2

    def test_cart_add_mixed_restaurant_returns_409_conflict(self):
        # Add from rest 1
        self.client.post(
            reverse('cart:cart_add'),
            data={'food_item_id': self.food1.id, 'quantity': 1},
            content_type='application/json'
        )
        # Attempt to add from rest 2
        resp = self.client.post(
            reverse('cart:cart_add'),
            data={'food_item_id': self.food2.id, 'quantity': 1},
            content_type='application/json'
        )
        assert resp.status_code == 409
        data = resp.json()
        assert data['conflict'] is True
        assert 'API Rest 1' in data['current_restaurant']
        assert 'API Rest 2' in data['new_restaurant']

    def test_cart_clear_endpoint(self):
        add_to_cart(self.user, self.food1.id, 1)
        resp = self.client.post(reverse('cart:cart_clear'))
        assert resp.status_code == 200
        assert resp.json()['cart_count'] == 0


# ---------------------------------------------------------------------------
# Order & Payment Service Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestOrderService:
    def setup_method(self):
        self.user = make_user("order_user_1", "9444444443")
        self.rest = make_restaurant("Royal Tandoor")
        self.cat = make_category()
        self.food = make_food(self.rest, self.cat, "Butter Chicken", "350.00")
        add_to_cart(self.user, self.food.id, quantity=2)

    def test_place_order_creates_order_and_snapshot(self):
        result = place_order(
            user=self.user,
            delivery_address="Flat 202, Palm Heights",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        order = result['order']
        payment = result['payment']

        assert order.pk is not None
        assert order.status == 'Placed'
        assert order.total_amount == Decimal("700.00")
        assert order.order_number.startswith("MM-")

        # Check OrderItem snapshot
        order_item = order.items.first()
        assert order_item.food_name == "Butter Chicken"
        assert order_item.price == Decimal("350.00")
        assert order_item.quantity == 2
        assert order_item.subtotal == Decimal("700.00")

        # Cart should be cleared
        cart = get_or_create_cart(self.user)
        assert cart.total_items_count == 0

        # Check Payment record
        assert payment.order == order
        assert payment.status == 'Pending'
        assert payment.amount == Decimal("700.00")

    def test_price_snapshot_immutability(self):
        """Editing food item price later must NOT alter past order snapshots."""
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        order = result['order']

        # Admin changes price of food item from 350 to 500
        self.food.price = Decimal("500.00")
        self.food.save()

        # Order item must retain original frozen price snapshot of 350
        order_item = order.items.first()
        order_item.refresh_from_db()
        assert order_item.price == Decimal("350.00")
        assert order_item.subtotal == Decimal("700.00")

    def test_verify_payment_success_advances_order_to_preparing(self):
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        payment = result['payment']

        # Verify payment using simulator mock signature
        verified_payment = verify_payment(
            razorpay_order_id=payment.razorpay_order_id,
            razorpay_payment_id="pay_test_999",
            razorpay_signature="mock_signature_valid"
        )

        assert verified_payment.status == 'Success'
        assert verified_payment.order.status == 'Preparing'

    def test_fail_payment_marks_payment_failed(self):
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        payment = result['payment']
        fail_payment(payment.razorpay_order_id, reason="User cancelled")

        payment.refresh_from_db()
        assert payment.status == 'Failed'
        assert payment.order.status == 'Placed'

    def test_cancel_order_when_placed_success(self):
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        order = result['order']
        cancelled = cancel_order(order, self.user)
        assert cancelled.status == 'Cancelled'

    def test_cancel_order_forbidden_once_preparing(self):
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        order = result['order']
        order.status = 'Preparing'
        order.save()

        with pytest.raises(ValueError):
            cancel_order(order, self.user)

    def test_cancel_order_idor_protection(self):
        other_user = make_user("other_user", "9444444444")
        result = place_order(
            user=self.user,
            delivery_address="Test Address",
            delivery_city="Bengaluru",
            contact_number="9444444443"
        )
        order = result['order']

        with pytest.raises(PermissionError):
            cancel_order(order, other_user)
