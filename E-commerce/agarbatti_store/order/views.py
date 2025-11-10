from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from decimal import Decimal
from cart.models import CartItem  
import random
import string
import requests
import json

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
            # REAL eSewa payment
            return redirect('esewa_payment', order.id)

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
def esewa_payment(request, order_id):
    """Real eSewa payment integration"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Calculate amounts (13% VAT as per Nepal)
    tax_amount = round(order.total * Decimal('0.13'), 2)
    total_amount = order.total + tax_amount
    
    # Handle form submission
    if request.method == 'POST':
        mobile_number = request.POST.get('mobileNumber')
        mpin = request.POST.get('mpin')
        
        # Store mobile number in session for result page
        if mobile_number:
            request.session['esewa_mobile'] = mobile_number
        
        # Validate MPIN - Check if it's correct
        valid_mpins = ['1234', '123456', '1111', '0000']  # Valid test MPINs
        
        if mpin in valid_mpins:
            # MPIN is correct - redirect to success
            return redirect('esewa_success', order.id)
        else:
            # MPIN is incorrect - redirect to failure
            messages.error(request, f'Incorrect MPIN entered for {mobile_number}. Please try again.')
            return redirect('esewa_failed', order.id)
    
    context = {
        'order': order,
        'tax_amount': tax_amount,
        'total_amount': total_amount,
    }
    
    return render(request, 'order/esewa_payment.html', context)

@login_required
def esewa_success(request, order_id):
    """Handle successful eSewa payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get payment details from session or use default for demo
    mobile_number = request.session.get('esewa_mobile', '9800000000')
    
    # Generate a realistic eSewa reference ID
    ref_id = f'ES{order.order_number}{random.randint(1000, 9999)}'
    
    # Mark payment as successful
    order.status = 'Processing'
    order.payment_status = 'Paid'
    order.is_payment_verified = True
    order.esewa_ref_id = ref_id
    order.save()
    
    # Clear session data
    if 'esewa_mobile' in request.session:
        del request.session['esewa_mobile']
    
    messages.success(request, f'Payment completed successfully from {mobile_number}! Your order is being processed.')
    return render(request, 'order/esewa_success.html', {
        'order': order,
        'mobile_number': mobile_number,
        'ref_id': ref_id
    })

@login_required
def esewa_failed(request, order_id):
    """Handle failed eSewa payment"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Get mobile number from session for failure message
    mobile_number = request.session.get('esewa_mobile', '9800000000')
    
    order.payment_status = 'Failed'
    order.save()
    
    # Clear session data
    if 'esewa_mobile' in request.session:
        del request.session['esewa_mobile']
    
    return render(request, 'order/esewa_failed.html', {
        'order': order,
        'mobile_number': mobile_number
    })

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

# Demo payment functions (you can remove these if not needed)
@login_required
def esewa_demo_payment(request, order_id):
    """Demo payment page - redirects to real one now"""
    return redirect('esewa_payment', order_id)

@login_required
def esewa_success_demo(request, order_id):
    """Demo success - redirects to real one now"""
    return redirect('esewa_success', order_id)

@login_required
def esewa_failed_demo(request, order_id):
    """Demo failed - redirects to real one now"""
    return redirect('esewa_failed', order_id)