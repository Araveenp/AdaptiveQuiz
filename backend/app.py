from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from .config import Config
from .database import init_db
from .auth import bp as auth_bp
from .content import bp as content_bp
from .quiz import bp as quiz_bp
from .admin import bp as admin_bp


def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # extensions
    CORS(app)
    jwt = JWTManager(app)
    init_db(app)

    # blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(quiz_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def index():
        return jsonify({
            "msg": "Adaptive Quiz & Question Generator API",
            "endpoints": {
                "auth": "/auth  (register, login, profile)",
                "content": "/content  (upload text/url/pdf, list, get, delete)",
                "quiz": "/quiz  (generate, submit, history, recommend)",
                "admin": "/admin  (stats, users, questions, feedback, promote)",
            }
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
