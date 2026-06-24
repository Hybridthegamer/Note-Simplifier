from functools import wraps
from flask import current_app, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import UserModel


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(current_app.db, user_id)
            if not user:
                return jsonify({"error": "User not found"}), 401
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Unauthorized", "detail": str(e)}), 401
    return wrapper


def require_admin(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = UserModel.find_by_id(current_app.db, user_id)
            if not user or user.get("role") != "admin":
                return jsonify({"error": "Admin access required"}), 403
            return fn(*args, **kwargs)
        except Exception as e:
            return jsonify({"error": "Unauthorized", "detail": str(e)}), 401
    return wrapper
