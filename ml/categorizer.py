# ml/categorizer.py
import re

def categorize_expense(merchant_name, raw_text):
    """
    Simple keyword-based categorization of expenses.
    You can later replace this with an ML model.
    """
    merchant_name = (merchant_name or "").lower()
    text = (raw_text or "").lower()

    # Keyword-based rules
    if re.search(r'(domino|pizza|kfc|burger|restaurant|food|meal)', merchant_name + text):
        return "Food & Dining"
    elif re.search(r'(uber|ola|taxi|bus|train|flight|travel)', text):
        return "Travel"
    elif re.search(r'(amazon|flipkart|shopping|mall|store)', text):
        return "Shopping"
    elif re.search(r'(electricity|water|internet|bill|gas)', text):
        return "Utilities"
    elif re.search(r'(movie|netflix|entertainment|ticket)', text):
        return "Entertainment"
    else:
        return "Others"