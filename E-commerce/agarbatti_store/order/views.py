from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from cart.models import CartItem  
import random
import string

from .models import Order, OrderItem

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order/order_history.html', {'orders': orders})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    delivery_fee = Decimal('5.00')
    total_with_delivery = order.total
    context = {
        'order': order,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery
    }
    return render(request, 'order/order_detail.html', context)

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    if not cart_items:
        messages.warning(request, 'Your cart is empty!')
        return redirect('cart_detail')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        cart_total = sum(Decimal(item.get_total_price()) for item in cart_items)
        delivery_fee = Decimal('5.00')
        total_with_delivery = cart_total + delivery_fee

        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            shipping_address=request.POST.get('shipping_address'),
            phone=request.POST.get('phone'),
            notes=request.POST.get('notes', ''),
            payment_method=payment_method,
            total=total_with_delivery
        )

        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )

        cart_items.delete()

        if payment_method == 'eSewa':
            # DEMO MODE: Redirect to demo payment page
            return redirect('esewa_demo', order.id)

        messages.success(request, 'Your order has been placed successfully!')
        return redirect('order_detail', order.id)

    cart_total = sum(Decimal(item.get_total_price()) for item in cart_items)
    delivery_fee = Decimal('5.00')
    total_with_delivery = cart_total + delivery_fee

    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'delivery_fee': delivery_fee,
        'total_with_delivery': total_with_delivery
    }
    return render(request, 'order/place_order.html', context)

@login_required
def esewa_demo_payment(request, order_id):
    """Show demo payment page instead of real eSewa"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'payments/esewa_demo.html', {'order': order})

@login_required
def esewa_success_demo(request, order_id):
    """Simulate successful payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Processing'
    order.is_payment_verified = True
    order.esewa_ref_id = f'DEMO-{order.id}-SUCCESS'
    order.save()
    
    messages.success(request, 'Demo payment completed successfully!')
    return render(request, 'payments/esewa_success_demo.html', {'order': order})

@login_required
def esewa_failed_demo(request, order_id):
    """Simulate failed payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    order.status = 'Cancelled'
    order.save()
    
    messages.error(request, 'Demo payment failed. Please try again.')
    return render(request, 'payments/esewa_failed_demo.html', {'order': order})

# Keep the original eSewa functions for reference (optional)
@login_required
def esewa_verify(request):
    """Original eSewa verify function - not used in demo"""
    messages.info(request, 'This would verify real eSewa payment in production.')
    return redirect('order_history')

@login_required
def esewa_failed(request):
    """Original eSewa failed function - not used in demo"""
    messages.error(request, 'Payment failed or cancelled.')
    return redirect('order_history')

@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'Pending':
        order.status = 'Cancelled'
        order.save()
        messages.success(request, 'Your order has been cancelled.')
    else:
        messages.error(request, 'This order cannot be cancelled.')
    return redirect('order_detail', order.id)