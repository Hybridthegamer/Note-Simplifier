from datetime import datetime, timezone
from bson import ObjectId
import bcrypt


class UserModel:
    COLLECTION = "users"

    @staticmethod
    def create(db, full_name: str, email: str, password: str, role: str = "student") -> dict:
        password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        user = {
            "full_name": full_name,
            "email": email.lower().strip(),
            "password_hash": password_hash,
            "role": role,
            "created_at": datetime.now(timezone.utc),
            "last_login": None,
        }
        result = db[UserModel.COLLECTION].insert_one(user)
        user["_id"] = result.inserted_id
        return user

    @staticmethod
    def find_by_email(db, email: str) -> dict | None:
        return db[UserModel.COLLECTION].find_one({"email": email.lower().strip()})

    @staticmethod
    def find_by_id(db, user_id: str) -> dict | None:
        try:
            return db[UserModel.COLLECTION].find_one({"_id": ObjectId(user_id)})
        except Exception:
            return None

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))

    @staticmethod
    def update_last_login(db, user_id: str):
        db[UserModel.COLLECTION].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )

    @staticmethod
    def to_public(user: dict) -> dict:
        return {
            "id": str(user["_id"]),
            "full_name": user["full_name"],
            "email": user["email"],
            "role": user["role"],
            "created_at": user["created_at"].isoformat() if user.get("created_at") else None,
            "last_login": user["last_login"].isoformat() if user.get("last_login") else None,
        }
