import re
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity
from app.models.user import UserModel
from app.middleware.auth_middleware import require_auth

auth_bp = Blueprint("auth", __name__)

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?]).{8,}$")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    full_name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not full_name or not email or not password:
        return jsonify({"error": "full_name, email and password are required"}), 400
    if not EMAIL_RE.match(email):
        return jsonify({"error": "Invalid email address"}), 400
    if not PASSWORD_RE.match(password):
        return jsonify({
            "error": "Password must be at least 8 characters and include an uppercase letter, "
                     "a number, and a special character"
        }), 400

    db = current_app.db
    if UserModel.find_by_email(db, email):
        return jsonify({"error": "Email already registered"}), 409

    user = UserModel.create(db, full_name, email, password)
    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token, "user": UserModel.to_public(user)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400

    db = current_app.db
    user = UserModel.find_by_email(db, email)
    if not user or not UserModel.verify_password(password, user["password_hash"]):
        return jsonify({"error": "Invalid credentials"}), 401

    UserModel.update_last_login(db, str(user["_id"]))
    token = create_access_token(identity=str(user["_id"]))
    return jsonify({"token": token, "user": UserModel.to_public(user)}), 200


@auth_bp.get("/me")
@require_auth
def me():
    user_id = get_jwt_identity()
    user = UserModel.find_by_id(current_app.db, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(UserModel.to_public(user)), 200
