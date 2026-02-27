"""Admin blueprint – moderation, analytics, feedback, flagging."""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .database import db
from .models import User, Content, Question, QuizAttempt, Feedback

bp = Blueprint("admin", __name__, url_prefix="/admin")


def _require_admin():
    uid = int(get_jwt_identity())
    user = User.query.get(uid)
    if not user or not user.is_admin:
        return None
    return user


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

@bp.route("/stats", methods=["GET"])
@jwt_required()
def stats():
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    return jsonify({
        "total_users": User.query.count(),
        "total_contents": Content.query.count(),
        "total_questions": Question.query.count(),
        "total_quizzes": QuizAttempt.query.count(),
        "flagged_questions": Question.query.filter_by(is_flagged=True).count(),
    })


@bp.route("/users", methods=["GET"])
@jwt_required()
def list_users():
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify({"users": [u.to_dict() for u in users]})


# ---------------------------------------------------------------------------
# Question moderation
# ---------------------------------------------------------------------------

@bp.route("/questions", methods=["GET"])
@jwt_required()
def list_questions():
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    flagged_only = request.args.get("flagged", "false").lower() == "true"
    q = Question.query
    if flagged_only:
        q = q.filter_by(is_flagged=True)
    questions = q.order_by(Question.created_at.desc()).limit(100).all()
    return jsonify({"questions": [qq.to_dict(include_answer=True) for qq in questions]})


@bp.route("/questions/<int:qid>/flag", methods=["POST"])
@jwt_required()
def flag_question(qid):
    """Any logged-in user can flag a question."""
    question = Question.query.get_or_404(qid)
    question.is_flagged = True
    db.session.commit()
    return jsonify({"msg": "question flagged"})


@bp.route("/questions/<int:qid>", methods=["DELETE"])
@jwt_required()
def delete_question(qid):
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    question = Question.query.get_or_404(qid)
    db.session.delete(question)
    db.session.commit()
    return jsonify({"msg": "question deleted"})


@bp.route("/questions/<int:qid>/unflag", methods=["POST"])
@jwt_required()
def unflag_question(qid):
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    question = Question.query.get_or_404(qid)
    question.is_flagged = False
    db.session.commit()
    return jsonify({"msg": "question unflagged"})


# ---------------------------------------------------------------------------
# Feedback
# ---------------------------------------------------------------------------

@bp.route("/feedback", methods=["POST"])
@jwt_required()
def submit_feedback():
    """Any user can submit feedback on a question."""
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    question_id = data.get("question_id")
    rating = data.get("rating", 3)
    comment = data.get("comment", "")
    if not question_id:
        return jsonify({"msg": "question_id required"}), 400
    fb = Feedback(user_id=user_id, question_id=question_id, rating=rating, comment=comment)
    db.session.add(fb)
    db.session.commit()
    return jsonify({"msg": "feedback submitted", "feedback": fb.to_dict()}), 201


@bp.route("/feedback", methods=["GET"])
@jwt_required()
def list_feedback():
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    items = Feedback.query.order_by(Feedback.created_at.desc()).limit(100).all()
    return jsonify({"feedback": [f.to_dict() for f in items]})


# ---------------------------------------------------------------------------
# Promote / demote admin
# ---------------------------------------------------------------------------

@bp.route("/promote/<int:uid>", methods=["POST"])
@jwt_required()
def promote(uid):
    admin = _require_admin()
    if not admin:
        return jsonify({"msg": "admin access required"}), 403
    user = User.query.get_or_404(uid)
    user.is_admin = True
    db.session.commit()
    return jsonify({"msg": f"{user.email} is now admin"})
