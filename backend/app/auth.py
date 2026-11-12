"""JWT authentication and role-based access control."""
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import current_app, g, jsonify, request

from .models import User, db


def create_token(user):
    payload = {
        "sub": str(user.id),
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=current_app.config["JWT_EXPIRY_HOURS"]),
    }
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")


def _user_from_request():
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        return None
    try:
        payload = jwt.decode(header[7:], current_app.config["SECRET_KEY"], algorithms=["HS256"])
    except jwt.PyJWTError:
        return None
    return db.session.get(User, int(payload["sub"]))


def login_required(*roles):
    """Decorator: @login_required() for any logged-in user,
    @login_required("cmo") to allow only certain roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            user = _user_from_request()
            if user is None:
                return jsonify(error="Authentication required"), 401
            if roles and user.role not in roles:
                return jsonify(error="You do not have permission for this action"), 403
            g.user = user
            return fn(*args, **kwargs)
        return wrapper
    return decorator
