import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

mongo_client = None
db = None
jwt = JWTManager()


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 86400))
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 20971520))
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")

    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    CORS(app, resources={r"/api/*": {"origins": os.getenv("FRONTEND_URL", "http://localhost:3000")}})
    jwt.init_app(app)

    global mongo_client, db
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017/academic_notes_db")

    if "<username>" in mongo_uri or "<password>" in mongo_uri or mongo_uri.endswith("cluster.mongodb.net/academic_notes_db?retryWrites=true&w=majority"):
        raise RuntimeError(
            "\n\n[CONFIG ERROR] MONGO_URI in your .env still contains placeholder values.\n"
            "Please update backend/.env with a real MongoDB connection string.\n\n"
            "Options:\n"
            "  A) MongoDB Atlas (cloud): https://www.mongodb.com/atlas  → free tier → get SRV URI\n"
            "  B) Local MongoDB:  set MONGO_URI=mongodb://localhost:27017/academic_notes_db\n"
        )

    try:
        mongo_client = MongoClient(mongo_uri, serverSelectionTimeoutMS=8000)
        db_name = mongo_uri.split("/")[-1].split("?")[0] if "/" in mongo_uri else "academic_notes_db"
        db = mongo_client[db_name]
        # Force a connection check so we fail fast with a clear message
        mongo_client.admin.command("ping")
        app.db = db
    except Exception as exc:
        raise RuntimeError(
            f"\n\n[DB ERROR] Could not connect to MongoDB: {exc}\n\n"
            "Check that:\n"
            "  • MONGO_URI in backend/.env is correct\n"
            "  • Your IP is whitelisted in Atlas (Network Access → Add IP)\n"
            "  • Local MongoDB is running if using mongodb://localhost\n"
        ) from exc

    db["users"].create_index("email", unique=True)
    db["documents"].create_index("user_id")
    db["summaries"].create_index("doc_id")
    db["quizzes"].create_index("summary_id")

    from app.routes.auth import auth_bp
    from app.routes.documents import docs_bp
    from app.routes.processing import processing_bp
    from app.routes.quiz import quiz_bp
    from app.routes.admin import admin_bp
    from app.routes.export import export_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(docs_bp, url_prefix="/api/documents")
    app.register_blueprint(processing_bp, url_prefix="/api/process")
    app.register_blueprint(quiz_bp, url_prefix="/api/quiz")
    app.register_blueprint(admin_bp, url_prefix="/api/admin")
    app.register_blueprint(export_bp, url_prefix="/api/export")

    @app.route("/api/health")
    def health():
        return {"status": "ok", "message": "Note Simplifier API running"}

    return app
