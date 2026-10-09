from django.shortcuts import render, get_object_or_404
from django.db.models import Count
from .models import Restaurant, Cuisine
from menu.models import FoodItem, Category

def restaurant_list_view(request):
    """
    List all active restaurants with filtering by type (Veg, Non-Veg, Both),
    cuisine, and city.
    """
    restaurant_type = request.GET.get('type', '').strip()
    cuisine_id = request.GET.get('cuisine', '').strip()
    city = request.GET.get('city', '').strip()
    sort_by = request.GET.get('sort', '-rating').strip()

    restaurants = Restaurant.objects.filter(is_active=True).prefetch_related('cuisines')

    if restaurant_type in ['Veg', 'Non-Veg', 'Both']:
        restaurants = restaurants.filter(restaurant_type=restaurant_type)

    if cuisine_id and cuisine_id.isdigit():
        restaurants = restaurants.filter(cuisines__id=cuisine_id)

    if city:
        restaurants = restaurants.filter(city__iexact=city)

    # Sorting options
    valid_sorts = ['-rating', 'rating', 'name', '-name']
    if sort_by in valid_sorts:
        restaurants = restaurants.order_by(sort_by)
    else:
        restaurants = restaurants.order_by('-rating')

    # Distinct in case of many-to-many joins
    restaurants = restaurants.distinct()

    all_cuisines = Cuisine.objects.all().order_by('name')
    cities = Restaurant.objects.values_list('city', flat=True).distinct().order_by('city')

    context = {
        'restaurants': restaurants,
        'cuisines': all_cuisines,
        'cities': cities,
        'selected_type': restaurant_type,
        'selected_cuisine': int(cuisine_id) if cuisine_id.isdigit() else None,
        'selected_city': city,
        'selected_sort': sort_by,
        'total_count': restaurants.count(),
    }
    return render(request, 'restaurants/restaurant_list.html', context)


def restaurant_detail_view(request, pk):
    """
    Detailed restaurant view showing banner, cuisines, info,
    and all available food items grouped by categories.
    """
    restaurant = get_object_or_404(Restaurant.objects.prefetch_related('cuisines'), pk=pk)
    
    # Filter menu items
    food_items = restaurant.food_items.filter(is_available=True).select_related('category', 'cuisine').order_by('category__name', 'name')

    # Category filter if selected
    selected_cat_slug = request.GET.get('category', '').strip()
    selected_type = request.GET.get('type', '').strip()

    if selected_cat_slug:
        food_items = food_items.filter(category__slug=selected_cat_slug)
    if selected_type in ['Veg', 'Non-Veg']:
        food_items = food_items.filter(food_type=selected_type)

    # Group food items by category for structured menu display
    categories = Category.objects.filter(food_items__restaurant=restaurant).distinct()

    context = {
        'restaurant': restaurant,
        'food_items': food_items,
        'categories': categories,
        'selected_category': selected_cat_slug,
        'selected_type': selected_type,
        'total_items': food_items.count(),
    }
    return render(request, 'restaurants/restaurant_detail.html', context)
