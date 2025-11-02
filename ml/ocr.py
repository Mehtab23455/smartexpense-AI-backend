import re
from PIL import Image, UnidentifiedImageError
import pytesseract
from dateutil import parser as dateparser

# ✅ Set Tesseract executable path (Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

# ✅ Regex patterns
AMOUNT_REGEX = re.compile(
    r'(?:(?:Rs\.?|INR|₹|USD|EUR|€|£)\s?[\d,]+(?:\.\d{1,2})?)|(?:Total[:\s]*([0-9]+(?:\.[0-9]{1,2})?))',
    re.IGNORECASE
)

# ✅ Date pattern now supports both numeric and text-based formats
DATE_REGEX = re.compile(
    r'(\d{1,2}[\/\-\.\s]?[A-Za-z]{3,9}[\/\-\.\s]?\d{2,4}|\d{1,2}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{2,4}|\d{4}[\/\-\.\s]\d{1,2}[\/\-\.\s]\d{1,2})',
    re.IGNORECASE
)

def run_ocr(image_path):
    """
    Extracts raw text from an image using Tesseract OCR.
    Returns:
        str: OCR extracted text or error message.
    """
    try:
        img = Image.open(image_path)
        # Convert to grayscale for better OCR accuracy
        img = img.convert("L")
        text = pytesseract.image_to_string(img)
        # Normalize OCR text
        text = (
            text.replace("₹", "Rs ")
                .replace("=", "")
                .replace("~", "-")
                .replace("—", "-")
        )
        if not text.strip():
            return "No text detected"
        print("\n🧾 OCR Extracted Text:\n", text, "\n-----------------------")  # debug log
        return text
    except FileNotFoundError:
        return "OCR Error: Image file not found"
    except UnidentifiedImageError:
        return "OCR Error: Invalid image format"
    except Exception as e:
        return f"OCR Error: {str(e)}"


def extract_entities(text):
    """
    Extracts structured data from OCR text.
    Returns:
        dict: {merchant, amount, date, raw_text}
    """
    if not text or "OCR Error" in text:
        return {"error": text, "raw_text": ""}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = "Unknown"

    # --- MERCHANT EXTRACTION ---
    for line in lines:
        if len(line.split()) <= 5 and not re.search(r'(invoice|bill|tax|receipt|table|number|amount|total)', line, re.IGNORECASE):
            merchant = line
            break

    # --- AMOUNT EXTRACTION ---
    amount = None

    # Look for TOTAL and capture number on same or nearby lines
    for i, line in enumerate(lines):
        if re.search(r'(total|grand total|net amount|amt payable)', line, re.IGNORECASE):
            nearby_text = " ".join(lines[i:i+2])  # current + next line
            m = re.search(r'([₹RsINR]*\s*[\d.,\s]+)', nearby_text, re.IGNORECASE)
            if m:
                amt_str = m.group(1)
                amt_str = re.sub(r'[^\d.,\s]', '', amt_str)
                amt_str = amt_str.replace(',', '').replace(' ', '').strip()
                amt_str = amt_str.replace(',', '').replace(' ', '').strip()
                amt_str = amt_str.replace(' ', '.')
                try:
                    amount = float(amt_str)
                    break
                except ValueError:
                    pass

    # Fallback — last numeric value in text (often the total)
    if amount is None:
        all_numbers = re.findall(r'([0-9]+[.,\s]?[0-9]{2})', text)
        parsed = []
        for n in all_numbers:
            n_clean = n.replace(',', '').replace(' ', '.')
            try:
                parsed.append(float(n_clean))
            except ValueError:
                continue
        if parsed:
            amount = parsed[-1]  # take the last amount seen (usually the total)

    # --- DATE EXTRACTION ---
    date_val = None
    m_date = DATE_REGEX.search(text)
    if m_date:
        try:
            date_val = dateparser.parse(m_date.group(0), fuzzy=True).date()
        except Exception:
            date_val = None

    return {
        "merchant": merchant,
        "amount": round(amount, 2) if amount else 0.0,
        "date": str(date_val) if date_val else None,
        "raw_text": text.strip(),
    }

    """
    Extracts structured data from OCR text.
    Returns:
        dict: {merchant, amount, date, raw_text}
    """
    if not text or "OCR Error" in text:
        return {"error": text, "raw_text": ""}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = "Unknown"

    # --- MERCHANT EXTRACTION ---
    for line in lines:
        if len(line.split()) <= 5 and not re.search(r'(invoice|bill|tax|receipt|table|number|amount|total)', line, re.IGNORECASE):
            merchant = line
            break

    # --- AMOUNT EXTRACTION ---
    amount = None

    # 1️⃣ Find "TOTAL" or "GRAND TOTAL" and get number on same or next line
    for i, line in enumerate(lines):
        if re.search(r'(total|grand total)', line, re.IGNORECASE):
            # Check this line
            m1 = re.search(r'([0-9]+[.,\s]?[0-9]{2})', line)
            if m1:
                amount_str = m1.group(1).replace(',', '').replace(' ', '.')
                try:
                    amount = float(amount_str)
                    break
                except ValueError:
                    pass

            # Check next line if no number on same line
            if i + 1 < len(lines):
                m2 = re.search(r'([0-9]+[.,\s]?[0-9]{2})', lines[i + 1])
                if m2:
                    amount_str = m2.group(1).replace(',', '').replace(' ', '.')
                    try:
                        amount = float(amount_str)
                        break
                    except ValueError:
                        pass

    # 2️⃣ If still not found, fallback to the **largest** numeric value in the text
    if amount is None:
        all_numbers = re.findall(r'([0-9]+[.,\s]?[0-9]{2})', text)
        parsed = []
        for n in all_numbers:
            n_clean = n.replace(',', '').replace(' ', '.')
            try:
                val = float(n_clean)
                if val > 10:  # ignore tiny prices
                    parsed.append(val)
            except ValueError:
                continue
        if parsed:
            amount = max(parsed)

    # --- DATE EXTRACTION ---
    date_val = None
    m_date = DATE_REGEX.search(text)
    if m_date:
        try:
            date_val = dateparser.parse(m_date.group(0), fuzzy=True).date()
        except Exception:
            date_val = None

    return {
        "merchant": merchant,
        "amount": round(amount, 2) if amount else 0.0,
        "date": str(date_val) if date_val else None,
        "raw_text": text.strip(),
    }

    """
    Extracts structured data from OCR text.
    Returns:
        dict: {merchant, amount, date, raw_text}
    """
    if not text or "OCR Error" in text:
        return {"error": text, "raw_text": ""}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = "Unknown"

    # --- MERCHANT EXTRACTION ---
    for line in lines:
        if len(line.split()) <= 5 and not re.search(r'(invoice|bill|tax|receipt|table|number|amount|total)', line, re.IGNORECASE):
            merchant = line
            break

    # --- AMOUNT EXTRACTION ---
    amount = None
    total_line_found = False

    # 1️⃣ Try to find a "TOTAL" or "GRAND TOTAL" line and extract number from it
    for line in lines:
        if re.search(r'(total|grand total)', line, re.IGNORECASE):
            total_line_found = True
            m_total = re.search(r'([0-9]+(?:\.[0-9]{1,2})?)', line)
            if m_total:
                try:
                    amount = float(m_total.group(1))
                    break
                except ValueError:
                    continue

    # 2️⃣ If no explicit "TOTAL" line found, get **largest** number (skip small line-item prices)
    if not total_line_found:
        all_numbers = re.findall(r'([0-9]+(?:\.[0-9]{1,2})?)', text)
        if all_numbers:
            try:
                nums = [float(n) for n in all_numbers if float(n) > 10]  # ignore tiny prices like 3.5, 6.75
                if nums:
                    amount = max(nums)
            except ValueError:
                pass

    # --- DATE EXTRACTION ---
    date_val = None
    m_date = DATE_REGEX.search(text)
    if m_date:
        try:
            date_val = dateparser.parse(m_date.group(0), fuzzy=True).date()
        except Exception:
            date_val = None

    return {
        "merchant": merchant,
        "amount": round(amount, 2) if amount else 0.0,
        "date": str(date_val) if date_val else None,
        "raw_text": text.strip(),
    }

    """
    Extracts structured data from OCR text.
    Returns:
        dict: {merchant, amount, date, raw_text}
    """
    if not text or "OCR Error" in text:
        return {"error": text, "raw_text": ""}

    lines = [l.strip() for l in text.splitlines() if l.strip()]
    merchant = "Unknown"

    # ✅ Identify merchant name (avoid generic headers)
    for line in lines:
        if len(line.split()) <= 5 and not re.search(r'(invoice|bill|tax|receipt|table|number|amount|total)', line, re.IGNORECASE):
            merchant = line
            break

    # ✅ Extract amount — prioritize TOTAL or GRAND TOTAL lines
    amount = None
    for line in lines:
        if re.search(r'(total|grand total)', line, re.IGNORECASE):
            m_total = re.search(r'([0-9]+(?:\.[0-9]{1,2})?)', line)
            if m_total:
                try:
                    amount = float(m_total.group(1))
                    break
                except ValueError:
                    continue

    # Fallback: use all numbers, pick the largest
    if not amount:
        m_amounts = AMOUNT_REGEX.findall(text)
        if m_amounts:
            cleaned = []
            for val in m_amounts:
                num_str = re.sub(r'[^\d\.]', '', val if isinstance(val, str) else ''.join(val))
                if num_str:
                    try:
                        cleaned.append(float(num_str))
                    except ValueError:
                        pass
            if cleaned:
                amount = max(cleaned)

    # ✅ Extract date (supports formats like 25AUG2018, 25/08/2018, etc.)
    date_val = None
    m_date = DATE_REGEX.search(text)
    if m_date:
        try:
            date_val = dateparser.parse(m_date.group(0), fuzzy=True).date()
        except Exception:
            date_val = None

    return {
        "merchant": merchant,
        "amount": round(amount, 2) if amount else 0.0,
        "date": str(date_val) if date_val else None,
        "raw_text": text.strip(),
    }
