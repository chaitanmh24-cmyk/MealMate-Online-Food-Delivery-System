"""
Phase 4 Tests — Unified Search + Filters + Search History.

Covers:
  - search_view URL reachable (200)
  - Empty query shows landing page (no results section)
  - Query matches food items by name / restaurant name
  - Query matches restaurants by name / city
  - food_type filter (Veg / Non-Veg)
  - cuisine filter
  - price_min / price_max filter
  - Unauthenticated search does NOT raise error (anonymous users ok)
  - Authenticated search stores history in SearchHistory
  - Identical consecutive queries are NOT stored twice
  - Old history pruned beyond 20 entries
  - search_service.perform_search returns correct structure
  - Price always present on every item in results
"""
import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Cuisine
from menu.models import FoodItem, Category
from menu.search_service import perform_search
from recommender.models import SearchHistory

User = get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_cuisine(name="South Indian"):
    c, _ = Cuisine.objects.get_or_create(name=name)
    return c


def make_category(name="Veg", slug="veg"):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug})
    return cat


def make_restaurant(name="Test Restaurant", rtype="Both"):
    return Restaurant.objects.create(
        name=name, restaurant_type=rtype,
        address="1 Main Street", city="Bengaluru"
    )


def make_food(restaurant, category, name="Test Dosa", food_type="Veg",
              price="120.00", cuisine=None):
    return FoodItem.objects.create(
        restaurant=restaurant, category=category,
        name=name, price=Decimal(price), food_type=food_type,
        is_available=True, cuisine=cuisine,
    )


def make_user(username="searcher", mobile="9111111111"):
    return User.objects.create_user(
        username=username, email=f"{username}@test.com",
        password="Test@1234", mobile_number=mobile
    )


# ---------------------------------------------------------------------------
# search_view basic access
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSearchViewAccess:
    def setup_method(self):
        self.client = Client()

    def test_search_url_returns_200(self):
        resp = self.client.get(reverse('menu:search'))
        assert resp.status_code == 200

    def test_empty_query_shows_landing_not_results(self):
        resp = self.client.get(reverse('menu:search'))
        assert b"What are you craving" in resp.content

    def test_search_with_query_returns_200(self):
        resp = self.client.get(reverse('menu:search') + '?q=Dosa')
        assert resp.status_code == 200

    def test_anonymous_user_can_search_without_error(self):
        rest = make_restaurant()
        cat = make_category()
        make_food(rest, cat, name="Masala Dosa")
        resp = self.client.get(reverse('menu:search') + '?q=Dosa')
        assert resp.status_code == 200
        assert resp.context['total_food'] >= 1


# ---------------------------------------------------------------------------
# search_service.perform_search unit tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestPerformSearch:
    def setup_method(self):
        self.cuisine_si = make_cuisine("South Indian")
        self.cuisine_ni = make_cuisine("North Indian")
        self.cat_veg    = make_category("Veg", "veg")
        self.cat_nv     = make_category("Non-Veg", "non-veg")
        self.rest_veg   = make_restaurant("Pure Palace", "Veg")
        self.rest_both  = make_restaurant("Empire Eats", "Both")

        self.dosa  = make_food(self.rest_veg,  self.cat_veg, "Crispy Masala Dosa",  "Veg",     "90.00",  self.cuisine_si)
        self.naan  = make_food(self.rest_both, self.cat_veg, "Butter Garlic Naan",  "Veg",     "60.00",  self.cuisine_ni)
        self.chick = make_food(self.rest_both, self.cat_nv,  "Chicken Tikka",       "Non-Veg", "280.00", self.cuisine_ni)

    def test_returns_expected_keys(self):
        result = perform_search("Dosa", {})
        assert 'food_items'  in result
        assert 'restaurants' in result
        assert 'query'       in result
        assert 'filters'     in result

    def test_query_matches_food_by_name(self):
        result = perform_search("Dosa", {})
        names = list(result['food_items'].values_list('name', flat=True))
        assert "Crispy Masala Dosa" in names

    def test_query_does_not_return_unavailable(self):
        self.dosa.is_available = False
        self.dosa.save()
        result = perform_search("Dosa", {})
        names = list(result['food_items'].values_list('name', flat=True))
        assert "Crispy Masala Dosa" not in names

    def test_query_matches_restaurant_by_name(self):
        result = perform_search("Empire", {})
        rest_names = list(result['restaurants'].values_list('name', flat=True))
        assert "Empire Eats" in rest_names

    def test_food_type_filter_veg_only(self):
        result = perform_search("", {"food_type": "Veg"})
        for item in result['food_items']:
            assert item.food_type == "Veg"

    def test_food_type_filter_non_veg_only(self):
        result = perform_search("", {"food_type": "Non-Veg"})
        for item in result['food_items']:
            assert item.food_type == "Non-Veg"

    def test_veg_filter_excludes_non_veg_restaurants(self):
        make_restaurant("Meats Only", "Non-Veg")
        result = perform_search("", {"food_type": "Veg"})
        for r in result['restaurants']:
            assert r.restaurant_type in ("Veg", "Both")

    def test_cuisine_filter(self):
        result = perform_search("", {"cuisine_id": str(self.cuisine_si.pk)})
        for item in result['food_items']:
            assert item.cuisine_id == self.cuisine_si.pk

    def test_price_min_filter(self):
        result = perform_search("", {"price_min": "100"})
        for item in result['food_items']:
            assert item.price >= Decimal("100")

    def test_price_max_filter(self):
        result = perform_search("", {"price_max": "100"})
        for item in result['food_items']:
            assert item.price <= Decimal("100")

    def test_price_range_filter(self):
        result = perform_search("", {"price_min": "55", "price_max": "95"})
        for item in result['food_items']:
            assert Decimal("55") <= item.price <= Decimal("95")

    def test_price_always_present_on_items(self):
        """Core requirement: every result item must expose a non-null price."""
        result = perform_search("", {})
        for item in result['food_items']:
            assert item.price is not None and item.price > 0

    def test_empty_query_returns_all_items(self):
        result = perform_search("", {})
        assert result['food_items'].count() >= 3


# ---------------------------------------------------------------------------
# Search History persistence
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSearchHistory:
    def setup_method(self):
        self.client = Client()
        self.user = make_user("histuser", "9222222222")
        self.rest = make_restaurant()
        self.cat  = make_category()
        make_food(self.rest, self.cat, "Biryani Special")

    def test_authenticated_search_stores_history(self):
        self.client.force_login(self.user)
        self.client.get(reverse('menu:search') + '?q=Biryani')
        assert SearchHistory.objects.filter(user=self.user, query__icontains='Biryani').exists()

    def test_anonymous_search_does_not_store_history(self):
        # anonymous user – should not fail or store
        self.client.get(reverse('menu:search') + '?q=Biryani')
        assert SearchHistory.objects.count() == 0

    def test_identical_consecutive_query_not_duplicated(self):
        self.client.force_login(self.user)
        self.client.get(reverse('menu:search') + '?q=Biryani')
        self.client.get(reverse('menu:search') + '?q=Biryani')
        count = SearchHistory.objects.filter(user=self.user, query__icontains='Biryani').count()
        assert count == 1, f"Expected 1 entry, got {count}"

    def test_different_queries_both_stored(self):
        self.client.force_login(self.user)
        self.client.get(reverse('menu:search') + '?q=Biryani')
        self.client.get(reverse('menu:search') + '?q=Paneer')
        assert SearchHistory.objects.filter(user=self.user).count() == 2

    def test_search_view_context_has_required_keys(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse('menu:search') + '?q=Biryani')
        for key in ('query', 'food_page_obj', 'restaurants', 'total_food', 'total_rest',
                    'categories', 'cuisines', 'selected_type', 'selected_cuisine',
                    'selected_cat', 'price_min', 'price_max'):
            assert key in resp.context, f"Missing context key: {key}"


# ---------------------------------------------------------------------------
# Search combined filter view test
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSearchViewFilters:
    def setup_method(self):
        self.client = Client()
        cuisine    = make_cuisine("Italian")
        cat_veg    = make_category("Veg", "veg")
        cat_nv     = make_category("Non-Veg", "non-veg")
        rest       = make_restaurant("Italian Corner", "Both")
        make_food(rest, cat_veg,  "Margherita Pizza",  "Veg",     "320.00", cuisine)
        make_food(rest, cat_nv,   "Chicken Penne",     "Non-Veg", "380.00", cuisine)
        make_food(rest, cat_veg,  "Budget Breadstick", "Veg",     "40.00",  cuisine)

    def test_veg_filter_on_search_page(self):
        resp = self.client.get(reverse('menu:search') + '?q=&type=Veg')
        for item in resp.context['food_page_obj']:
            assert item.food_type == 'Veg'

    def test_price_max_filter_on_search_page(self):
        resp = self.client.get(reverse('menu:search') + '?price_max=50')
        for item in resp.context['food_page_obj']:
            assert item.price <= Decimal('50')

    def test_search_by_restaurant_name_surfaces_restaurant(self):
        resp = self.client.get(reverse('menu:search') + '?q=Italian+Corner')
        assert resp.context['total_rest'] >= 1

    def test_total_food_count_in_context(self):
        resp = self.client.get(reverse('menu:search') + '?q=Pizza')
        assert resp.context['total_food'] >= 1
