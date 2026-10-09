"""
Phase 3 Tests — Restaurants, Menu, Admin Food CRUD.

Covers:
  - Restaurant model integrity (Pure-Veg constraint)
  - Restaurant listing / detail views (status codes, context data)
  - Food item listing / detail views
  - Price always present in food card context
  - Admin CRUD views (permission checks, create, update, delete)
  - FoodItemAdminForm validation (Pure-Veg rule)
"""
import pytest
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from restaurants.models import Restaurant, Cuisine
from menu.models import FoodItem, Category
from menu.forms import FoodItemAdminForm

User = get_user_model()


# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

def make_cuisine(name="South Indian"):
    c, _ = Cuisine.objects.get_or_create(name=name)
    return c


def make_category(name="Veg", slug="veg"):
    cat, _ = Category.objects.get_or_create(name=name, defaults={"slug": slug})
    return cat


def make_restaurant(name="Test Kitchen", rtype="Both"):
    return Restaurant.objects.create(
        name=name, restaurant_type=rtype,
        address="1 Test Lane", city="Bengaluru"
    )


def make_food(restaurant, category, name="Test Dosa", food_type="Veg", price="120.00"):
    return FoodItem.objects.create(
        restaurant=restaurant, category=category,
        name=name, price=Decimal(price), food_type=food_type,
        is_available=True,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRestaurantModel:
    def test_str_representation(self):
        r = make_restaurant("Idli House", "Veg")
        assert "Idli House" in str(r)
        assert "Pure Veg" in str(r)

    def test_default_ordering_by_rating(self):
        r1 = Restaurant.objects.create(name="A", address="x", city="B", rating=Decimal("3.5"))
        r2 = Restaurant.objects.create(name="B", address="x", city="B", rating=Decimal("4.8"))
        first = Restaurant.objects.all().first()
        assert first.rating >= Decimal("4.0"), "Highest-rated restaurant should come first"


@pytest.mark.django_db
class TestFoodItemModel:
    def test_veg_restaurant_rejects_non_veg_item(self):
        from django.core.exceptions import ValidationError
        r = make_restaurant("Pure Palace", "Veg")
        cat = make_category()
        with pytest.raises(ValidationError):
            FoodItem.objects.create(
                restaurant=r, category=cat,
                name="Chicken 65", price=Decimal("250"), food_type="Non-Veg"
            )

    def test_both_restaurant_allows_non_veg_item(self):
        r = make_restaurant("Empire", "Both")
        cat = make_category()
        item = make_food(r, cat, food_type="Non-Veg")
        assert item.pk is not None

    def test_price_stored_correctly(self):
        r = make_restaurant()
        cat = make_category()
        item = make_food(r, cat, price="349.50")
        assert item.price == Decimal("349.50")

    def test_str_includes_price_and_restaurant(self):
        r = make_restaurant("Savoury")
        cat = make_category()
        item = make_food(r, cat, name="Paneer Tikka", price="275.00")
        s = str(item)
        assert "Paneer Tikka" in s
        assert "275" in s
        assert "Savoury" in s


# ---------------------------------------------------------------------------
# Restaurant view tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestRestaurantViews:
    def setup_method(self):
        self.client = Client()
        self.rest = make_restaurant("Vidyarthi Bhavan", "Veg")

    def test_restaurant_list_returns_200(self):
        resp = self.client.get(reverse('restaurants:restaurant_list'))
        assert resp.status_code == 200

    def test_restaurant_list_context_has_restaurants(self):
        resp = self.client.get(reverse('restaurants:restaurant_list'))
        assert 'restaurants' in resp.context
        assert resp.context['total_count'] >= 1

    def test_restaurant_list_filter_by_type(self):
        resp = self.client.get(reverse('restaurants:restaurant_list') + '?type=Veg')
        assert resp.status_code == 200
        for r in resp.context['restaurants']:
            assert r.restaurant_type == 'Veg'

    def test_restaurant_detail_returns_200(self):
        resp = self.client.get(reverse('restaurants:restaurant_detail', args=[self.rest.pk]))
        assert resp.status_code == 200

    def test_restaurant_detail_shows_correct_name(self):
        resp = self.client.get(reverse('restaurants:restaurant_detail', args=[self.rest.pk]))
        assert b"Vidyarthi Bhavan" in resp.content

    def test_restaurant_detail_404_for_invalid_pk(self):
        resp = self.client.get(reverse('restaurants:restaurant_detail', args=[99999]))
        assert resp.status_code == 404

    def test_restaurant_detail_inactive_excluded(self):
        r_inactive = Restaurant.objects.create(
            name="Closed Shop", address="x", city="B", is_active=False
        )
        # Inactive restaurants can still be accessed by PK but won't appear in list
        resp = self.client.get(reverse('restaurants:restaurant_list'))
        names = [r.name for r in resp.context['restaurants']]
        assert "Closed Shop" not in names


# ---------------------------------------------------------------------------
# Menu view tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestMenuViews:
    def setup_method(self):
        self.client = Client()
        self.rest = make_restaurant()
        self.cat = make_category()
        self.item = make_food(self.rest, self.cat, price="199.00")

    def test_food_list_returns_200(self):
        resp = self.client.get(reverse('menu:food_list'))
        assert resp.status_code == 200

    def test_food_list_context_has_items(self):
        resp = self.client.get(reverse('menu:food_list'))
        assert 'page_obj' in resp.context
        assert resp.context['total_count'] >= 1

    def test_food_list_filter_by_veg(self):
        resp = self.client.get(reverse('menu:food_list') + '?type=Veg')
        assert resp.status_code == 200
        for item in resp.context['page_obj']:
            assert item.food_type == 'Veg'

    def test_price_always_visible_on_every_food_card(self):
        """
        Every food item in the page_obj must have a price value.
        This ensures the UI requirement (price displayed on every card) is met.
        """
        resp = self.client.get(reverse('menu:food_list'))
        for item in resp.context['page_obj']:
            assert item.price is not None
            assert item.price > 0

    def test_food_detail_returns_200(self):
        resp = self.client.get(reverse('menu:food_detail', args=[self.item.pk]))
        assert resp.status_code == 200

    def test_food_detail_shows_price(self):
        resp = self.client.get(reverse('menu:food_detail', args=[self.item.pk]))
        assert b"199" in resp.content

    def test_food_detail_404_unavailable_item(self):
        self.item.is_available = False
        self.item.save()
        resp = self.client.get(reverse('menu:food_detail', args=[self.item.pk]))
        assert resp.status_code == 404

    def test_food_list_price_range_filter(self):
        # Add cheap item
        make_food(self.rest, self.cat, name="Budget Vada", price="30.00")
        resp = self.client.get(reverse('menu:food_list') + '?price_max=50')
        assert resp.status_code == 200
        for item in resp.context['page_obj']:
            assert item.price <= 50


# ---------------------------------------------------------------------------
# Admin CRUD permission tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAdminFoodViews:
    def setup_method(self):
        self.client = Client()
        self.staff = User.objects.create_user(
            username='staffuser', email='staff@test.com',
            password='Staff@1234', is_staff=True,
            mobile_number='9000000001'
        )
        self.regular = User.objects.create_user(
            username='reguser', email='reg@test.com',
            password='Reg@12345', is_staff=False,
            mobile_number='9000000002'
        )
        self.rest = make_restaurant()
        self.cat = make_category()
        self.item = make_food(self.rest, self.cat)

    def test_food_admin_list_redirects_anonymous(self):
        resp = self.client.get(reverse('menu:admin_food_list'))
        assert resp.status_code == 302
        assert '/auth/login/' in resp['Location']

    def test_food_admin_list_redirects_non_staff(self):
        self.client.force_login(self.regular)
        resp = self.client.get(reverse('menu:admin_food_list'))
        assert resp.status_code == 302

    def test_food_admin_list_accessible_by_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse('menu:admin_food_list'))
        assert resp.status_code == 200

    def test_food_admin_create_valid(self):
        self.client.force_login(self.staff)
        cuisine = make_cuisine()
        data = {
            'restaurant': self.rest.pk,
            'category': self.cat.pk,
            'cuisine': cuisine.pk,
            'name': 'Staff Created Dosa',
            'description': 'Crispy and golden.',
            'price': '140.00',
            'food_type': 'Veg',
            'image': 'https://example.com/img.jpg',
            'is_available': True,
        }
        resp = self.client.post(reverse('menu:admin_food_create'), data, follow=True)
        assert resp.status_code == 200
        assert FoodItem.objects.filter(name='Staff Created Dosa').exists()

    def test_food_admin_delete(self):
        self.client.force_login(self.staff)
        pk = self.item.pk
        resp = self.client.post(reverse('menu:admin_food_delete', args=[pk]))
        assert resp.status_code == 302
        assert not FoodItem.objects.filter(pk=pk).exists()

    def test_food_admin_update(self):
        self.client.force_login(self.staff)
        cuisine = make_cuisine()
        data = {
            'restaurant': self.rest.pk,
            'category': self.cat.pk,
            'cuisine': cuisine.pk,
            'name': 'Updated Name',
            'description': 'Updated desc',
            'price': '299.00',
            'food_type': 'Veg',
            'image': '',
            'is_available': True,
        }
        resp = self.client.post(reverse('menu:admin_food_update', args=[self.item.pk]), data, follow=True)
        assert resp.status_code == 200
        self.item.refresh_from_db()
        assert self.item.name == 'Updated Name'
        assert self.item.price == Decimal('299.00')


# ---------------------------------------------------------------------------
# FoodItemAdminForm validation
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestFoodItemAdminForm:
    def test_form_rejects_non_veg_in_veg_restaurant(self):
        r = make_restaurant("Pure Kitchen", "Veg")
        cat = make_category()
        cuisine = make_cuisine()
        form = FoodItemAdminForm(data={
            'restaurant': r.pk,
            'category': cat.pk,
            'cuisine': cuisine.pk,
            'name': 'Butter Chicken',
            'description': 'Non-veg item',
            'price': '320.00',
            'food_type': 'Non-Veg',
            'image': '',
            'is_available': True,
        })
        assert not form.is_valid()
        assert 'Pure-Veg restaurant' in str(form.errors)

    def test_form_accepts_veg_in_veg_restaurant(self):
        r = make_restaurant("Pure Kitchen", "Veg")
        cat = make_category()
        cuisine = make_cuisine()
        form = FoodItemAdminForm(data={
            'restaurant': r.pk,
            'category': cat.pk,
            'cuisine': cuisine.pk,
            'name': 'Paneer Butter Masala',
            'description': 'Rich gravy dish',
            'price': '280.00',
            'food_type': 'Veg',
            'image': '',
            'is_available': True,
        })
        assert form.is_valid(), form.errors
