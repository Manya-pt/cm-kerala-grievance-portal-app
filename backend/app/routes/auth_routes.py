"""Registration, login and current-user endpoints."""
from flask import Blueprint, g, jsonify, request

from ..auth import create_token, login_required
from ..models import User, db
from ..validators import validate_account

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/register")
def register():
    """Public registration is for CITIZENS only. The CMO account is created from the command line
    (python -m app.cli create-cmo) and officers are created by the CMO."""
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    mobile = (data.get("mobile") or "").strip()
    password = data.get("password") or ""

    errors = validate_account(name, email, mobile, password)
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
