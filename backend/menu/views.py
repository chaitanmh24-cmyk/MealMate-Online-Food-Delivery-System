from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import FoodItem, Category
from .forms import FoodItemAdminForm
from .search_service import perform_search
from restaurants.models import Cuisine, Restaurant

# ---------------------------------------------------------------------------
# Public Views
# ---------------------------------------------------------------------------

def food_list_view(request):
    """
    Public view: Browse all available food items with filters.
    Filters: category (slug), food_type (Veg/Non-Veg), cuisine,
             price_min, price_max.
    """
    category_slug = request.GET.get('category', '').strip()
    food_type     = request.GET.get('type', '').strip()
    cuisine_id    = request.GET.get('cuisine', '').strip()
    price_min     = request.GET.get('price_min', '').strip()
    price_max     = request.GET.get('price_max', '').strip()
    sort_by       = request.GET.get('sort', 'name').strip()

    items = FoodItem.objects.filter(is_available=True).select_related(
        'restaurant', 'category', 'cuisine'
    )

    if category_slug:
        items = items.filter(category__slug=category_slug)

    if food_type in ['Veg', 'Non-Veg']:
        items = items.filter(food_type=food_type)

    if cuisine_id and cuisine_id.isdigit():
        items = items.filter(cuisine__id=cuisine_id)

    if price_min.replace('.', '', 1).isdigit():
        items = items.filter(price__gte=float(price_min))

    if price_max.replace('.', '', 1).isdigit():
        items = items.filter(price__lte=float(price_max))

    valid_sorts = {'name': 'name', '-name': '-name', 'price': 'price', '-price': '-price'}
    items = items.order_by(valid_sorts.get(sort_by, 'name'))

    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj':         page_obj,
        'categories':       Category.objects.all().order_by('name'),
        'cuisines':         Cuisine.objects.all().order_by('name'),
        'selected_cat':     category_slug,
        'selected_type':    food_type,
        'selected_cuisine': int(cuisine_id) if cuisine_id.isdigit() else None,
        'selected_sort':    sort_by,
        'price_min':        price_min,
        'price_max':        price_max,
        'total_count':      items.count(),
    }
    return render(request, 'menu/food_list.html', context)


def food_detail_view(request, pk):
    """
    Public view: Detail page for a single food item with suggested picks.
    """
    item = get_object_or_404(
        FoodItem.objects.select_related('restaurant', 'category', 'cuisine'),
        pk=pk, is_available=True
    )
    related_items = FoodItem.objects.filter(
        restaurant=item.restaurant, is_available=True
    ).exclude(pk=pk)[:6]

    context = {
        'item':          item,
        'related_items': related_items,
    }
    return render(request, 'menu/food_detail.html', context)


def search_view(request):
    """
    Unified search: single query box searches both food items and restaurants.
    Supports filters: food_type, cuisine, category, price_min, price_max.
    Stores query in SearchHistory for logged-in users.
    """
    query      = request.GET.get('q', '').strip()
    food_type  = request.GET.get('type', '').strip()
    cuisine_id = request.GET.get('cuisine', '').strip()
    category   = request.GET.get('category', '').strip()
    price_min  = request.GET.get('price_min', '').strip()
    price_max  = request.GET.get('price_max', '').strip()

    filters = {
        'food_type':   food_type,
        'cuisine_id':  cuisine_id,
        'category':    category,
        'price_min':   price_min,
        'price_max':   price_max,
    }

    results = perform_search(query, filters, user=request.user)

    # Paginate food items (12 per page)
    food_paginator = Paginator(results['food_items'], 12)
    food_page_obj  = food_paginator.get_page(request.GET.get('page'))

    context = {
        'query':           query,
        'food_page_obj':   food_page_obj,
        'restaurants':     results['restaurants'][:8],   # cap at 8 for the sidebar
        'total_food':      results['food_items'].count(),
        'total_rest':      results['restaurants'].count(),
        'categories':      Category.objects.all().order_by('name'),
        'cuisines':        Cuisine.objects.all().order_by('name'),
        'selected_type':   food_type,
        'selected_cuisine': int(cuisine_id) if cuisine_id.isdigit() else None,
        'selected_cat':    category,
        'price_min':       price_min,
        'price_max':       price_max,
    }
    return render(request, 'menu/search_results.html', context)


# ---------------------------------------------------------------------------
# Admin (Staff-Only) CRUD Views for Food Items
# ---------------------------------------------------------------------------

def _is_staff(user):
    return user.is_active and user.is_staff


@user_passes_test(_is_staff, login_url='/auth/login/')
def admin_food_list_view(request):
    """Staff only: list all food items with search."""
    q = request.GET.get('q', '').strip()
    items = FoodItem.objects.select_related('restaurant', 'category', 'cuisine').order_by('-created_at')
    if q:
        items = items.filter(Q(name__icontains=q) | Q(restaurant__name__icontains=q))
    paginator = Paginator(items, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'menu/admin/food_list.html', {'page_obj': page_obj, 'q': q})


@user_passes_test(_is_staff, login_url='/auth/login/')
def admin_food_create_view(request):
    """Staff only: create a new food item."""
    if request.method == 'POST':
        form = FoodItemAdminForm(request.POST)
        if form.is_valid():
            item = form.save()
            messages.success(request, f'✅ "{item.name}" added to the menu successfully!')
            return redirect('menu:admin_food_list')
    else:
        form = FoodItemAdminForm()
    return render(request, 'menu/admin/food_form.html', {'form': form, 'action': 'Add New Food Item'})


@user_passes_test(_is_staff, login_url='/auth/login/')
def admin_food_update_view(request, pk):
    """Staff only: edit an existing food item."""
    item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        form = FoodItemAdminForm(request.POST, instance=item)
        if form.is_valid():
            updated = form.save()
            messages.success(request, f'✅ "{updated.name}" updated successfully!')
            return redirect('menu:admin_food_list')
    else:
        form = FoodItemAdminForm(instance=item)
    return render(request, 'menu/admin/food_form.html', {'form': form, 'action': f'Edit: {item.name}', 'item': item})


@user_passes_test(_is_staff, login_url='/auth/login/')
def admin_food_delete_view(request, pk):
    """Staff only: confirm and delete a food item."""
    item = get_object_or_404(FoodItem, pk=pk)
    if request.method == 'POST':
        name = item.name
        item.delete()
        messages.success(request, f'🗑️ "{name}" removed from the menu.')
        return redirect('menu:admin_food_list')
    return render(request, 'menu/admin/food_confirm_delete.html', {'item': item})
