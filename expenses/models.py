# expenses/models.py
from django.db import models
from django.conf import settings

# ✅ Define CATEGORY_CHOICES at module level so it can be imported anywhere
CATEGORY_CHOICES = [
    ('Food & Dining', 'Food & Dining'),
    ('Travel', 'Travel'),
    ('Shopping', 'Shopping'),
    ('Utilities', 'Utilities'),
    ('Entertainment', 'Entertainment'),
    ('Other', 'Other'),
]


class Merchant(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Expense(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="expenses"
    )
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date = models.DateField(null=True, blank=True)

    # ✅ Use the same CATEGORY_CHOICES from the global scope
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="Other")

    receipt_image = models.ImageField(upload_to="receipts/%Y/%m/%d/", null=True, blank=True)
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.merchant or 'Unknown'} - {self.amount}"
