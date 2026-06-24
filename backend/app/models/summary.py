from datetime import datetime, timezone
from bson import ObjectId


class SummaryModel:
    COLLECTION = "summaries"

    @staticmethod
    def create(db, doc_id: str, simplified_text: str, complexity_level: str,
               key_concepts: list, word_count: int) -> dict:
        summary = {
            "doc_id": ObjectId(doc_id),
            "simplified_text": simplified_text,
            "complexity_level": complexity_level,
            "key_concepts": key_concepts,
            "word_count": word_count,
            "created_at": datetime.now(timezone.utc),
        }
        result = db[SummaryModel.COLLECTION].insert_one(summary)
        summary["_id"] = result.inserted_id
        return summary

    @staticmethod
    def find_by_id(db, summary_id: str) -> dict | None:
        try:
            return db[SummaryModel.COLLECTION].find_one({"_id": ObjectId(summary_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_doc(db, doc_id: str) -> list:
        results = db[SummaryModel.COLLECTION].find(
            {"doc_id": ObjectId(doc_id)}
        ).sort("created_at", -1)
        return list(results)

    @staticmethod
    def to_public(summary: dict) -> dict:
        return {
            "id": str(summary["_id"]),
            "doc_id": str(summary["doc_id"]),
            "simplified_text": summary["simplified_text"],
            "complexity_level": summary["complexity_level"],
            "key_concepts": summary.get("key_concepts", []),
            "word_count": summary.get("word_count", 0),
            "created_at": summary["created_at"].isoformat() if summary.get("created_at") else None,
        }
