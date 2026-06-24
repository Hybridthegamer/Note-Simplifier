from datetime import datetime, timezone
from bson import ObjectId


class DocumentModel:
    COLLECTION = "documents"

    @staticmethod
    def create(db, user_id: str, original_filename: str, file_type: str,
               raw_text: str, file_size_kb: float) -> dict:
        doc = {
            "user_id": ObjectId(user_id),
            "original_filename": original_filename,
            "file_type": file_type,
            "raw_text": raw_text,
            "upload_date": datetime.now(timezone.utc),
            "file_size_kb": file_size_kb,
            "status": "uploaded",
        }
        result = db[DocumentModel.COLLECTION].insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    @staticmethod
    def find_by_id(db, doc_id: str) -> dict | None:
        try:
            return db[DocumentModel.COLLECTION].find_one({"_id": ObjectId(doc_id)})
        except Exception:
            return None

    @staticmethod
    def find_by_user(db, user_id: str) -> list:
        docs = db[DocumentModel.COLLECTION].find(
            {"user_id": ObjectId(user_id)},
            {"raw_text": 0}
        ).sort("upload_date", -1)
        return list(docs)

    @staticmethod
    def update_status(db, doc_id: str, status: str):
        db[DocumentModel.COLLECTION].update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": {"status": status}}
        )

    @staticmethod
    def delete(db, doc_id: str):
        db[DocumentModel.COLLECTION].delete_one({"_id": ObjectId(doc_id)})
        db["summaries"].delete_many({"doc_id": ObjectId(doc_id)})

    @staticmethod
    def to_public(doc: dict) -> dict:
        return {
            "id": str(doc["_id"]),
            "user_id": str(doc["user_id"]),
            "original_filename": doc["original_filename"],
            "file_type": doc["file_type"],
            "file_size_kb": doc.get("file_size_kb", 0),
            "upload_date": doc["upload_date"].isoformat() if doc.get("upload_date") else None,
            "status": doc.get("status", "uploaded"),
        }
