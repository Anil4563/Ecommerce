from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal
from product.models import Product
from .models import CartItem

DELIVERY_FEE = Decimal('5.00')  # fixed delivery fee

@login_required
def cart_detail(request):
    cart_items = CartItem.objects.filter(user=request.user)
    
    cart_total = sum(item.get_total_price() for item in cart_items) or Decimal('0.00')
    tax = cart_total * Decimal('0.05')  # Example: 5% tax
    grand_total = cart_total + tax + DELIVERY_FEE
    
    context = {
        'cart_items': cart_items,
        'cart_total': cart_total,
        'tax': tax,
        'delivery_fee': DELIVERY_FEE,
        'grand_total': grand_total,
    }
    return render(request, 'cart/cart_detail.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    
    cart_item, created = CartItem.objects.get_or_create(
        user=request.user,
        product=product,
        defaults={'quantity': quantity}
    )
    
    if not created:
        cart_item.quantity += quantity
        cart_item.save()
    
    messages.success(request, f'{product.name} added to your cart!')
    return redirect('cart_detail')

@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated successfully!')
        else:
            cart_item.delete()
            messages.success(request, 'Item removed from cart.')
    
    return redirect('cart_detail')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart_detail')
