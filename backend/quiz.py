"""Quiz blueprint – generate quizzes, submit answers, view results, adaptive logic."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .database import db
from .models import Content, ContentChunk, Question, QuizAttempt, QuizResponse, User
from .generator import generate_questions_from_text

bp = Blueprint("quiz", __name__, url_prefix="/quiz")


# ---------------------------------------------------------------------------
# Adaptive helper
# ---------------------------------------------------------------------------

def _recommended_difficulty(user: User) -> str:
    """Recommend next difficulty based on recent quiz performance."""
    recent = (
        QuizAttempt.query
        .filter_by(user_id=user.id)
        .order_by(QuizAttempt.started_at.desc())
        .limit(5)
        .all()
    )
    if not recent:
        return user.preferred_difficulty or "medium"

    avg_score = sum(a.score_percent for a in recent) / len(recent)
    if avg_score >= 80:
        mapping = {"easy": "medium", "medium": "hard", "hard": "hard"}
    elif avg_score < 50:
        mapping = {"easy": "easy", "medium": "easy", "hard": "medium"}
    else:
        mapping = {"easy": "easy", "medium": "medium", "hard": "hard"}
    current = recent[0].difficulty or user.preferred_difficulty or "medium"
    return mapping.get(current, "medium")


# ---------------------------------------------------------------------------
# endpoints
# ---------------------------------------------------------------------------

@bp.route("/generate", methods=["POST"])
@jwt_required()
def generate_quiz():
    """Generate a new quiz from a content item.

    Body JSON:
      content_id    – required
      num_questions – optional (default 10)
      difficulty    – optional (easy/medium/hard/auto)
      types         – optional list e.g. ["mcq","true_false"]
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    content_id = data.get("content_id")
    num_q = min(data.get("num_questions", 10), 50)
    difficulty = data.get("difficulty", "auto")
    q_types = data.get("types", None)

    if not content_id:
        return jsonify({"msg": "content_id is required"}), 400

    content = Content.query.get_or_404(content_id)

    # Build the full text from chunks
    chunks = ContentChunk.query.filter_by(content_id=content.id).order_by(ContentChunk.chunk_index).all()
    full_text = " ".join(c.chunk_text for c in chunks)
    if not full_text.strip():
        return jsonify({"msg": "content has no text"}), 400

    # Adaptive difficulty
    user = User.query.get(user_id)
    if difficulty == "auto":
        difficulty = _recommended_difficulty(user)

    raw_questions = generate_questions_from_text(
        full_text,
        question_types=q_types,
        difficulty=difficulty if difficulty != "mixed" else None,
        max_questions=num_q,
    )

    if not raw_questions:
        return jsonify({"msg": "could not generate questions from this content", "questions": []}), 200

    # Persist questions
    db_questions = []
    for rq in raw_questions:
        q = Question(
            content_id=content.id,
            question_text=rq["question_text"],
            question_type=rq["question_type"],
            correct_answer=rq["correct_answer"],
            difficulty=rq["difficulty"],
            explanation=rq.get("explanation", ""),
        )
        q.set_options(rq.get("options", []))
        db.session.add(q)
        db.session.flush()
        db_questions.append(q)

    # Create quiz attempt
    attempt = QuizAttempt(
        user_id=user_id,
        content_id=content.id,
        difficulty=difficulty,
        total_questions=len(db_questions),
    )
    db.session.add(attempt)
    db.session.commit()

    return jsonify({
        "attempt_id": attempt.id,
        "difficulty": difficulty,
        "questions": [q.to_dict(include_answer=False) for q in db_questions],
    }), 201


@bp.route("/submit", methods=["POST"])
@jwt_required()
def submit_quiz():
    """Submit answers for a quiz attempt.

    Body JSON:
      attempt_id – required
      answers    – list of {question_id, answer, time_spent_seconds}
    """
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    attempt_id = data.get("attempt_id")
    answers = data.get("answers", [])

    if not attempt_id:
        return jsonify({"msg": "attempt_id is required"}), 400

    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({"msg": "forbidden"}), 403

    correct = 0
    total_time = 0.0
    results = []

    for ans in answers:
        qid = ans.get("question_id")
        user_answer = ans.get("answer", "")
        time_spent = float(ans.get("time_spent_seconds", 0))
        question = Question.query.get(qid)
        if not question:
            continue
        is_correct = user_answer.strip().lower() == question.correct_answer.strip().lower()
        if is_correct:
            correct += 1
        total_time += time_spent
        resp = QuizResponse(
            attempt_id=attempt.id,
            question_id=qid,
            user_answer=user_answer,
            is_correct=is_correct,
            time_spent_seconds=time_spent,
        )
        db.session.add(resp)
        results.append({
            "question_id": qid,
            "your_answer": user_answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "explanation": question.explanation,
        })

    attempt.correct_count = correct
    attempt.score_percent = (correct / attempt.total_questions * 100) if attempt.total_questions else 0
    attempt.time_taken_seconds = total_time
    attempt.completed_at = datetime.utcnow()

    # Update user preferred_difficulty adaptively
    user = User.query.get(user_id)
    user.preferred_difficulty = _recommended_difficulty(user)

    db.session.commit()

    return jsonify({
        "attempt": attempt.to_dict(),
        "results": results,
        "recommended_difficulty": user.preferred_difficulty,
    })


@bp.route("/history", methods=["GET"])
@jwt_required()
def quiz_history():
    """Return the user's quiz history."""
    user_id = int(get_jwt_identity())
    attempts = (
        QuizAttempt.query
        .filter_by(user_id=user_id)
        .order_by(QuizAttempt.started_at.desc())
        .limit(50)
        .all()
    )
    return jsonify({"attempts": [a.to_dict() for a in attempts]})


@bp.route("/attempt/<int:attempt_id>", methods=["GET"])
@jwt_required()
def get_attempt(attempt_id):
    """Return details of a specific quiz attempt including responses."""
    user_id = int(get_jwt_identity())
    attempt = QuizAttempt.query.get_or_404(attempt_id)
    if attempt.user_id != user_id:
        return jsonify({"msg": "forbidden"}), 403
    responses = [r.to_dict() for r in attempt.responses]
    return jsonify({"attempt": attempt.to_dict(), "responses": responses})


@bp.route("/recommend", methods=["GET"])
@jwt_required()
def recommend():
    """Return adaptive recommendation for next quiz session."""
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    diff = _recommended_difficulty(user)
    recent = (
        QuizAttempt.query
        .filter_by(user_id=user_id)
        .order_by(QuizAttempt.started_at.desc())
        .limit(5)
        .all()
    )
    avg = sum(a.score_percent for a in recent) / len(recent) if recent else 0
    return jsonify({
        "recommended_difficulty": diff,
        "recent_average_score": round(avg, 1),
        "total_quizzes_taken": QuizAttempt.query.filter_by(user_id=user_id).count(),
    })
