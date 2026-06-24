from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.middleware.auth_middleware import require_auth
from app.models.document import DocumentModel
from app.services.text_extractor import extract_text

docs_bp = Blueprint("documents", __name__)

ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
MAX_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@docs_bp.post("/upload")
@require_auth
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files["file"]
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": f"File type '{ext}' not supported. Use PDF, DOCX or TXT."}), 400

    file_bytes = file.read()
    if len(file_bytes) > MAX_SIZE_BYTES:
        return jsonify({"error": "File exceeds 20 MB limit"}), 413

    file_size_kb = len(file_bytes) / 1024

    try:
        raw_text, word_count = extract_text(file_bytes, ext)
    except Exception as e:
        return jsonify({"error": f"Text extraction failed: {str(e)}"}), 422

    if not raw_text.strip():
        return jsonify({"error": "Document appears to be empty or could not be read"}), 422

    user_id = get_jwt_identity()
    doc = DocumentModel.create(
        current_app.db,
        user_id=user_id,
        original_filename=file.filename,
        file_type=ext,
        raw_text=raw_text,
        file_size_kb=round(file_size_kb, 2),
    )
    return jsonify({
        "message": "Document uploaded successfully",
        "document": DocumentModel.to_public(doc),
        "word_count": word_count,
    }), 201


@docs_bp.get("/")
@require_auth
def list_documents():
    user_id = get_jwt_identity()
    docs = DocumentModel.find_by_user(current_app.db, user_id)
    return jsonify([DocumentModel.to_public(d) for d in docs]), 200


@docs_bp.get("/<doc_id>")
@require_auth
def get_document(doc_id):
    user_id = get_jwt_identity()
    doc = DocumentModel.find_by_id(current_app.db, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    if str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403
    return jsonify(DocumentModel.to_public(doc)), 200


@docs_bp.delete("/<doc_id>")
@require_auth
def delete_document(doc_id):
    user_id = get_jwt_identity()
    doc = DocumentModel.find_by_id(current_app.db, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    if str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403
    DocumentModel.delete(current_app.db, doc_id)
    return jsonify({"message": "Document deleted"}), 200
