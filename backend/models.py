from datetime import datetime
from .database import db
import json


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(255), nullable=True)
    preferred_difficulty = db.Column(db.String(50), default="medium")
    subjects_json = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_subjects(self, subjects_list):
        self.subjects_json = json.dumps(subjects_list)

    def get_subjects(self):
        if not self.subjects_json:
            return []
        try:
            return json.loads(self.subjects_json)
        except Exception:
            return []

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "preferred_difficulty": self.preferred_difficulty,
            "subjects": self.get_subjects(),
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat(),
        }


class Content(db.Model):
    __tablename__ = "contents"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    source_type = db.Column(db.String(50))  # text, url, pdf
    raw_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    chunks = db.relationship("ContentChunk", backref="content", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "source_type": self.source_type,
            "chunk_count": len(self.chunks),
            "created_at": self.created_at.isoformat(),
        }


class ContentChunk(db.Model):
    __tablename__ = "content_chunks"
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("contents.id"), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    chunk_index = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id,
            "content_id": self.content_id,
            "chunk_text": self.chunk_text,
            "chunk_index": self.chunk_index,
        }


class Question(db.Model):
    __tablename__ = "questions"
    id = db.Column(db.Integer, primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey("contents.id"), nullable=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50), nullable=False)  # mcq, fill_blank, true_false, short_answer
    correct_answer = db.Column(db.Text, nullable=False)
    options_json = db.Column(db.Text, nullable=True)  # JSON list for MCQ options
    difficulty = db.Column(db.String(50), default="medium")  # easy, medium, hard
    explanation = db.Column(db.Text, nullable=True)
    is_flagged = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_options(self):
        if not self.options_json:
            return []
        try:
            return json.loads(self.options_json)
        except Exception:
            return []

    def set_options(self, options_list):
        self.options_json = json.dumps(options_list)

    def to_dict(self, include_answer=False):
        d = {
            "id": self.id,
            "content_id": self.content_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "options": self.get_options(),
            "difficulty": self.difficulty,
        }
        if include_answer:
            d["correct_answer"] = self.correct_answer
            d["explanation"] = self.explanation
        return d


class QuizAttempt(db.Model):
    __tablename__ = "quiz_attempts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey("contents.id"), nullable=True)
    difficulty = db.Column(db.String(50), default="medium")
    total_questions = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    score_percent = db.Column(db.Float, default=0.0)
    time_taken_seconds = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    responses = db.relationship("QuizResponse", backref="attempt", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content_id": self.content_id,
            "difficulty": self.difficulty,
            "total_questions": self.total_questions,
            "correct_count": self.correct_count,
            "score_percent": self.score_percent,
            "time_taken_seconds": self.time_taken_seconds,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class QuizResponse(db.Model):
    __tablename__ = "quiz_responses"
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey("quiz_attempts.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    user_answer = db.Column(db.Text, nullable=True)
    is_correct = db.Column(db.Boolean, default=False)
    time_spent_seconds = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "attempt_id": self.attempt_id,
            "question_id": self.question_id,
            "user_answer": self.user_answer,
            "is_correct": self.is_correct,
            "time_spent_seconds": self.time_spent_seconds,
        }


class Feedback(db.Model):
    __tablename__ = "feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id"), nullable=False)
    rating = db.Column(db.Integer, default=0)  # 1-5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "question_id": self.question_id,
            "rating": self.rating,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
        }
