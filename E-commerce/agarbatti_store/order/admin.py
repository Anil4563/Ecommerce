from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ('product',)  # updated

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number', 'user', 'status', 'payment_method', 'total', 'esewa_ref_id', 'created_at'
    )
    list_filter = ('status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'esewa_ref_id')
    inlines = (OrderItemInline,)
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'esewa_ref_id')
    
    fieldsets = (
        (None, {
            'fields': ('order_number', 'user', 'status', 'payment_method', 'esewa_ref_id')
        }),
        ('Billing', {
            'fields': ('total', 'shipping_address', 'phone', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'product', 'quantity', 'price', 'get_total_price')  # updated
    list_filter = ('order__status',)
    search_fields = ('product__name', 'order__order_number')  # updated
    
    def get_total_price(self, obj):
        return obj.get_total_price()
    get_total_price.short_description = 'Total Price'
