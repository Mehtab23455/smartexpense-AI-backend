from django.contrib import admin
from .models import Expense, Merchant

@admin.register(Merchant)
class MerchantAdmin(admin.ModelAdmin):
    list_display = ("name",)

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("user", "merchant", "amount", "date", "created_at")
    list_filter = ("category", "date", "merchant")
    search_fields = ("merchant__name", "raw_text")
