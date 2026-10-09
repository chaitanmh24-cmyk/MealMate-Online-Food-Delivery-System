"""
Search service — Phase 4.

Provides a single function `perform_search()` that:
  1. Searches FoodItem by name / description (partial, case-insensitive).
  2. Searches Restaurant by name / city (partial, case-insensitive).
  3. Applies optional filters: food_type, cuisine id, category slug, price_min/max.
  4. Persists the query to SearchHistory (for logged-in users, silently).
  5. Returns a dict with `food_items` and `restaurants` QuerySets.
"""
from django.db.models import Q
from menu.models import FoodItem, Category
from restaurants.models import Restaurant, Cuisine


def perform_search(query: str, filters: dict, user=None):
    """
    Execute a unified search across food items and restaurants.

    Args:
        query   – raw search string (can be empty / None).
        filters – dict with optional keys:
                    food_type   ('Veg' | 'Non-Veg')
                    cuisine_id  (int pk)
                    category    (category slug string)
                    price_min   (Decimal / float)
                    price_max   (Decimal / float)
        user    – request.user; if authenticated, search is stored.

    Returns:
        {
          'food_items':    QuerySet[FoodItem],
          'restaurants':   QuerySet[Restaurant],
          'query':         str,
          'filters':       dict,
        }
    """
    q = (query or '').strip()

    # ── Food Items ────────────────────────────────────────────────────────
    food_qs = FoodItem.objects.filter(is_available=True).select_related(
        'restaurant', 'category', 'cuisine'
    )

    if q:
        food_qs = food_qs.filter(
            Q(name__icontains=q) |
            Q(description__icontains=q) |
            Q(restaurant__name__icontains=q)
        )

    # Filters
    food_type = filters.get('food_type', '').strip()
    if food_type in ('Veg', 'Non-Veg'):
        food_qs = food_qs.filter(food_type=food_type)

    cuisine_id = filters.get('cuisine_id')
    if cuisine_id and str(cuisine_id).isdigit():
        food_qs = food_qs.filter(cuisine__id=int(cuisine_id))

    category_slug = filters.get('category', '').strip()
    if category_slug:
        food_qs = food_qs.filter(category__slug=category_slug)

    price_min = filters.get('price_min')
    price_max = filters.get('price_max')
    if price_min not in (None, ''):
        try:
            food_qs = food_qs.filter(price__gte=float(price_min))
        except (ValueError, TypeError):
            pass
    if price_max not in (None, ''):
        try:
            food_qs = food_qs.filter(price__lte=float(price_max))
        except (ValueError, TypeError):
            pass

    food_qs = food_qs.order_by('name').distinct()

    # ── Restaurants ───────────────────────────────────────────────────────
    rest_qs = Restaurant.objects.filter(is_active=True).prefetch_related('cuisines')

    if q:
        rest_qs = rest_qs.filter(
            Q(name__icontains=q) |
            Q(address__icontains=q) |
            Q(city__icontains=q) |
            Q(cuisines__name__icontains=q)
        )

    # If food_type filter set, surface only restaurants that *could* serve it
    if food_type == 'Veg':
        rest_qs = rest_qs.filter(restaurant_type__in=('Veg', 'Both'))
    elif food_type == 'Non-Veg':
        rest_qs = rest_qs.filter(restaurant_type__in=('Non-Veg', 'Both'))

    if cuisine_id and str(cuisine_id).isdigit():
        rest_qs = rest_qs.filter(cuisines__id=int(cuisine_id))

    rest_qs = rest_qs.order_by('-rating').distinct()

    # ── Persist search history ────────────────────────────────────────────
    if q and user and user.is_authenticated:
        _save_search(user, q, filters)

    return {
        'food_items':  food_qs,
        'restaurants': rest_qs,
        'query':       q,
        'filters':     filters,
    }


def _save_search(user, query: str, filters: dict):
    """Store last 20 unique queries; silently ignore DB errors."""
    try:
        from recommender.models import SearchHistory
        # Avoid storing identical consecutive searches
        last = (
            SearchHistory.objects
            .filter(user=user)
            .order_by('-created_at')
            .values_list('query', flat=True)
            .first()
        )
        if last and last.lower() == query.lower():
            return
        SearchHistory.objects.create(user=user, query=query, filters=filters)
        # Keep only last 20 per user
        old_ids = (
            SearchHistory.objects
            .filter(user=user)
            .order_by('-created_at')
            .values_list('id', flat=True)[20:]
        )
        if old_ids:
            SearchHistory.objects.filter(id__in=list(old_ids)).delete()
    except Exception:
        pass  # Never crash the search page due to history errors
