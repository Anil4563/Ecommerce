from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Category, Product

class ProductListView(ListView):
    model = Product
    template_name = 'product/product_list.html'
    context_object_name = 'products'
    paginate_by = 12

    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        search_query = self.request.GET.get('q', '').strip()

        if search_query:
            # Prefix search (case-insensitive)
            queryset = queryset.filter(name__istartswith=search_query)

        # Category filter
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)

        # Fragrance filter
        fragrance = self.request.GET.get('fragrance')
        if fragrance:
            queryset = queryset.filter(fragrance=fragrance)

        # Burn time filter
        burn_time = self.request.GET.get('burn_time')
        if burn_time:
            queryset = queryset.filter(burn_time=burn_time)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['fragrances'] = Product.objects.values_list('fragrance', flat=True).distinct()
        context['burn_times'] = Product.objects.values_list('burn_time', flat=True).distinct()
        context['q'] = self.request.GET.get('q', '')
        return context


class ProductDetailView(DetailView):
    model = Product
    template_name = 'product/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_products'] = Product.objects.filter(
            category=self.object.category,
            is_available=True
        ).exclude(id=self.object.id)[:4]
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'product/category_list.html'
    context_object_name = 'categories'