"""
Cart service — all business logic for cart operations.

Rules enforced here (NOT in the view):
  - One restaurant per cart. Adding an item from a different restaurant
    raises MixedRestaurantError (caller decides how to handle — usually warn
    the user and offer to clear).
  - Quantity boundaries: 1 – 20 per line item.
  - get_or_create_cart() is the single entry point used by all views.
"""
from decimal import Decimal
from django.db import transaction
from .models import Cart, CartItem
from menu.models import FoodItem


class MixedRestaurantError(Exception):
    """Raised when user tries to add items from a different restaurant."""
    def __init__(self, current_restaurant, new_restaurant):
        self.current_restaurant = current_restaurant
        self.new_restaurant = new_restaurant
        super().__init__(
            f"Cart already has items from '{current_restaurant.name}'. "
            f"Cannot add item from '{new_restaurant.name}'."
        )


def get_or_create_cart(user):
    """Return the user's Cart, creating one if it doesn't exist."""
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


def add_to_cart(user, food_item_id: int, quantity: int = 1) -> dict:
    """
    Add a food item to the user's cart.

    Returns:
        {'status': 'added'|'updated', 'cart_count': int}

    Raises:
        MixedRestaurantError if item is from a different restaurant.
        ValueError for invalid quantity or unavailable item.
    """
    quantity = max(1, min(int(quantity), 20))

    item = FoodItem.objects.select_related('restaurant').get(pk=food_item_id, is_available=True)

    with transaction.atomic():
        cart = get_or_create_cart(user)

        # Enforce single-restaurant rule
        if cart.restaurant_id and cart.restaurant_id != item.restaurant_id:
            raise MixedRestaurantError(cart.restaurant, item.restaurant)

        # Set cart restaurant if not yet set
        if not cart.restaurant_id:
            cart.restaurant = item.restaurant
            cart.save(update_fields=['restaurant', 'updated_at'])

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, food_item=item,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity = min(cart_item.quantity + quantity, 20)
            cart_item.save(update_fields=['quantity', 'updated_at'])

    return {
        'status': 'added' if created else 'updated',
        'cart_count': cart.total_items_count,
    }


def update_cart_item(user, food_item_id: int, quantity: int) -> dict:
    """
    Set a cart item to an exact quantity. If quantity <= 0 removes it.
    Returns {'removed': bool, 'cart_count': int, 'subtotal': str}
    """
    cart = get_or_create_cart(user)
    try:
        cart_item = CartItem.objects.select_related('food_item').get(
            cart=cart, food_item_id=food_item_id
        )
    except CartItem.DoesNotExist:
        return {'removed': True, 'cart_count': cart.total_items_count, 'subtotal': '0.00'}

    if quantity <= 0:
        cart_item.delete()
        _maybe_clear_restaurant(cart)
        return {'removed': True, 'cart_count': cart.total_items_count, 'subtotal': '0.00'}

    cart_item.quantity = min(int(quantity), 20)
    cart_item.save(update_fields=['quantity', 'updated_at'])
    return {
        'removed': False,
        'cart_count': cart.total_items_count,
        'subtotal': str(cart_item.subtotal),
    }


def remove_from_cart(user, food_item_id: int) -> dict:
    """Remove a specific item from the cart entirely."""
    cart = get_or_create_cart(user)
    CartItem.objects.filter(cart=cart, food_item_id=food_item_id).delete()
    _maybe_clear_restaurant(cart)
    return {'cart_count': cart.total_items_count}


def clear_cart(user):
    """Wipe all items and reset the restaurant FK."""
    cart = get_or_create_cart(user)
    cart.clear()


def _maybe_clear_restaurant(cart: Cart):
    """If the cart is now empty, unlink the restaurant FK."""
    if not cart.items.exists():
        cart.restaurant = None
        cart.save(update_fields=['restaurant', 'updated_at'])
