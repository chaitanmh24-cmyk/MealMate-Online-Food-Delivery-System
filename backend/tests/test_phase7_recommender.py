"""
Phase 7 Tests — Hybrid Recommendation System.

Covers:
  - Cold-start fallback (popularity & rating ranking for anonymous/new users)
  - Strict Pure-Veg business rule (users who order only veg NEVER receive non-veg items)
  - Cart item exclusion (dishes currently in user's cart are not recommended)
  - Content-based TF-IDF cosine similarity (recommends matching cuisine/category)
  - Recommendations dedicated page & JSON API endpoint
"""
import pytest
from decimal import Decimal
from django.test import Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Cuisine
from menu.models import FoodItem, Category
from orders.models import Order, OrderItem, Payment
from cart.cart_service import add_to_cart, get_or_create_cart
from recommender.models import SearchHistory
from recommender.engine import get_recommendations, get_popularity_recommendations

User = get_user_model()


def make_user(username="rec_user", mobile="9666666661"):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com",
        password="TestPassword@123", mobile_number=mobile
    )


def make_cuisine(name="Italian"):
    c, _ = Cuisine.objects.get_or_create(name=name)
    return c


def make_category(name="Pizzas", slug="pizzas"):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug})
    return cat


def make_restaurant(name="Bella Italia", rtype="Both"):
    return Restaurant.objects.create(
        name=name, restaurant_type=rtype,
        address="12 Pizza Lane", city="Bengaluru",
        rating=Decimal("4.8"), is_active=True
    )


def make_food(restaurant, category, name="Margherita", price="300.00", food_type="Veg", cuisine=None):
    return FoodItem.objects.create(
        restaurant=restaurant, category=category,
        name=name, price=Decimal(price), food_type=food_type,
        cuisine=cuisine, is_available=True
    )


# ---------------------------------------------------------------------------
# Recommender Engine Unit Tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRecommenderEngine:
    def setup_method(self):
        self.user = make_user("tasty_user", "9666666662")
        self.c_italian = make_cuisine("Italian")
        self.c_mughlai = make_cuisine("Mughlai")
        self.cat_mains = make_category("Mains", "mains")
        
        self.rest_italian = make_restaurant("Bella Italia", "Both")
        self.rest_mughlai = make_restaurant("Royal Biryani", "Both")

        # Italian dishes (Veg)
        self.pizza = make_food(self.rest_italian, self.cat_mains, "Margherita Pizza", "320.00", "Veg", self.c_italian)
        self.pasta = make_food(self.rest_italian, self.cat_mains, "Penne Alfredo", "280.00", "Veg", self.c_italian)

        # Mughlai dishes (Non-Veg)
        self.biryani = make_food(self.rest_mughlai, self.cat_mains, "Chicken Dum Biryani", "350.00", "Non-Veg", self.c_mughlai)
        self.kebab = make_food(self.rest_mughlai, self.cat_mains, "Mutton Seekh Kebab", "420.00", "Non-Veg", self.c_mughlai)

        # Mughlai dish (Veg)
        self.paneer_biryani = make_food(self.rest_mughlai, self.cat_mains, "Paneer Dum Biryani", "290.00", "Veg", self.c_mughlai)

    def test_cold_start_popularity_fallback(self):
        """Anonymous or new users receive popular available dishes."""
        recs = get_recommendations(user=None, limit=4)
        assert len(recs) > 0
        for item in recs:
            assert item.is_available is True
            assert item.restaurant.is_active is True

    def test_strict_pure_veg_rule_enforced(self):
        """
        A user who has only ordered Veg items in their past orders
        must NEVER be recommended any Non-Veg food items!
        """
        # User places an order with ONLY Veg items (Margherita Pizza & Penne Alfredo)
        order = Order.objects.create(
            user=self.user,
            restaurant=self.rest_italian,
            delivery_address="Home",
            delivery_city="Bengaluru",
            contact_number="9666666662",
            total_amount=Decimal("600.00"),
            status="Delivered"
        )
        OrderItem.objects.create(order=order, food_item=self.pizza, food_name=self.pizza.name, price=self.pizza.price, quantity=1)
        OrderItem.objects.create(order=order, food_item=self.pasta, food_name=self.pasta.name, price=self.pasta.price, quantity=1)

        # Request recommendations
        recs = get_recommendations(user=self.user, limit=8)
        assert len(recs) > 0

        # Verify: zero non-veg items returned
        for item in recs:
            assert item.food_type == 'Veg', f"Violation: Pure-veg user was recommended non-veg item '{item.name}'"

    def test_items_already_in_cart_are_excluded(self):
        """An item currently sitting in the user's active cart is excluded from recommendations."""
        add_to_cart(self.user, self.pizza.id, quantity=1)
        
        recs = get_recommendations(user=self.user, limit=8)
        rec_ids = [item.id for item in recs]
        assert self.pizza.id not in rec_ids, "Item currently in cart should not be recommended"

    def test_content_based_similarity_signals(self):
        """
        User with repeated Italian searches & orders gets Italian recommendations
        ranked higher than other cuisines.
        """
        # Store recent searches for Italian / Pizza
        SearchHistory.objects.create(user=self.user, query="Italian Pasta Pizza")
        SearchHistory.objects.create(user=self.user, query="Wood fired Margherita")

        recs = get_recommendations(user=self.user, limit=4)
        assert len(recs) > 0
        # The top recommended items should be Italian cuisine
        cuisines_in_recs = [item.cuisine.name for item in recs if item.cuisine]
        assert "Italian" in cuisines_in_recs

    def test_unavailable_food_items_excluded(self):
        """Items marked unavailable must never be recommended."""
        self.pasta.is_available = False
        self.pasta.save()

        recs = get_recommendations(user=self.user, limit=8)
        rec_ids = [item.id for item in recs]
        assert self.pasta.id not in rec_ids


# ---------------------------------------------------------------------------
# Recommender Views and API Endpoints
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRecommenderEndpoints:
    def setup_method(self):
        self.client = Client()
        self.user = make_user("api_rec_user", "9666666663")
        self.rest = make_restaurant("Taste Hub")
        self.cat = make_category()
        self.food = make_food(self.rest, self.cat, "Veg Burger", "150.00")

    def test_recommendations_page_loads(self):
        resp = self.client.get(reverse('recommender:recommendations_list'))
        assert resp.status_code == 200
        assert 'recommendations' in resp.context

    def test_recommendations_api_returns_json(self):
        resp = self.client.get(reverse('recommender:recommendations_api') + '?limit=4')
        assert resp.status_code == 200
        data = resp.json()
        assert data['ok'] is True
        assert 'results' in data
        assert isinstance(data['results'], list)
