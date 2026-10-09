"""
Cart views — Phase 5.

  GET  /cart/                  → cart detail page (HTML)
  POST /cart/add/              → add item (JSON, fetch API)
  POST /cart/update/           → update qty (JSON, fetch API)
  POST /cart/remove/           → remove item (JSON, fetch API)
  POST /cart/clear/            → clear cart (JSON, fetch API)
"""
import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .cart_service import (
    get_or_create_cart, add_to_cart, update_cart_item,
    remove_from_cart, clear_cart, MixedRestaurantError
)
from menu.models import FoodItem


def _json_error(msg, status=400):
    return JsonResponse({'ok': False, 'error': msg}, status=status)


def _json_ok(data: dict):
    return JsonResponse({'ok': True, **data})


@login_required(login_url='/auth/login/')
def cart_detail_view(request):
    """Full cart page with item list, subtotals, and checkout button."""
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('food_item__restaurant', 'food_item__category').all()
    context = {
        'cart': cart,
        'items': items,
        'total': cart.total_amount,
        'item_count': cart.total_items_count,
    }
    return render(request, 'cart/cart_detail.html', context)


@login_required(login_url='/auth/login/')
@require_POST
def cart_add_view(request):
    """
    POST /cart/add/
    Body: { food_item_id: int, quantity: int (optional, default 1) }
    Response: { ok, cart_count, status, conflict_restaurant? }
    """
    try:
        data = json.loads(request.body)
        food_item_id = int(data.get('food_item_id', 0))
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError, json.JSONDecodeError):
        return _json_error('Invalid request data.')

    if not food_item_id:
        return _json_error('food_item_id is required.')

    try:
        result = add_to_cart(request.user, food_item_id, quantity)
        return _json_ok(result)
    except MixedRestaurantError as e:
        return JsonResponse({
            'ok': False,
            'conflict': True,
            'error': str(e),
            'current_restaurant': e.current_restaurant.name,
            'new_restaurant': e.new_restaurant.name,
        }, status=409)
    except FoodItem.DoesNotExist:
        return _json_error('Food item not found or unavailable.', 404)
    except Exception as e:
        return _json_error(str(e))


@login_required(login_url='/auth/login/')
@require_POST
def cart_update_view(request):
    """
    POST /cart/update/
    Body: { food_item_id: int, quantity: int }
    Response: { ok, removed, cart_count, subtotal }
    """
    try:
        data = json.loads(request.body)
        food_item_id = int(data['food_item_id'])
        quantity = int(data['quantity'])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return _json_error('Invalid request data.')

    result = update_cart_item(request.user, food_item_id, quantity)
    # Also return updated cart total
    cart = get_or_create_cart(request.user)
    result['cart_total'] = str(cart.total_amount)
    return _json_ok(result)


@login_required(login_url='/auth/login/')
@require_POST
def cart_remove_view(request):
    """
    POST /cart/remove/
    Body: { food_item_id: int }
    Response: { ok, cart_count, cart_total }
    """
    try:
        data = json.loads(request.body)
        food_item_id = int(data['food_item_id'])
    except (ValueError, TypeError, KeyError, json.JSONDecodeError):
        return _json_error('Invalid request data.')

    result = remove_from_cart(request.user, food_item_id)
    cart = get_or_create_cart(request.user)
    result['cart_total'] = str(cart.total_amount)
    return _json_ok(result)


@login_required(login_url='/auth/login/')
@require_POST
def cart_clear_view(request):
    """
    POST /cart/clear/
    Clears the entire cart. Returns { ok, cart_count: 0 }
    """
    clear_cart(request.user)
    return _json_ok({'cart_count': 0, 'cart_total': '0.00'})
