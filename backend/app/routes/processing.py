from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.middleware.auth_middleware import require_auth
from app.models.document import DocumentModel
from app.models.summary import SummaryModel
from app.services.nlp_pipeline import simplify_text
from app.services.keyword_extractor import extract_keywords

processing_bp = Blueprint("processing", __name__)


@processing_bp.post("/<doc_id>")
@require_auth
def process_document(doc_id):
    """
    Run the full NLP pipeline on an uploaded document.
    Body: { complexity_level: "basic"|"intermediate"|"advanced", include_keywords: bool }
    """
    user_id = get_jwt_identity()
    doc = DocumentModel.find_by_id(current_app.db, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    if str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json(silent=True) or {}
    complexity_level = data.get("complexity_level", "intermediate").lower()
    include_keywords = data.get("include_keywords", True)

    if complexity_level not in ("basic", "intermediate", "advanced"):
        complexity_level = "intermediate"

    DocumentModel.update_status(current_app.db, doc_id, "processing")

    try:
        simplified_text, _ = simplify_text(doc["raw_text"], complexity_level)

        key_concepts = []
        if include_keywords:
            key_concepts = extract_keywords(simplified_text, top_n=15, enrich_definitions=True)

        word_count = len(simplified_text.split())
        summary = SummaryModel.create(
            current_app.db,
            doc_id=doc_id,
            simplified_text=simplified_text,
            complexity_level=complexity_level,
            key_concepts=key_concepts,
            word_count=word_count,
        )
        DocumentModel.update_status(current_app.db, doc_id, "processed")
        return jsonify({
            "message": "Processing complete",
            "summary": SummaryModel.to_public(summary),
        }), 200

    except Exception as e:
        DocumentModel.update_status(current_app.db, doc_id, "error")
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500


@processing_bp.get("/<doc_id>/summaries")
@require_auth
def get_summaries(doc_id):
    user_id = get_jwt_identity()
    doc = DocumentModel.find_by_id(current_app.db, doc_id)
    if not doc:
        return jsonify({"error": "Document not found"}), 404
    if str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403

    summaries = SummaryModel.find_by_doc(current_app.db, doc_id)
    return jsonify([SummaryModel.to_public(s) for s in summaries]), 200


@processing_bp.get("/summary/<summary_id>")
@require_auth
def get_summary(summary_id):
    user_id = get_jwt_identity()
    summary = SummaryModel.find_by_id(current_app.db, summary_id)
    if not summary:
        return jsonify({"error": "Summary not found"}), 404

    doc = DocumentModel.find_by_id(current_app.db, str(summary["doc_id"]))
    if not doc or str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403

    return jsonify(SummaryModel.to_public(summary)), 200
