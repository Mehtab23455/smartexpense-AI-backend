# expenses/urls.py
from django.urls import path
from .views import ExpenseListCreateView, ExpenseRetrieveView

urlpatterns = [
    path("", ExpenseListCreateView.as_view(), name="expense_list_create"),
    path("<int:pk>/", ExpenseRetrieveView.as_view(), name="expense_detail"),
]
