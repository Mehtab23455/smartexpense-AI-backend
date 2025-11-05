# ml/categorizer.py
import os
import joblib
import re

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.pkl")

def categorize_expense(merchant, raw_text):
    """
    Predict category using the trained model.
    Fallback to simple keyword-based rules if model not available.
    """
    text = f"{merchant} {raw_text}".lower()

    # Try ML model
    if os.path.exists(MODEL_PATH):
        vectorizer, model = joblib.load(MODEL_PATH)
        X = vectorizer.transform([text])
        return model.predict(X)[0]

    # Fallback rules
    if "pizza" in text or "domino" in text or "restaurant" in text:
        return "Food & Dining"
    if "uber" in text or "ola" in text or "fuel" in text:
        return "Transport"
    if "amazon" in text or "flipkart" in text:
        return "Shopping"
    if "electricity" in text or "wifi" in text:
        return "Utilities"

    return "Miscellaneous"