from django.db import models
from django.conf import settings
from django.core.validators import RegexValidator
from product.models import Product

class Order(models.Model):
    # ----- Order Status Choices -----
    PENDING = 'Pending'
    PROCESSING = 'Processing'
    SHIPPED = 'Shipped'
    DELIVERED = 'Delivered'
    CANCELLED = 'Cancelled'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (SHIPPED, 'Shipped'),
        (DELIVERED, 'Delivered'),
        (CANCELLED, 'Cancelled'),
    ]

    # ----- Payment Method Choices -----
    ESEWA = 'eSewa'
    CASH_ON_DELIVERY = 'Cash on Delivery'

    PAYMENT_METHOD_CHOICES = [
        (ESEWA, 'eSewa'),
        (CASH_ON_DELIVERY, 'Cash on Delivery'),
    ]

    # ----- Payment Status Choices -----
    PAYMENT_PENDING = 'Pending'
    PAYMENT_PAID = 'Paid'
    PAYMENT_FAILED = 'Failed'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_PAID, 'Paid'),
        (PAYMENT_FAILED, 'Failed'),
    ]

    # ----- Validators -----
    phone_validator = RegexValidator(
        regex=r'^(97|98)\d{8}$',
        message='Enter a valid Nepali 10-digit mobile number starting with 97 or 98.'
    )

    # ----- Fields -----
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipping_address = models.TextField()
    phone = models.CharField(max_length=10, validators=[phone_validator])
    notes = models.TextField(blank=True)
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHOD_CHOICES,
        default=CASH_ON_DELIVERY
    )
    esewa_ref_id = models.CharField(max_length=100, blank=True, null=True)
    is_payment_verified = models.BooleanField(default=False)
    payment_status = models.CharField(
        max_length=20, 
        choices=PAYMENT_STATUS_CHOICES, 
        default=PAYMENT_PENDING
    )

    def __str__(self):
        return f'Order #{self.order_number}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantity} x {self.product.name}'

    def get_total_price(self):
        return self.quantity * self.price