# ml/ocr.py
import re
from PIL import Image
import pytesseract
from dateutil import parser as dateparser

# Basic regex patterns
AMOUNT_REGEX = re.compile(r'([₹₹\$\€]\s?[\d,]+(?:\.\d{1,2})?)|(\bTotal\b[:\s]*([0-9]+(?:\.[0-9]{1,2})?))', re.IGNORECASE)
DATE_REGEX = re.compile(r'(\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4})')

def run_ocr(image_path):
    """
    Returns the raw text extracted from the image.
    """
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def extract_entities(text):
    """
    Returns a dict with keys: merchant (str), amount (float), date (date obj or string), raw_text.
    Heuristics:
     - merchant: first non-empty line
     - amount: first match to currency pattern
     - date: first matched date-like string parsed by dateutil
    """
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = lines[0] if lines else None

    amount = None
    m_amount = AMOUNT_REGEX.search(text)
    if m_amount:
        # try to get numeric part
        amt_str = m_amount.group(0)
        # remove currency symbols and commas
        amt_num = re.sub(r'[^\d\.]', '', amt_str)
        try:
            amount = float(amt_num)
        except:
            amount = None

    date_val = None
    m_date = DATE_REGEX.search(text)
    if m_date:
        try:
            date_val = dateparser.parse(m_date.group(0), dayfirst=False).date()
        except:
            date_val = None

    return {
        "merchant": merchant,
        "amount": amount,
        "date": date_val,
        "raw_text": text,
    }
