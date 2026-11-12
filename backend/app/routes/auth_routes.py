"""Registration, login and current-user endpoints."""
import re

from flask import Blueprint, g, jsonify, request

from ..auth import create_token, login_required
from ..models import User, db

bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MOBILE_RE = re.compile(r"^[6-9]\d{9}$")  # Indian 10-digit mobile


@bp.post("/register")
def register():
    """Public registration is for CITIZENS only. CMO and officer accounts are created by admins/seed."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    mobile = (data.get("mobile") or "").strip()
    password = data.get("password") or ""

    errors = {}
    if len(name) < 2:
        errors["name"] = "Name is required"
    if not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email"
    if not MOBILE_RE.match(mobile):
        errors["mobile"] = "Enter a valid 10-digit mobile number"
    if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Za-z]", password):
        errors["password"] = "Password must be at least 8 characters with letters and numbers"
    if not errors and User.query.filter_by(email=email).first():
        errors["email"] = "An account with this email already exists"
    if errors:
        return jsonify(error="Validation failed", fields=errors), 400

    user = User(name=name, email=email, mobile=mobile, role="citizen")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify(token=create_token(user), user=user.to_dict()), 201


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(data.get("password") or ""):
        return jsonify(error="Invalid email or password"), 401
    return jsonify(token=create_token(user), user=user.to_dict())


@bp.get("/me")
@login_required()
def me():
    return jsonify(user=g.user.to_dict())


@bp.post("/logout")
@login_required()
def logout():
    # JWTs are stateless: the client deletes its token. Endpoint kept for API completeness.
    return jsonify(message="Logged out")
