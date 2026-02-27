"""AdaptiveQuiz — Main Flask Application."""
import os
import json
import tempfile

from flask import Flask
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv

from backend.models import db, User

load_dotenv()


def create_app():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "frontend", "templates"),
        static_folder=os.path.join(base_dir, "frontend", "static"),
    )

    # ── Configuration ────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "adaptive-quiz-dev-key-2026")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Database — use /tmp on Vercel (read-only filesystem)
    if os.environ.get("VERCEL"):
        db_path = os.path.join(tempfile.gettempdir(), "adaptive_quiz.db")
    else:
        db_path = os.path.join(os.path.dirname(__file__), "adaptive_quiz.db")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", f"sqlite:///{db_path}"
    )

    # Uploads
    app.config["UPLOAD_FOLDER"] = "/tmp/uploads"
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

    # ── Extensions ───────────────────────────────────────────────
    CORS(app)
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "routes.login"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # JSON filter for templates
    @app.template_filter("from_json")
    def from_json_filter(value):
        try:
            return json.loads(value)
        except (ValueError, TypeError):
            return {}

    # ── Blueprints ───────────────────────────────────────────────
    from backend.routes import routes_bp
    app.register_blueprint(routes_bp)

    # ── Create tables ────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app


# Create the app instance (Vercel uses this)
app = create_app()


# For running directly
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
