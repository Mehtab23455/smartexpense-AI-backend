from rest_framework import viewsets, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.views import APIView
from django.db import transaction
from .models import Expense, Merchant, CATEGORY_CHOICES  # ✅ import category choices
from .serializers import ExpenseSerializer
from ml.ocr import run_ocr, extract_entities
from ml.categorizer import categorize_expense


# ✅ Upload Receipt (AI Extraction)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_receipt(request):
    image = request.FILES.get('receipt_image')
    if not image:
        return Response({"error": "No image uploaded"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # Step 1: Run OCR to extract text from image
        text = run_ocr(image)
        if not text.strip():
            return Response({"error": "No text extracted from image"}, status=status.HTTP_400_BAD_REQUEST)

        # Step 2: Extract entities (merchant, date, amount)
        entities = extract_entities(text)
        if not entities:
            return Response({"error": "Entity extraction failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Step 3: Categorize expense based on merchant or raw text
        category = categorize_expense(entities.get("merchant", ""), entities.get("raw_text", text))

        # ✅ Step 4: Fallback for unknown categories
        valid_categories = dict(CATEGORY_CHOICES)
        if category not in valid_categories:
            category = "Other"

        entities["category"] = category
        entities["raw_text"] = text

        return Response(entities, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"[AI Extraction Error] {e}")
        return Response({"error": f"Error during AI extraction: {str(e)}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ✅ Expense CRUD ViewSet
class ExpenseViewSet(viewsets.ModelViewSet):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        """Return only the logged-in user's expenses."""
        return Expense.objects.filter(user=self.request.user).order_by("-created_at")

    @transaction.atomic
    def perform_create(self, serializer):
        """Attach user to expense, and validate unknown categories."""
        user = self.request.user
        image = self.request.FILES.get("receipt_image")

        instance = serializer.save(user=user)

        # ✅ Normalize unknown categories
        valid_categories = dict(CATEGORY_CHOICES)
        if instance.category not in valid_categories:
            instance.category = "Other"

        if image:
            try:
                image_path = instance.receipt_image.path
                raw_text = run_ocr(image_path)
                entities = extract_entities(raw_text)

                merchant_name = entities.get("merchant")
                amount = entities.get("amount")
                date_val = entities.get("date")

                # Create or get merchant object
                merchant_obj = None
                if merchant_name:
                    merchant_obj, _ = Merchant.objects.get_or_create(name=merchant_name)

                # Assign extracted data
                instance.merchant = merchant_obj
                if amount:
                    instance.amount = amount
                if date_val:
                    instance.date = date_val
                instance.raw_text = raw_text
                instance.save()

            except Exception as e:
                print(f"[OCR Error] {e}")
                instance.raw_text = "OCR processing failed"
                instance.save()

        return instance


# ✅ Basic OCR + Category Endpoint (Optional)
class ExpenseExtractView(APIView):
    def post(self, request):
        image = request.FILES.get("image")
        if not image:
            return Response({"error": "No image uploaded"}, status=400)

        text = run_ocr(image)
        category = categorize_expense(text)

        valid_categories = dict(CATEGORY_CHOICES)
        if category not in valid_categories:
            category = "Other"

        return Response({
            "text": text,
            "category": category
        })
