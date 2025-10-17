from django.urls import path
from . import views

urlpatterns = [
    path('', views.ProductListView.as_view(), name='product_list'),
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail'),
]
