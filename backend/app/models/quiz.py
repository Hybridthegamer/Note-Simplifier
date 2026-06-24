from datetime import datetime, timezone
from bson import ObjectId


class QuizModel:
    COLLECTION = "quizzes"

    @staticmethod
    def create(db, summary_id: str, questions: list, num_questions: int,
               pass_score: float = 60.0) -> dict:
        quiz = {
            "summary_id": ObjectId(summary_id),
            "questions": questions,
            "num_questions": num_questions,
            "pass_score": pass_score,
            "attempts": [],
            "created_at": datetime.now(timezone.utc),
        }
        result = db[QuizModel.COLLECTION].insert_one(quiz)
        quiz["_id"] = result.inserted_id
        return quiz

    @staticmethod
    def find_by_id(db, quiz_id: str) -> dict | None:
        try:
            return db[QuizModel.COLLECTION].find_one({"_id": ObjectId(quiz_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_summary(db, summary_id: str) -> list:
        results = db[QuizModel.COLLECTION].find(
            {"summary_id": ObjectId(summary_id)}
        ).sort("created_at", -1)
        return list(results)

    @staticmethod
    def add_attempt(db, quiz_id: str, user_id: str, score: float):
        attempt = {
            "user_id": ObjectId(user_id),
            "score": score,
            "timestamp": datetime.now(timezone.utc),
        }
        db[QuizModel.COLLECTION].update_one(
            {"_id": ObjectId(quiz_id)},
            {"$push": {"attempts": attempt}}
        )
        return attempt

    @staticmethod
    def to_public(quiz: dict, include_answers: bool = False) -> dict:
        questions = []
        for q in quiz.get("questions", []):
            question = {
                "question": q["question"],
                "options": q["options"],
            }
            if include_answers:
                question["correct_index"] = q["correct_index"]
                question["explanation"] = q.get("explanation", "")
            questions.append(question)

        attempts = []
        for a in quiz.get("attempts", []):
            attempts.append({
                "user_id": str(a["user_id"]),
                "score": a["score"],
                "timestamp": a["timestamp"].isoformat() if a.get("timestamp") else None,
            })

        return {
            "id": str(quiz["_id"]),
            "summary_id": str(quiz["summary_id"]),
            "questions": questions,
            "num_questions": quiz["num_questions"],
            "pass_score": quiz["pass_score"],
            "attempts": attempts,
            "created_at": quiz["created_at"].isoformat() if quiz.get("created_at") else None,
        }
