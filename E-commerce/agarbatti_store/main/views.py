from django.shortcuts import render
from django.views.generic import TemplateView
from product.models import Product, Category
from order.models import OrderItem
from .forms import ContactForm

class HomeView(TemplateView):
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Show 3 featured categories (Dhoop, Agarbatti, Cones, etc.)
        context['featured_categories'] = Category.objects.all()[:3]

        # Fetch all available products
        available_products = Product.objects.filter(is_available=True)

        # Fetch all OrderItems related to available products
        order_items = OrderItem.objects.filter(product__in=available_products)

        # Count frequency of each product (popularity)
        frequency = {}
        for product_id in order_items.values_list('product_id', flat=True):
            frequency[product_id] = frequency.get(product_id, 0) + 1

        # Sort by frequency (popular first)
        sorted_product_ids = sorted(frequency, key=frequency.get, reverse=True)

        # Exclude products user already ordered
        user = self.request.user
        if user.is_authenticated:
            user_ordered_product_ids = set(
                OrderItem.objects.filter(order__user=user).values_list('product_id', flat=True)
            )
            sorted_product_ids = [pid for pid in sorted_product_ids if pid not in user_ordered_product_ids]

        # Map IDs to Product objects
        id_to_product = {product.id: product for product in available_products}
        popular_products = [id_to_product[pid] for pid in sorted_product_ids if pid in id_to_product]

        # Fill with newest products if less than 8 popular
        if len(popular_products) < 8:
            needed = 8 - len(popular_products)
            excluded_ids = set(p.id for p in popular_products)
            newest_products = available_products.exclude(id__in=excluded_ids).order_by('-created_at')[:needed]
            popular_products.extend(newest_products)

        context['popular_products'] = popular_products[:8]  # Max 8 items
        context['form'] = ContactForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        context = self.get_context_data()
        if form.is_valid():
            form.save()
            context['form'] = ContactForm()
            context['success'] = True
        else:
            context['form'] = form
        return self.render_to_response(context)
