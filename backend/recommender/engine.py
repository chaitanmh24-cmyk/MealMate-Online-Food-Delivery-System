"""
Hybrid Food Recommendation Engine — Phase 7.

Architecture:
  1. Signals Gathering:
     - Orders: Last 10 orders with recency decay (weight: 3.0)
     - Cart: Current active cart items (weight: 2.0)
     - Searches: Recent SearchHistory queries & filters (weight: 1.0)
  2. Strict Business Rules:
     - Strict Veg Preference: A user who has only ordered veg must NEVER be shown non-veg.
     - Cart Exclusion: Items currently in the user's cart are excluded.
     - Availability: Exclude unavailable food items and inactive restaurants.
  3. Content-Based TF-IDF Model:
     - Vectorizes cuisine, category, food_type, restaurant, price band, and description.
     - Computes cosine similarity between user preference vector and candidate food items.
  4. Popularity Fallback (Cold Start):
     - For anonymous users or users with zero historical signals, recommends
       highest-rated and most ordered dishes.
"""

from decimal import Decimal
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Count, Sum

from menu.models import FoodItem
from orders.models import Order, OrderItem
from cart.models import Cart
from recommender.models import SearchHistory


def _get_price_band(price: Decimal) -> str:
    """Categorize item price into distinct bands for TF-IDF feature tokens."""
    if price <= 150:
        return "price_budget under_150"
    elif price <= 350:
        return "price_midrange 150_to_350"
    else:
        return "price_premium above_350"


def _build_food_document(food: FoodItem) -> str:
    """
    Construct rich text token document for a food item.
    Includes item name, cuisine, category, food type, restaurant name, and price band.
    """
    cuisine_name = food.cuisine.name if food.cuisine else ""
    category_name = food.category.name if food.category else ""
    restaurant_name = food.restaurant.name if food.restaurant else ""
    price_band = _get_price_band(food.price)
    
    # Weight key categorical attributes by repetition in the text document
    tokens = [
        food.name, food.name,
        food.food_type, food.food_type,
        cuisine_name, cuisine_name,
        category_name,
        restaurant_name,
        price_band,
        food.description or ""
    ]
    return " ".join(tokens)


def get_popularity_recommendations(is_pure_veg: bool = False, exclude_ids: set = None, limit: int = 8):
    """
    Cold-start fallback: Recommend highest-rated partner kitchen dishes
    ordered most frequently across the platform.
    """
    exclude_ids = exclude_ids or set()
    qs = (
        FoodItem.objects.filter(is_available=True, restaurant__is_active=True)
        .exclude(id__in=exclude_ids)
        .select_related('restaurant', 'category', 'cuisine')
    )
    if is_pure_veg:
        qs = qs.filter(food_type='Veg')

    # Order by restaurant rating descending and order volume
    qs = qs.annotate(order_count=Count('order_items')).order_by(
        '-restaurant__rating', '-order_count', '?'
    )
    return list(qs[:limit])


def get_recommendations(user=None, limit=8):
    """
    Primary recommendation API:
    Returns a list of FoodItem objects recommended specifically for the user.
    """
    available_items_qs = FoodItem.objects.filter(
        is_available=True,
        restaurant__is_active=True
    ).select_related('restaurant', 'category', 'cuisine')

    if not available_items_qs.exists():
        return []

    # Fast path for anonymous or non-authenticated users
    if user is None or not getattr(user, 'is_authenticated', False):
        return get_popularity_recommendations(is_pure_veg=False, limit=limit)

    # 1. Inspect Cart (Items to exclude and cart signals)
    cart_item_ids = set()
    cart_food_docs = []
    try:
        if hasattr(user, 'cart'):
            cart_items = list(user.cart.items.select_related('food_item__cuisine', 'food_item__category', 'food_item__restaurant').all())
            for ci in cart_items:
                cart_item_ids.add(ci.food_item_id)
                cart_food_docs.append(_build_food_document(ci.food_item))
    except Exception:
        pass

    # 2. Gather User's Past Orders (up to last 10)
    user_orders = list(
        Order.objects.filter(user=user)
        .prefetch_related('items__food_item__cuisine', 'items__food_item__category', 'items__food_item__restaurant')
        .order_by('-created_at')[:10]
    )

    ordered_food_types = set()
    order_signals = []  # list of tuples: (document_str, weight)

    for order_idx, order in enumerate(user_orders):
        # Recency decay: most recent order gets decay 1.0, 10th order gets 0.4
        decay = max(0.4, 1.0 - (order_idx * 0.06))
        for item in order.items.all():
            ordered_food_types.add(item.food_item.food_type)
            doc = _build_food_document(item.food_item)
            order_signals.append((doc, 3.0 * decay))

    # Strict Veg Preference Detection:
    # If the user has order history and has ONLY ordered Veg, or cart only has Veg:
    is_pure_veg_user = False
    if ordered_food_types and ordered_food_types == {'Veg'}:
        is_pure_veg_user = True

    # 3. Gather Recent Searches
    recent_searches = list(
        SearchHistory.objects.filter(user=user)
        .order_by('-created_at')[:8]
    )
    search_signals = []
    for s_idx, s in enumerate(recent_searches):
        decay = max(0.4, 1.0 - (s_idx * 0.07))
        search_query_text = s.query
        if s.filters and isinstance(s.filters, dict):
            if s.filters.get('food_type') == 'Veg':
                search_query_text += " Veg Pure-Veg"
            if s.filters.get('category'):
                search_query_text += f" {s.filters.get('category')}"
        search_signals.append((search_query_text, 1.0 * decay))

    # Cold Start Check: If user has no orders, no cart items, and no searches
    has_signals = bool(order_signals or cart_food_docs or search_signals)
    if not has_signals:
        return get_popularity_recommendations(
            is_pure_veg=is_pure_veg_user,
            exclude_ids=cart_item_ids,
            limit=limit
        )

    # 4. Filter candidate items (Exclude cart items & apply Pure-Veg rule)
    candidates_qs = available_items_qs.exclude(id__in=cart_item_ids)
    if is_pure_veg_user:
        candidates_qs = candidates_qs.filter(food_type='Veg')

    candidates = list(candidates_qs)
    if not candidates:
        return []

    # 5. Build Content TF-IDF Space
    candidate_docs = [_build_food_document(item) for item in candidates]

    # Assemble user query tokens with weights
    user_tokens = []
    # Order signals (weight 3.0)
    for doc, w in order_signals:
        user_tokens.append(doc * int(round(w)))
    # Cart signals (weight 2.0)
    for doc in cart_food_docs:
        user_tokens.append(doc * 2)
    # Search signals (weight 1.0)
    for doc, w in search_signals:
        user_tokens.append(doc * int(round(w)))

    user_profile_doc = " ".join(user_tokens).strip()

    if not user_profile_doc:
        return get_popularity_recommendations(is_pure_veg=is_pure_veg_user, exclude_ids=cart_item_ids, limit=limit)

    try:
        vectorizer = TfidfVectorizer(stop_words='english', max_features=1500)
        tfidf_matrix = vectorizer.fit_transform(candidate_docs)
        user_vector = vectorizer.transform([user_profile_doc])

        # Compute cosine similarity
        similarities = cosine_similarity(user_vector, tfidf_matrix).flatten()

        # Rank candidates by cosine similarity descending
        top_indices = np.argsort(similarities)[::-1]

        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0.01:
                recommendations.append(candidates[idx])
            if len(recommendations) >= limit:
                break

        # If similarity returned fewer than limit, backfill with popularity
        if len(recommendations) < limit:
            existing_ids = cart_item_ids.union({item.id for item in recommendations})
            backfill = get_popularity_recommendations(
                is_pure_veg=is_pure_veg_user,
                exclude_ids=existing_ids,
                limit=limit - len(recommendations)
            )
            recommendations.extend(backfill)

        return recommendations[:limit]

    except Exception:
        # Fallback to popularity safely on any mathematical/vectorizer error
        return get_popularity_recommendations(
            is_pure_veg=is_pure_veg_user,
            exclude_ids=cart_item_ids,
            limit=limit
        )
