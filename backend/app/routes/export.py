from flask import Blueprint, send_file, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
import io

from app.middleware.auth_middleware import require_auth
from app.models.summary import SummaryModel
from app.models.document import DocumentModel
from app.models.quiz import QuizModel
from app.services.export_service import (
    export_notes_pdf, export_notes_docx,
    export_quiz_pdf, export_quiz_docx,
)

export_bp = Blueprint("export", __name__)


@export_bp.get("/notes/<summary_id>/pdf")
@require_auth
def download_notes_pdf(summary_id):
    user_id = get_jwt_identity()
    summary, doc = _get_summary_and_doc(summary_id, user_id)
    if summary is None:
        return jsonify({"error": "Not found or access denied"}), 404

    pdf_bytes = export_notes_pdf(
        doc["original_filename"],
        summary["simplified_text"],
        summary.get("key_concepts", []),
        summary["complexity_level"],
    )
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"notes_{doc['original_filename'].rsplit('.', 1)[0]}.pdf",
    )


@export_bp.get("/notes/<summary_id>/docx")
@require_auth
def download_notes_docx(summary_id):
    user_id = get_jwt_identity()
    summary, doc = _get_summary_and_doc(summary_id, user_id)
    if summary is None:
        return jsonify({"error": "Not found or access denied"}), 404

    docx_bytes = export_notes_docx(
        doc["original_filename"],
        summary["simplified_text"],
        summary.get("key_concepts", []),
        summary["complexity_level"],
    )
    return send_file(
        io.BytesIO(docx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=f"notes_{doc['original_filename'].rsplit('.', 1)[0]}.docx",
    )


@export_bp.get("/quiz/<quiz_id>/pdf")
@require_auth
def download_quiz_pdf(quiz_id):
    user_id = get_jwt_identity()
    quiz = QuizModel.find_by_id(current_app.db, quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    pdf_bytes = export_quiz_pdf("Quiz", quiz["questions"])
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"quiz_{quiz_id}.pdf",
    )


@export_bp.get("/quiz/<quiz_id>/docx")
@require_auth
def download_quiz_docx(quiz_id):
    user_id = get_jwt_identity()
    quiz = QuizModel.find_by_id(current_app.db, quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    docx_bytes = export_quiz_docx("Quiz", quiz["questions"])
    return send_file(
        io.BytesIO(docx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=f"quiz_{quiz_id}.docx",
    )


def _get_summary_and_doc(summary_id: str, user_id: str):
    summary = SummaryModel.find_by_id(current_app.db, summary_id)
    if not summary:
        return None, None
    doc = DocumentModel.find_by_id(current_app.db, str(summary["doc_id"]))
    if not doc or str(doc["user_id"]) != user_id:
        return None, None
    return summary, doc
