# expenses/views.py
from rest_framework import generics, permissions, status
from .serializers import ExpenseSerializer, MerchantSerializer
from .models import Expense, Merchant
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from ml.ocr import run_ocr, extract_entities
from django.utils import timezone

class ExpenseListCreateView(generics.ListCreateAPIView):
    queryset = Expense.objects.all().order_by("-created_at")
    serializer_class = ExpenseSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Expense.objects.filter(user=user).order_by("-created_at")
        return Expense.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        image = self.request.FILES.get("receipt_image")
        # save first without merchant/amount/date/raw_text to get file path
        instance = serializer.save(user=user)
        # run OCR on saved image file
        if image:
            # path on disk
            image_path = instance.receipt_image.path
            raw_text = run_ocr(image_path)
            entities = extract_entities(raw_text)
            merchant_name = entities.get("merchant")
            amount = entities.get("amount")
            date_val = entities.get("date")
            # get or create merchant
            merchant_obj = None
            if merchant_name:
                merchant_obj, _ = Merchant.objects.get_or_create(name=merchant_name)
            instance.merchant = merchant_obj
            if amount:
                instance.amount = amount
            if date_val:
                instance.date = date_val
            instance.raw_text = raw_text
            instance.save()

class ExpenseRetrieveView(generics.RetrieveAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = (permissions.IsAuthenticated,)
