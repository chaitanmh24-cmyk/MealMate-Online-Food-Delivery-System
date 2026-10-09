"""
Orders views — Phase 5.

  GET  /orders/checkout/              → Checkout form (address, contact)
  POST /orders/checkout/              → place_order → redirect to payment page
  GET  /orders/<pk>/payment/          → Razorpay payment page
  POST /orders/payment/verify/        → Razorpay success callback
  POST /orders/payment/fail/          → Razorpay failure callback
  GET  /orders/<pk>/success/          → Order success page
  GET  /orders/                       → User's order history list
  GET  /orders/<pk>/                  → Order detail
  POST /orders/<pk>/cancel/           → Cancel order (only if 'Placed')
"""
import json
import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse, Http404

from .models import Order, Payment
from .order_service import place_order, verify_payment, fail_payment, cancel_order

logger = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _owned_order(request, pk):
    """Return Order only if it belongs to request.user, else 404."""
    return get_object_or_404(Order.objects.select_related('restaurant', 'payment'), pk=pk, user=request.user)


# ── Checkout ─────────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def checkout_view(request):
    from cart.cart_service import get_or_create_cart
    cart = get_or_create_cart(request.user)
    items = cart.items.select_related('food_item').all()

    if not items.exists():
        messages.warning(request, 'Your cart is empty. Add some items first!')
        return redirect('cart:cart_detail')

    if request.method == 'POST':
        delivery_address = request.POST.get('delivery_address', '').strip()
        delivery_city    = request.POST.get('delivery_city', 'Bengaluru').strip()
        contact_number   = request.POST.get('contact_number', '').strip()

        errors = {}
        if not delivery_address:
            errors['delivery_address'] = 'Delivery address is required.'
        if not contact_number or not contact_number.isdigit() or len(contact_number) < 10:
            errors['contact_number'] = 'Enter a valid 10-digit mobile number.'

        if errors:
            return render(request, 'orders/checkout.html', {
                'cart': cart, 'items': items, 'total': cart.total_amount,
                'errors': errors,
                'delivery_address': delivery_address,
                'delivery_city': delivery_city,
                'contact_number': contact_number,
            })

        try:
            result = place_order(
                user=request.user,
                delivery_address=delivery_address,
                delivery_city=delivery_city,
                contact_number=contact_number,
            )
            return redirect('orders:payment_page', pk=result['order'].pk)
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart:cart_detail')

    # Pre-fill address from profile if available
    user = request.user
    prefill_address = getattr(user, 'address', '') or ''
    prefill_city    = getattr(user, 'city', 'Bengaluru') or 'Bengaluru'
    prefill_mobile  = getattr(user, 'mobile_number', '') or ''

    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'items': items,
        'total': cart.total_amount,
        'delivery_address': prefill_address,
        'delivery_city': prefill_city,
        'contact_number': prefill_mobile,
        'errors': {},
    })


# ── Razorpay Payment Page ─────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def payment_page_view(request, pk):
    order   = _owned_order(request, pk)
    payment = get_object_or_404(Payment, order=order)

    if payment.status == 'Success':
        return redirect('orders:order_success', pk=order.pk)

    order_items = order.items.select_related('food_item').all()

    from django.conf import settings
    context = {
        'order':              order,
        'payment':            payment,
        'order_items':        order_items,
        'razorpay_key':       settings.RAZORPAY_KEY_ID,
        'razorpay_order_id':  payment.razorpay_order_id,
        'amount_paise':       int(payment.amount * 100),
        'user_name':          request.user.get_full_name() or request.user.username,
        'user_email':         request.user.email,
        'user_mobile':        getattr(request.user, 'mobile_number', '') or '',
    }
    return render(request, 'orders/payment.html', context)


# ── Razorpay Callbacks ────────────────────────────────────────────────────────

@csrf_exempt
@require_POST
def payment_verify_view(request):
    """Called by Razorpay JS SDK after successful payment."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    rz_order_id   = data.get('razorpay_order_id', '')
    rz_payment_id = data.get('razorpay_payment_id', '')
    rz_signature  = data.get('razorpay_signature', '')

    try:
        payment = verify_payment(rz_order_id, rz_payment_id, rz_signature)
        # AJAX call → return JSON; fallback for form POST → redirect
        if request.content_type == 'application/json':
            return JsonResponse({'ok': True, 'order_id': payment.order.pk})
        messages.success(request, f'🎉 Payment successful! Order #{payment.order.order_number} is being prepared.')
        return redirect('orders:order_success', pk=payment.order.pk)
    except (Payment.DoesNotExist, ValueError) as exc:
        logger.error("Payment verify error: %s", exc)
        if request.content_type == 'application/json':
            return JsonResponse({'ok': False, 'error': str(exc)}, status=400)
        messages.error(request, f'Payment verification failed: {exc}')
        return redirect('orders:order_list')


@csrf_exempt
@require_POST
def payment_fail_view(request):
    """Called by Razorpay JS SDK after payment failure / dismiss."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        data = request.POST

    rz_order_id = data.get('razorpay_order_id', '')
    if rz_order_id:
        fail_payment(rz_order_id, reason='User dismissed or payment failed')

    if request.content_type == 'application/json':
        return JsonResponse({'ok': True})
    messages.warning(request, 'Payment was not completed. Your order is still saved — you can retry or cancel.')
    return redirect('orders:order_list')


# ── Order Success ─────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def order_success_view(request, pk):
    order       = _owned_order(request, pk)
    order_items = order.items.select_related('food_item').all()
    return render(request, 'orders/order_success.html', {'order': order, 'order_items': order_items})


# ── Order List ────────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def order_list_view(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .select_related('restaurant', 'payment')
        .prefetch_related('items')
        .order_by('-created_at')
    )
    return render(request, 'orders/order_list.html', {'orders': orders})


# ── Order Detail ──────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
def order_detail_view(request, pk):
    order       = _owned_order(request, pk)
    order_items = order.items.select_related('food_item').all()
    return render(request, 'orders/order_detail.html', {'order': order, 'order_items': order_items})


# ── Cancel Order ──────────────────────────────────────────────────────────────

@login_required(login_url='/auth/login/')
@require_POST
def cancel_order_view(request, pk):
    order = _owned_order(request, pk)
    try:
        cancel_order(order, request.user)
        messages.success(request, f'Order #{order.order_number} has been cancelled successfully.')
    except (PermissionError, ValueError) as exc:
        messages.error(request, str(exc))
    return redirect('orders:order_detail', pk=order.pk)
