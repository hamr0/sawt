import re

def normalize_arabic(text: str) -> str:
    """Normalize Arabic text by removing extra spaces and tatweel"""
    text = re.sub(r'[ـ_]', '', text)  # Remove tatweel
    text = re.sub(r'\s+', ' ', text)  # Normalize spaces
    return text.strip()

def contains_arabic(text: str) -> bool:
    """Check if text contains Arabic characters"""
    return bool(re.search(r'[\u0600-\u06FF]', text))