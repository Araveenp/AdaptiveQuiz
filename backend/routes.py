"""Flask routes for AdaptiveQuiz — all application endpoints."""
import json
import os
from datetime import datetime, timedelta, date

from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, session, jsonify,
)
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import or_

from backend.models import User, Question, QuizResult, TopicMastery, MistakeBank, db
from backend.ai_engine import AIEngine
from backend.services import extract_text_from_pdf, extract_text_from_image, clean_text

routes_bp = Blueprint("routes", __name__)

# Initialize AI engine (lazy — key resolved at first use)
ai = AIEngine()


def is_allowed():
    """Check if user is logged in or guest."""
    return current_user.is_authenticated or session.get("is_guest")


# ═══════════════════════════════════════════════════════════════════
# HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/health")
def health_check():
    key = os.getenv("GROQ_API_KEY", "")
    return jsonify({
        "status": "ok",
        "groq_key_set": bool(key),
        "groq_key_preview": f"...{key[-6:]}" if len(key) > 6 else "NOT SET",
        "ai_client_ready": ai.client is not None,
    })


# ═══════════════════════════════════════════════════════════════════
# LANDING & AUTH
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/")
def index():
    return render_template("landing.html")


@routes_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("routes.dashboard"))

    if request.method == "POST":
        login_id = request.form.get("login_id", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter(
            or_(User.email == login_id, User.username == login_id)
        ).first()

        if user and user.check_password(password):
            login_user(user)
            session["is_guest"] = False
            return redirect(url_for("routes.dashboard"))

        flash("Invalid credentials. Please try again.", "danger")
    return render_template("login.html")


@routes_bp.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return redirect(url_for("routes.signup"))

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return redirect(url_for("routes.signup"))

        existing = User.query.filter(
            or_(User.email == email, User.username == username)
        ).first()
        if existing:
            flash("Username or email already taken!", "danger")
            return redirect(url_for("routes.signup"))

        new_user = User(email=email, username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for("routes.login"))

    return render_template("signup.html")


@routes_bp.route("/guest-login")
def guest_login():
    session.clear()
    session["is_guest"] = True
    session["username"] = "Guest Explorer"
    session["streak"] = 0
    flash("Welcome, Guest! Your progress won't be saved.", "info")
    return redirect(url_for("routes.dashboard"))


@routes_bp.route("/logout")
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("routes.login"))


# ═══════════════════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/dashboard")
def dashboard():
    if not is_allowed():
        return redirect(url_for("routes.login"))

    is_guest = session.get("is_guest", False)
    username = session.get("username", "Guest")
    correct_total = 0
    total_q = 0
    mistake_count = 0
    user_streak = 0
    mastery_data = []

    if not is_guest and current_user.is_authenticated:
        username = current_user.username
        results_list = QuizResult.query.filter_by(user_id=current_user.id).all()
        correct_total = sum(r.score for r in results_list)
        total_q = sum(r.total_questions for r in results_list)
        mistake_count = MistakeBank.query.filter_by(user_id=current_user.id).count()
        user_streak = current_user.streak or 0
        mastery_data = TopicMastery.query.filter_by(user_id=current_user.id).all()

    try:
        fun_fact = ai.get_fun_fact()
    except Exception:
        fun_fact = "Learning is a superpower — keep going! 🚀"

    return render_template(
        "dashboard.html",
        username=username,
        is_guest=is_guest,
        correct_total=correct_total,
        incorrect_total=max(0, total_q - correct_total),
        mistake_count=mistake_count,
        streak=user_streak,
        fun_fact=fun_fact,
        topic_mastery=mastery_data,
        total_quizzes=len(QuizResult.query.filter_by(
            user_id=current_user.id).all()) if not is_guest and current_user.is_authenticated else 0,
    )


# ═══════════════════════════════════════════════════════════════════
# STUDY HUB
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/study-hub", methods=["GET", "POST"])
def study_hub():
    if not is_allowed():
        return redirect(url_for("routes.login"))

    if request.method == "POST":
        source_type = request.form.get("source_type")
        content = ""

        try:
            if source_type == "pdf":
                f = request.files.get("pdf_file")
                if f:
                    content = extract_text_from_pdf(f)
            elif source_type == "text":
                content = request.form.get("raw_text", "")
            elif source_type == "topic":
                topic = request.form.get("topic_name", "")
                content = f"Comprehensive overview of: {topic}"
            elif source_type == "image":
                f = request.files.get("image_file")
                if f:
                    content = extract_text_from_image(f)

            content = clean_text(content)
            if not content:
                flash("No content could be extracted. Please try again.", "warning")
                return redirect(url_for("routes.study_hub"))

            study_material = ai.generate_study_material(content)
            session["study_content"] = content
            return render_template(
                "study_hub_result.html",
                material=study_material,
                source_type=source_type,
            )
        except Exception as e:
            print(f"Study Hub error: {e}")
            flash("An error occurred while generating study material.", "danger")

    return render_template("study_hub.html")


# ═══════════════════════════════════════════════════════════════════
# QUIZ GENERATION & PLAY
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/generate", methods=["POST", "GET"])
def handle_generation():
    if not is_allowed():
        return redirect(url_for("routes.login"))

    source_type = request.form.get("source_type") or request.args.get("source_type")
    count = int(request.form.get("count", 5))
    q_format = request.form.get("q_format", "mcq")
    difficulty = request.form.get("difficulty", "medium")
    mastery_label = "General"
    q_ids = []

    try:
        content = ""
        if source_type == "mistake":
            # Re-quiz from mistake bank
            if session.get("is_guest"):
                flash("Guest users don't have a Mistake Bank!", "warning")
                return redirect(url_for("routes.dashboard"))
            mistakes = MistakeBank.query.filter_by(user_id=current_user.id).limit(count).all()
            if not mistakes:
                flash("Your Mistake Bank is empty! 🎉", "info")
                return redirect(url_for("routes.dashboard"))
            for m in mistakes:
                new_q = Question(
                    question_text=m.question_text,
                    options_json=m.options_json,
                    correct_answer=m.correct_answer,
                    explanation=m.explanation,
                    user_id=current_user.id if current_user.is_authenticated else None,
                    topic=m.topic,
                )
                db.session.add(new_q)
                db.session.flush()
                q_ids.append(new_q.id)
            db.session.commit()
            mastery_label = "Mistake Review"
        else:
            if source_type == "pdf":
                f = request.files.get("pdf_file")
                if f and f.filename:
                    content = extract_text_from_pdf(f)
                    mastery_label = f"PDF: {f.filename}"
            elif source_type == "text":
                content = request.form.get("raw_text", "")
                mastery_label = "Custom Text"
            elif source_type == "topic":
                mastery_label = request.form.get("topic_name", "General")
                content = f"Generate questions about: {mastery_label}"
            elif source_type == "image":
                f = request.files.get("image_file")
                if f and f.filename:
                    content = extract_text_from_image(f)
                    mastery_label = f"Image: {f.filename}"

            content = clean_text(content)
            if not content:
                flash("No content to generate questions from!", "danger")
                return redirect(url_for("routes.dashboard"))

            # AI-detected topic if possible
            detected = ai.detect_topic(content)
            if detected and detected != "General Study":
                mastery_label = detected

            questions = ai.generate_questions(content, count, q_format, difficulty)
            if not questions:
                flash("AI couldn't generate questions. Try different content.", "danger")
                return redirect(url_for("routes.dashboard"))

            for q_data in questions:
                new_q = Question(
                    question_text=q_data.get("question", ""),
                    options_json=json.dumps(q_data.get("options", {})),
                    correct_answer=q_data.get("correct_answer", ""),
                    explanation=q_data.get("explanation", ""),
                    difficulty=difficulty,
                    q_type=q_format,
                    user_id=current_user.id if current_user.is_authenticated else None,
                    topic=mastery_label,
                )
                db.session.add(new_q)
                db.session.flush()
                q_ids.append(new_q.id)
            db.session.commit()

        if not q_ids:
            flash("No questions generated.", "warning")
            return redirect(url_for("routes.dashboard"))

        # Store quiz session
        session.update({
            "active_questions": q_ids,
            "current_idx": 0,
            "score": 0,
            "quiz_topic": mastery_label,
            "quiz_difficulty": difficulty,
            "user_answers": [],
        })
        return redirect(url_for("routes.quiz_page", q_id=q_ids[0]))

    except Exception as e:
        db.session.rollback()
        print(f"Generation error: {e}")
        flash(f"Error generating quiz: {str(e)}", "danger")
        return redirect(url_for("routes.dashboard"))


@routes_bp.route("/quiz/<int:q_id>")
def quiz_page(q_id):
    if not is_allowed():
        return redirect(url_for("routes.login"))

    question = Question.query.get_or_404(q_id)
    options = json.loads(question.options_json) if question.options_json else {}
    q_list = session.get("active_questions", [])
    current = session.get("current_idx", 0)

    return render_template(
        "quiz.html",
        question=question,
        options=options,
        current=current + 1,
        total=len(q_list),
        topic=session.get("quiz_topic", "Quiz"),
    )


@routes_bp.route("/submit-answer", methods=["POST"])
def submit_answer():
    if not is_allowed():
        return redirect(url_for("routes.login"))

    q_id = int(request.form.get("question_id"))
    user_answer = request.form.get("answer", "")
    question = Question.query.get_or_404(q_id)

    is_correct = user_answer.strip().upper() == question.correct_answer.strip().upper()

    # Save answer
    ans_list = session.get("user_answers", [])
    ans_list.append({
        "question": question.question_text,
        "user_answer": user_answer,
        "correct_answer": question.correct_answer,
        "is_correct": is_correct,
        "explanation": question.explanation,
        "options": json.loads(question.options_json) if question.options_json else {},
    })
    session["user_answers"] = ans_list

    if is_correct:
        session["score"] = session.get("score", 0) + 1
    elif not session.get("is_guest") and current_user.is_authenticated:
        # Add to mistake bank
        mistake = MistakeBank(
            user_id=current_user.id,
            question_text=question.question_text,
            correct_answer=question.correct_answer,
            options_json=question.options_json,
            topic=session.get("quiz_topic", "General"),
            explanation=question.explanation,
        )
        db.session.add(mistake)
        db.session.commit()

    # Next question or results
    session["current_idx"] = session.get("current_idx", 0) + 1
    q_list = session.get("active_questions", [])

    if session["current_idx"] < len(q_list):
        return redirect(url_for("routes.quiz_page", q_id=q_list[session["current_idx"]]))
    return redirect(url_for("routes.results"))


# ═══════════════════════════════════════════════════════════════════
# RESULTS
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/results")
def results():
    score = session.get("score", 0)
    user_answers = session.get("user_answers", [])
    total = len(user_answers)
    topic = session.get("quiz_topic", "Quiz")
    difficulty = session.get("quiz_difficulty", "medium")
    accuracy = (score / total * 100) if total > 0 else 0

    history_labels = []
    history_scores = []
    is_guest = session.get("is_guest", False)
    ai_insight = ""

    try:
        if not is_guest and current_user.is_authenticated:
            # Save result
            new_res = QuizResult(
                user_id=current_user.id,
                score=score,
                total_questions=total,
                topic=topic,
                difficulty=difficulty,
                timestamp=datetime.utcnow(),
            )
            db.session.add(new_res)

            # Update streak
            today = date.today()
            if current_user.last_quiz_date:
                last = current_user.last_quiz_date
                if last == today:
                    pass  # same day
                elif last == today - timedelta(days=1):
                    current_user.streak += 1
                else:
                    current_user.streak = 1
            else:
                current_user.streak = 1
            current_user.last_quiz_date = today

            # Update topic mastery
            mastery = TopicMastery.query.filter_by(
                user_id=current_user.id, topic=topic
            ).first()
            if not mastery:
                mastery = TopicMastery(
                    user_id=current_user.id, topic=topic,
                    correct_count=0, total_count=0,
                )
                db.session.add(mastery)
            mastery.correct_count += score
            mastery.total_count += total
            db.session.commit()

            # History for chart
            past = QuizResult.query.filter_by(
                user_id=current_user.id
            ).order_by(QuizResult.timestamp.asc()).all()
            for r in past[-7:]:
                history_labels.append(r.timestamp.strftime("%d %b"))
                history_scores.append(
                    int(r.score / r.total_questions * 100) if r.total_questions else 0
                )

            # AI insight on mistakes
            wrong = [a for a in user_answers if not a["is_correct"]]
            if wrong:
                ai_insight = ai.generate_performance_insight(wrong, topic)
        else:
            history_labels = ["Now"]
            history_scores = [int(accuracy)]

    except Exception as e:
        db.session.rollback()
        print(f"Results save error: {e}")

    return render_template(
        "results.html",
        score=score,
        total=total,
        accuracy=accuracy,
        user_answers=user_answers,
        is_guest=is_guest,
        topic=topic,
        history_labels=json.dumps(history_labels),
        history_scores=json.dumps(history_scores),
        ai_insight=ai_insight,
    )


# ═══════════════════════════════════════════════════════════════════
# LIBRARY & MISTAKES
# ═══════════════════════════════════════════════════════════════════

@routes_bp.route("/library")
@login_required
def library():
    if session.get("is_guest"):
        flash("Library is for registered users only!", "info")
        return redirect(url_for("routes.signup"))

    results = QuizResult.query.filter_by(
        user_id=current_user.id
    ).order_by(QuizResult.timestamp.desc()).all()
    return render_template("library.html", results=results)


@routes_bp.route("/review-mistakes")
@login_required
def review_mistakes():
    mistakes = MistakeBank.query.filter_by(user_id=current_user.id).all()
    processed = []
    for m in mistakes:
        processed.append({
            "id": m.id,
            "question": m.question_text,
            "correct_answer": m.correct_answer,
            "options": json.loads(m.options_json) if m.options_json else {},
            "topic": m.topic,
            "explanation": m.explanation,
        })
    return render_template("review.html", mistakes=processed)


@routes_bp.route("/delete-mistake/<int:m_id>", methods=["POST"])
@login_required
def delete_mistake(m_id):
    m = MistakeBank.query.get_or_404(m_id)
    if m.user_id == current_user.id:
        db.session.delete(m)
        db.session.commit()
        flash("Mistake removed!", "success")
    return redirect(url_for("routes.review_mistakes"))
