# analytics/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions
from expenses.models import Expense
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from expenses.models import Expense
from datetime import datetime
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions, status
from rest_framework.response import Response
from expenses.models import Expense

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expense_summary(request):
    user = request.user

    # Total spend per category
    category_summary = (
        Expense.objects.filter(user=user)
        .values("category")
        .annotate(total=Sum("amount"))
        .order_by("-total")
    )

    # Total spend per merchant
    merchant_summary = (
        Expense.objects.filter(user=user)
        .values("merchant")
        .annotate(total=Sum("amount"))
        .order_by("-total")[:10]  # top 10 merchants
    )

    # Monthly spend trend
    monthly_trend = (
        Expense.objects.filter(user=user)
        .annotate(month=TruncMonth("date"))
        .values("month")
        .annotate(total=Sum("amount"))
        .order_by("month")
    )

    return Response({
        "category_summary": list(category_summary),
        "merchant_summary": list(merchant_summary),
        "monthly_trend": list(monthly_trend),
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def expense_summary(request):
    """
    Returns a summary of user's total spending by category.
    """
    expenses = Expense.objects.filter(user=request.user)
    
    summary = {}
    for exp in expenses:
        cat = getattr(exp, 'category', 'Uncategorized')
        summary[cat] = summary.get(cat, 0) + exp.amount

    return Response({
        "total_expenses": sum(summary.values()),
        "category_breakdown": summary,
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def expense_trends(request):
    """
    Returns monthly expense trends for the authenticated user.
    Useful for analytics dashboard charts.
    """
    expenses = (
        Expense.objects
        .filter(user=request.user)
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total_spent=Sum('amount'))
        .order_by('month')
    )

    data = [
        {
            "month": datetime.strftime(entry['month'], "%b %Y"),
            "total_spent": entry['total_spent']
        }
        for entry in expenses
    ]

    return Response(data, status=status.HTTP_200_OK)