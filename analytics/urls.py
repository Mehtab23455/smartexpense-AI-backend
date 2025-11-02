# analytics/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('summary/', views.expense_summary, name='expense_summary'),
    path('trends/', views.expense_trends, name='expense_trends'),

]
