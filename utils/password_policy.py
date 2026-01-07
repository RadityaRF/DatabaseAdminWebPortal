import re

def validate_password(password: str):
    """
    Enforce strong password policy
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long"

    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter"

    if not re.search(r"[0-9]", password):
        return "Password must contain at least one number"

    if not re.search(r"[^A-Za-z0-9]", password):
        return "Password must contain at least one special character"

    return None
