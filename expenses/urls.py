from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExpenseViewSet
from .views import upload_receipt


router = DefaultRouter()
router.register(r"", ExpenseViewSet, basename="expenses")

urlpatterns = [
    path("", include(router.urls)),
    path('upload/receipt/', upload_receipt, name='upload_receipt'),
]