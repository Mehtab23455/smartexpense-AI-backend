# ml/trainer.py
import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from expenses.models import Expense

MODEL_PATH = os.path.join(os.path.dirname(__file__), "ml_model.pkl")

def train_model():
    expenses = Expense.objects.exclude(category__isnull=True).values("merchant", "raw_text", "category")
    if not expenses:
        print(" Not enough data to train model.")
        return None

    df = pd.DataFrame(expenses)
    df["text"] = df["merchant"].fillna('') + " " + df["raw_text"].fillna('')

    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X = vectorizer.fit_transform(df["text"])
    y = df["category"]

    model = MultinomialNB()
    model.fit(X, y)

    joblib.dump((vectorizer, model), MODEL_PATH)
    print(f" Model trained and saved at {MODEL_PATH}")
    return MODEL_PATH
