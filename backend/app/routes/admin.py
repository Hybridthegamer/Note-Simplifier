from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from bson import ObjectId
from app.middleware.auth_middleware import require_admin
from app.models.user import UserModel

admin_bp = Blueprint("admin", __name__)


@admin_bp.get("/users")
@require_admin
def list_users():
    users = list(current_app.db["users"].find({}, {"password_hash": 0}))
    return jsonify([UserModel.to_public(u) for u in users]), 200


@admin_bp.get("/stats")
@require_admin
def stats():
    db = current_app.db
    return jsonify({
        "total_users": db["users"].count_documents({}),
        "total_documents": db["documents"].count_documents({}),
        "total_summaries": db["summaries"].count_documents({}),
        "total_quizzes": db["quizzes"].count_documents({}),
        "documents_by_status": {
            "uploaded": db["documents"].count_documents({"status": "uploaded"}),
            "processing": db["documents"].count_documents({"status": "processing"}),
            "processed": db["documents"].count_documents({"status": "processed"}),
            "error": db["documents"].count_documents({"status": "error"}),
        },
    }), 200


@admin_bp.delete("/users/<user_id>")
@require_admin
def delete_user(user_id):
    db = current_app.db
    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "Invalid user ID"}), 400

    requester_id = get_jwt_identity()
    if user_id == requester_id:
        return jsonify({"error": "Cannot delete your own account via admin"}), 400

    db["users"].delete_one({"_id": oid})
    return jsonify({"message": "User deleted"}), 200
