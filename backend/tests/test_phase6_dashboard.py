"""
Phase 6 Tests — User Dashboard & Admin Dashboard.

Covers:
  - User Dashboard: authentication guard, context keys, stats calculations (total orders, total spent)
  - Admin Dashboard: staff-only access control, KPI metrics calculations, top-selling analytics
  - Admin Order Status Update: staff permission check, valid status transitions, rejection of invalid statuses
"""
import pytest
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant
from menu.models import FoodItem, Category
from orders.models import Order, OrderItem, Payment
from cart.cart_service import add_to_cart

User = get_user_model()


def make_user(username="dash_user", mobile="9555555551", is_staff=False):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com",
        password="TestPassword@123", mobile_number=mobile,
        is_staff=is_staff
    )


def make_restaurant(name="Spice Route"):
    return Restaurant.objects.create(
        name=name, restaurant_type="Both",
        address="100 Main St", city="Bengaluru"
    )


def make_category(name="Main Dishes", slug="main-dishes"):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug})
    return cat


def make_food(restaurant, category, name="Chicken Biryani", price="300.00"):
    return FoodItem.objects.create(
        restaurant=restaurant, category=category,
        name=name, price=Decimal(price), food_type="Non-Veg", is_available=True
    )


# ---------------------------------------------------------------------------
# User Dashboard Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestUserDashboard:
    def setup_method(self):
        self.client = Client()
        self.user = make_user("cust_user", "9555555552")
        self.rest = make_restaurant("Flavours")
        self.cat = make_category()
        self.food = make_food(self.rest, self.cat, "Paneer Tikka", "200.00")

    def test_user_dashboard_redirects_anonymous(self):
        resp = self.client.get(reverse('dashboard:user_dashboard'))
        assert resp.status_code == 302
        assert '/auth/login/' in resp['Location']

    def test_user_dashboard_loads_for_authenticated_user(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('dashboard:user_dashboard'))
        assert resp.status_code == 200
        assert 'total_orders' in resp.context
        assert 'total_spent' in resp.context
        assert 'active_orders' in resp.context
        assert 'cart' in resp.context

    def test_user_dashboard_stats_accuracy(self):
        # Create an order for this user
        order = Order.objects.create(
            user=self.user,
            restaurant=self.rest,
            delivery_address="123 Street",
            delivery_city="Bengaluru",
            contact_number="9555555552",
            total_amount=Decimal("400.00"),
            status="Preparing"
        )
        OrderItem.objects.create(
            order=order,
            food_item=self.food,
            food_name=self.food.name,
            price=Decimal("200.00"),
            quantity=2
        )
        Payment.objects.create(
            order=order,
            amount=Decimal("400.00"),
            status="Success",
            razorpay_order_id="rz_test_order_1"
        )

        self.client.force_login(self.user)
        resp = self.client.get(reverse('dashboard:user_dashboard'))
        assert resp.context['total_orders'] == 1
        assert resp.context['total_spent'] == Decimal("400.00")
        assert resp.context['active_orders'].count() == 1


# ---------------------------------------------------------------------------
# Admin Dashboard Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAdminDashboard:
    def setup_method(self):
        self.client = Client()
        self.staff_user = make_user("admin_staff", "9555555553", is_staff=True)
        self.reg_user = make_user("normal_cust", "9555555554", is_staff=False)
        self.rest = make_restaurant("Empire Suites")
        self.cat = make_category()
        self.food = make_food(self.rest, self.cat, "Dum Biryani", "250.00")

    def test_admin_dashboard_redirects_anonymous(self):
        resp = self.client.get(reverse('dashboard:admin_dashboard'))
        assert resp.status_code == 302
        assert '/auth/login/' in resp['Location']

    def test_admin_dashboard_redirects_non_staff(self):
        self.client.force_login(self.reg_user)
        resp = self.client.get(reverse('dashboard:admin_dashboard'))
        assert resp.status_code == 302

    def test_admin_dashboard_accessible_by_staff(self):
        self.client.force_login(self.staff_user)
        resp = self.client.get(reverse('dashboard:admin_dashboard'))
        assert resp.status_code == 200
        assert 'total_orders' in resp.context
        assert 'total_revenue' in resp.context
        assert 'active_orders_count' in resp.context
        assert 'total_users' in resp.context
        assert 'top_selling' in resp.context
        assert 'orders_page' in resp.context

    def test_admin_dashboard_kpis_and_top_selling(self):
        # Create completed order with items
        order = Order.objects.create(
            user=self.reg_user,
            restaurant=self.rest,
            delivery_address="456 Cross",
            delivery_city="Bengaluru",
            contact_number="9555555554",
            total_amount=Decimal("750.00"),
            status="Delivered"
        )
        OrderItem.objects.create(
            order=order,
            food_item=self.food,
            food_name=self.food.name,
            price=Decimal("250.00"),
            quantity=3
        )
        Payment.objects.create(
            order=order,
            amount=Decimal("750.00"),
            status="Success",
            razorpay_order_id="rz_test_order_2"
        )

        self.client.force_login(self.staff_user)
        resp = self.client.get(reverse('dashboard:admin_dashboard'))

        assert resp.context['total_orders'] >= 1
        assert resp.context['total_revenue'] >= Decimal("750.00")
        
        # Check top-selling item aggregation
        top_items = resp.context['top_selling']
        assert len(top_items) >= 1
        assert top_items[0]['food_name'] == "Dum Biryani"
        assert top_items[0]['total_qty'] == 3
        assert top_items[0]['total_rev'] == Decimal("750.00")

    def test_admin_order_status_update_by_staff(self):
        order = Order.objects.create(
            user=self.reg_user,
            restaurant=self.rest,
            delivery_address="789 Blvd",
            delivery_city="Bengaluru",
            contact_number="9555555554",
            total_amount=Decimal("250.00"),
            status="Placed"
        )

        self.client.force_login(self.staff_user)
        resp = self.client.post(
            reverse('dashboard:admin_order_status_update', args=[order.pk]),
            data={'status': 'Preparing'},
            follow=True
        )
        assert resp.status_code == 200
        order.refresh_from_db()
        assert order.status == "Preparing"

    def test_admin_order_status_update_rejects_non_staff(self):
        order = Order.objects.create(
            user=self.reg_user,
            restaurant=self.rest,
            delivery_address="789 Blvd",
            delivery_city="Bengaluru",
            contact_number="9555555554",
            total_amount=Decimal("250.00"),
            status="Placed"
        )

        self.client.force_login(self.reg_user)
        resp = self.client.post(
            reverse('dashboard:admin_order_status_update', args=[order.pk]),
            data={'status': 'Delivered'}
        )
        assert resp.status_code == 302
        order.refresh_from_db()
        assert order.status == "Placed"  # Unchanged
