from django.db import models

class Donation(models.Model):
    PAYMENT_METHODS = (
        ('mtn', 'MTN Mobile Money'),
        ('airtel', 'Airtel Money'),
        ('bank', 'Bank Transfer'),
        ('paypal', 'PayPal / Credit Card'),
    )
    donor_name = models.CharField(max_length=150, default="Anonymous")
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="UGX")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    transaction_reference = models.CharField(max_length=100, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - {self.currency} {self.amount} ({self.payment_method})"
