from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity
from app.middleware.auth_middleware import require_auth
from app.models.summary import SummaryModel
from app.models.document import DocumentModel
from app.models.quiz import QuizModel
from app.services.quiz_generator import generate_quiz

quiz_bp = Blueprint("quiz", __name__)


@quiz_bp.post("/generate/<summary_id>")
@require_auth
def generate_quiz_route(summary_id):
    """
    Generate MCQs from a summary.
    Body: { num_questions: 5–20 }
    """
    user_id = get_jwt_identity()
    summary = SummaryModel.find_by_id(current_app.db, summary_id)
    if not summary:
        return jsonify({"error": "Summary not found"}), 404

    doc = DocumentModel.find_by_id(current_app.db, str(summary["doc_id"]))
    if not doc or str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json(silent=True) or {}
    num_questions = int(data.get("num_questions", 10))
    num_questions = max(5, min(20, num_questions))

    try:
        questions = generate_quiz(summary["simplified_text"], num_questions)
        quiz = QuizModel.create(
            current_app.db,
            summary_id=summary_id,
            questions=questions,
            num_questions=len(questions),
        )
        return jsonify({
            "message": "Quiz generated",
            "quiz": QuizModel.to_public(quiz),
        }), 201
    except Exception as e:
        return jsonify({"error": f"Quiz generation failed: {str(e)}"}), 500


@quiz_bp.get("/<quiz_id>")
@require_auth
def get_quiz(quiz_id):
    user_id = get_jwt_identity()
    quiz = QuizModel.find_by_id(current_app.db, quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404
    return jsonify(QuizModel.to_public(quiz, include_answers=False)), 200


@quiz_bp.post("/<quiz_id>/submit")
@require_auth
def submit_quiz(quiz_id):
    """
    Submit answers and receive score.
    Body: { answers: [0, 2, 1, ...] }  (0-based index for each question)
    """
    user_id = get_jwt_identity()
    quiz = QuizModel.find_by_id(current_app.db, quiz_id)
    if not quiz:
        return jsonify({"error": "Quiz not found"}), 404

    data = request.get_json(silent=True) or {}
    answers = data.get("answers", [])
    questions = quiz["questions"]

    if len(answers) != len(questions):
        return jsonify({"error": "Answer count does not match question count"}), 400

    results = []
    correct = 0
    for i, (q, ans) in enumerate(zip(questions, answers)):
        is_correct = ans == q["correct_index"]
        if is_correct:
            correct += 1
        results.append({
            "question": q["question"],
            "selected": ans,
            "correct_index": q["correct_index"],
            "correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    score_pct = round((correct / len(questions)) * 100, 1) if questions else 0
    passed = score_pct >= quiz["pass_score"]

    QuizModel.add_attempt(current_app.db, quiz_id, user_id, score_pct)

    return jsonify({
        "score": score_pct,
        "correct": correct,
        "total": len(questions),
        "passed": passed,
        "pass_threshold": quiz["pass_score"],
        "results": results,
    }), 200


@quiz_bp.get("/summary/<summary_id>")
@require_auth
def list_quizzes(summary_id):
    user_id = get_jwt_identity()
    summary = SummaryModel.find_by_id(current_app.db, summary_id)
    if not summary:
        return jsonify({"error": "Summary not found"}), 404

    doc = DocumentModel.find_by_id(current_app.db, str(summary["doc_id"]))
    if not doc or str(doc["user_id"]) != user_id:
        return jsonify({"error": "Access denied"}), 403

    quizzes = QuizModel.find_by_summary(current_app.db, summary_id)
    return jsonify([QuizModel.to_public(q) for q in quizzes]), 200
