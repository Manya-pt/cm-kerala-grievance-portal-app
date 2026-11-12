"""Input checks shared by registration, officer creation and the command line."""
import re

from .models import User

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")  # Indian 10-digit mobile


def validate_account(name, email, mobile, password):
    """Return {field: message}. Empty dict means everything is valid."""
    errors = {}
    if len(name) < 2:
        errors["name"] = "Name is required"
    if not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email"
    if not MOBILE_RE.match(mobile):
        errors["mobile"] = "Enter a valid 10-digit mobile number"
    if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Za-z]", password):
        errors["password"] = "Password must be at least 8 characters with letters and numbers"
    if "email" not in errors and User.query.filter_by(email=email).first():
        errors["email"] = "An account with this email already exists"
    return errors
