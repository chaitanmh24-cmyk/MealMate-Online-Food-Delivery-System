from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, F, Q
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

from restaurants.models import Restaurant
from menu.models import FoodItem, Category
from orders.models import Order, OrderItem, Payment
from cart.cart_service import get_or_create_cart
from recommender.models import SearchHistory

from recommender.engine import get_recommendations

User = get_user_model()


def home_view(request):
    """
    Homepage: hero section, top-rated restaurants, category tabs,
    recommended for you section, and a featured food grid.
    """
    top_restaurants = Restaurant.objects.filter(is_active=True).prefetch_related('cuisines').order_by('-rating')[:8]
    categories      = Category.objects.all().order_by('name')

    # Selected category tab
    selected_cat_slug = request.GET.get('category', '').strip()

    featured_items = FoodItem.objects.filter(is_available=True).select_related(
        'restaurant', 'category', 'cuisine'
    )
    if selected_cat_slug:
        featured_items = featured_items.filter(category__slug=selected_cat_slug)

    featured_items = featured_items.order_by('?')[:8]

    # Personalized or Popular Recommendations
    user = request.user if request.user.is_authenticated else None
    recommendations = get_recommendations(user=user, limit=8)

    context = {
        'top_restaurants':    top_restaurants,
        'categories':         categories,
        'featured_items':     featured_items,
        'selected_cat':       selected_cat_slug,
        'recommendations':    recommendations,
    }
    return render(request, 'home.html', context)


@login_required(login_url='/auth/login/')
def user_dashboard_view(request):
    """
    Customer Dashboard: Account details, order statistics, active orders,
    current cart snapshot, personalized recommendations, and order history.
    """
    user = request.user
    user_orders = (
        Order.objects.filter(user=user)
        .select_related('restaurant', 'payment')
        .prefetch_related('items')
        .order_by('-created_at')
    )

    total_orders = user_orders.count()
    
    # Calculate total spent on successful orders
    total_spent_val = (
        user_orders.filter(payment__status='Success')
        .aggregate(total=Sum('total_amount'))['total']
    ) or Decimal('0.00')

    active_orders = user_orders.filter(status__in=['Placed', 'Preparing', 'Out for Delivery'])
    recent_orders = user_orders[:5]

    cart = get_or_create_cart(user)
    cart_items = cart.items.select_related('food_item').all()

    recent_searches = SearchHistory.objects.filter(user=user).order_by('-created_at')[:6]

    # Personalized Recommendations for user dashboard
    recommendations = get_recommendations(user=user, limit=6)

    context = {
        'user': user,
        'total_orders': total_orders,
        'total_spent': total_spent_val,
        'active_orders': active_orders,
        'recent_orders': recent_orders,
        'cart': cart,
        'cart_items': cart_items,
        'recent_searches': recent_searches,
        'recommendations': recommendations,
    }
    return render(request, 'dashboard/user_dashboard.html', context)


def _is_staff_user(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(_is_staff_user, login_url='/auth/login/')
def admin_dashboard_view(request):
    """
    Staff / Admin Dashboard:
    - High-level business KPIs: Total Revenue, Total Orders, Active Orders, Registered Users.
    - Top-selling food items with quantity sold and revenue generated.
    - Recent orders management table with inline status update actions.
    """
    # 1. KPIs
    total_orders = Order.objects.count()
    
    total_revenue_val = (
        Order.objects.filter(payment__status='Success')
        .aggregate(total=Sum('total_amount'))['total']
    ) or Decimal('0.00')

    active_orders_count = Order.objects.filter(
        status__in=['Placed', 'Preparing', 'Out for Delivery']
    ).count()

    total_users_count = User.objects.filter(is_staff=False).count()
    total_restaurants_count = Restaurant.objects.count()
    total_food_count = FoodItem.objects.count()

    # 2. Top-Selling Dishes (aggregated by quantity and revenue)
    top_selling = (
        OrderItem.objects.values('food_name')
        .annotate(
            total_qty=Sum('quantity'),
            total_rev=Sum(F('price') * F('quantity'))
        )
        .order_by('-total_qty')[:6]
    )

    # 3. Orders Management Table with filtering
    status_filter = request.GET.get('status', '').strip()
    orders_qs = (
        Order.objects.select_related('user', 'restaurant', 'payment')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    if status_filter in dict(Order.STATUS_CHOICES):
        orders_qs = orders_qs.filter(status=status_filter)

    paginator = Paginator(orders_qs, 15)
    page_number = request.GET.get('page')
    orders_page = paginator.get_page(page_number)

    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue_val,
        'active_orders_count': active_orders_count,
        'total_users': total_users_count,
        'total_restaurants': total_restaurants_count,
        'total_food_items': total_food_count,
        'top_selling': top_selling,
        'orders_page': orders_page,
        'status_choices': Order.STATUS_CHOICES,
        'selected_status': status_filter,
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@user_passes_test(_is_staff_user, login_url='/auth/login/')
def admin_update_order_status(request, pk):
    """
    Staff / Admin: Update status of any order (e.g. from Placed -> Preparing -> Out for Delivery -> Delivered).
    """
    if request.method != 'POST':
        return redirect('dashboard:admin_dashboard')

    order = get_object_or_404(Order, pk=pk)
    new_status = request.POST.get('status', '').strip()

    valid_statuses = [s[0] for s in Order.STATUS_CHOICES]
    if new_status in valid_statuses:
        old_status = order.status
        order.status = new_status
        order.save(update_fields=['status', 'updated_at'])
        messages.success(
            request,
            f"✅ Order #{order.order_number} status updated from '{old_status}' to '{new_status}'."
        )
    else:
        messages.error(request, "Invalid order status value.")

    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/dashboard/admin/'
    return redirect(next_url)
