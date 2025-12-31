import re
from typing import Tuple


def validate_full_name(name: str) -> Tuple[bool, str]:
    """
    Validate full name (should be at least 2 words)
    Returns: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "Будь ласка, введіть ваше ПІБ"

    words = name.strip().split()
    if len(words) < 2:
        return False, "Будь ласка, введіть повне ПІБ (мінімум ім'я та прізвище)"

    # Check if contains only letters and spaces
    if not all(word.replace('-', '').replace("'", "").isalpha() for word in words):
        return False, "ПІБ повинно містити тільки букви"

    return True, ""


def validate_phone_number(phone: str) -> Tuple[bool, str, str]:
    """
    Validate Ukrainian phone number
    Returns: (is_valid, cleaned_phone, error_message)
    """
    if not phone or not phone.strip():
        return False, "", "Будь ласка, введіть номер телефону"

    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)

    # Check Ukrainian phone patterns
    # +380XXXXXXXXX (12 digits with country code)
    # 380XXXXXXXXX (11 digits with country code without +)
    # 0XXXXXXXXX (10 digits without country code)

    if cleaned.startswith('380') and len(cleaned) == 12:
        # Already has country code
        return True, f"+{cleaned}", ""
    elif cleaned.startswith('80') and len(cleaned) == 11:
        # 80... format
        return True, f"+3{cleaned}", ""
    elif cleaned.startswith('0') and len(cleaned) == 10:
        # Without country code
        return True, f"+38{cleaned}", ""
    else:
        return False, "", "Будь ласка, введіть коректний український номер телефону\nПриклад: +380501234567 або 0501234567"


def sanitize_folder_name(name: str) -> str:
    """
    Sanitize string for use as folder name
    Remove/replace invalid characters
    """
    # Replace spaces with underscores
    name = name.replace(' ', '_')

    # Remove invalid characters for folder names
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '')

    return name
