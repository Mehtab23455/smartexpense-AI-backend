# expenses/models.py
from django.db import models
from django.contrib.auth.models import User

class Merchant(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ("food", "Food"),
        ("travel", "Travel"),
        ("shopping", "Shopping"),
        ("utilities", "Utilities"),
        ("other", "Other"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="expenses")
    merchant = models.ForeignKey(Merchant, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="other")
    receipt_image = models.ImageField(upload_to="receipts/%Y/%m/%d/")
    raw_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.merchant or 'Unknown'} - {self.amount}"
