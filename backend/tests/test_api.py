"""Comprehensive test suite for the Adaptive Quiz backend.

Run with:  backend\\venv\\Scripts\\python -m pytest backend/tests/test_api.py -v
"""

import os
import sys
import json
import pytest

# Ensure project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.app import create_app
from backend.database import db as _db
from backend.config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


@pytest.fixture(scope="module")
def app():
    app = create_app(TestConfig)
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    return app.test_client()


@pytest.fixture(scope="module")
def auth_header(client):
    """Register a dedicated test user, login, and return an Authorization header."""
    client.post("/auth/register", json={
        "email": "fixture@test.com", "password": "fixturepass", "name": "Tester"
    })
    resp = client.post("/auth/login", json={"email": "fixture@test.com", "password": "fixturepass"})
    data = resp.get_json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ── Auth tests ──────────────────────────────────────────────────

class TestAuth:
    def test_register(self, client):
        resp = client.post("/auth/register", json={
            "email": "new@test.com", "password": "pw", "name": "New"
        })
        assert resp.status_code == 201
        assert resp.get_json()["user"]["email"] == "new@test.com"

    def test_duplicate_register(self, client):
        # "new@test.com" was already registered above
        resp = client.post("/auth/register", json={"email": "new@test.com", "password": "pw"})
        assert resp.status_code == 400

    def test_login_success(self, client):
        resp = client.post("/auth/login", json={"email": "new@test.com", "password": "pw"})
        assert resp.status_code == 200
        assert "access_token" in resp.get_json()

    def test_login_fail(self, client):
        resp = client.post("/auth/login", json={"email": "new@test.com", "password": "wrong"})
        assert resp.status_code == 401

    def test_profile_get(self, client, auth_header):
        resp = client.get("/auth/profile", headers=auth_header)
        assert resp.status_code == 200
        assert resp.get_json()["user"]["name"] == "Tester"

    def test_profile_update(self, client, auth_header):
        resp = client.put("/auth/profile", headers=auth_header, json={"name": "Updated"})
        assert resp.status_code == 200
        assert resp.get_json()["user"]["name"] == "Updated"


# ── Content tests ───────────────────────────────────────────────

SAMPLE_TEXT = """
Machine learning is a subset of artificial intelligence. It focuses on building systems that learn
from data. Supervised learning uses labeled data to train models. Unsupervised learning finds
patterns in unlabeled data. Deep learning uses neural networks with many layers. Natural language
processing enables computers to understand human language. Computer vision allows machines to
interpret visual information from the world. Reinforcement learning trains agents through rewards
and penalties.
"""


class TestContent:
    def test_upload_text(self, client, auth_header):
        resp = client.post("/content/upload/text", headers=auth_header, json={
            "title": "ML Basics", "text": SAMPLE_TEXT
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["content"]["chunk_count"] > 0

    def test_list_content(self, client, auth_header):
        resp = client.get("/content/list", headers=auth_header)
        assert resp.status_code == 200
        assert len(resp.get_json()["contents"]) >= 1

    def test_get_content(self, client, auth_header):
        resp = client.get("/content/1", headers=auth_header)
        assert resp.status_code == 200
        assert "chunks" in resp.get_json()["content"]


# ── Quiz tests ──────────────────────────────────────────────────

class TestQuiz:
    def test_generate_quiz(self, client, auth_header):
        resp = client.post("/quiz/generate", headers=auth_header, json={
            "content_id": 1, "num_questions": 5, "difficulty": "medium"
        })
        assert resp.status_code in (200, 201)
        data = resp.get_json()
        if data.get("questions"):
            assert len(data["questions"]) > 0
            # Store attempt_id for submit test
            TestQuiz._attempt_id = data["attempt_id"]
            TestQuiz._questions = data["questions"]

    def test_submit_quiz(self, client, auth_header):
        if not hasattr(TestQuiz, "_questions") or not TestQuiz._questions:
            pytest.skip("No questions generated")
        answers = [
            {"question_id": q["id"], "answer": "test", "time_spent_seconds": 2.5}
            for q in TestQuiz._questions
        ]
        resp = client.post("/quiz/submit", headers=auth_header, json={
            "attempt_id": TestQuiz._attempt_id, "answers": answers
        })
        assert resp.status_code == 200
        assert "results" in resp.get_json()

    def test_quiz_history(self, client, auth_header):
        resp = client.get("/quiz/history", headers=auth_header)
        assert resp.status_code == 200

    def test_recommendation(self, client, auth_header):
        resp = client.get("/quiz/recommend", headers=auth_header)
        assert resp.status_code == 200
        assert "recommended_difficulty" in resp.get_json()


# ── Admin tests ─────────────────────────────────────────────────

class TestAdmin:
    def test_admin_requires_admin(self, client, auth_header):
        resp = client.get("/admin/stats", headers=auth_header)
        assert resp.status_code == 403

    def test_flag_question(self, client, auth_header):
        if not hasattr(TestQuiz, "_questions") or not TestQuiz._questions:
            pytest.skip("No questions")
        qid = TestQuiz._questions[0]["id"]
        resp = client.post(f"/admin/questions/{qid}/flag", headers=auth_header)
        assert resp.status_code == 200

    def test_submit_feedback(self, client, auth_header):
        if not hasattr(TestQuiz, "_questions") or not TestQuiz._questions:
            pytest.skip("No questions")
        qid = TestQuiz._questions[0]["id"]
        resp = client.post("/admin/feedback", headers=auth_header, json={
            "question_id": qid, "rating": 4, "comment": "Good question!"
        })
        assert resp.status_code == 201
