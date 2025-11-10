from django.urls import path
from . import views

urlpatterns = [
    path('history/', views.order_history, name='order_history'),
    path('checkout/', views.checkout, name='checkout'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),

    # REAL eSewa payment URLs
    path('esewa-payment/<int:order_id>/', views.esewa_payment, name='esewa_payment'),
    path('esewa-success/<int:order_id>/', views.esewa_success, name='esewa_success'),
    path('esewa-failed/<int:order_id>/', views.esewa_failed, name='esewa_failed'),

     # Demo URLs (redirect to real ones)
    path('esewa-demo/<int:order_id>/', views.esewa_demo_payment, name='esewa_demo'),
    path('esewa-success-demo/<int:order_id>/', views.esewa_success_demo, name='esewa_success_demo'),
    path('esewa-failed-demo/<int:order_id>/', views.esewa_failed_demo, name='esewa_failed_demo'),
    
]