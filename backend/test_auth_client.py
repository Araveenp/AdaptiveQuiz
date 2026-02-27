import os
import json
from pathlib import Path

from backend.app import create_app


DB_PATH = Path(__file__).resolve().parent / "adaptive_quiz.db"


def clean_db():
    if DB_PATH.exists():
        try:
            DB_PATH.unlink()
            print("Removed existing DB", DB_PATH)
        except Exception as e:
            print("Could not remove DB:", e)


def run_tests():
    clean_db()
    app = create_app()
    client = app.test_client()

    # Register
    resp = client.post(
        "/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "TestPass123",
            "name": "Test User",
            "preferred_difficulty": "easy",
            "subjects": ["math", "science"],
        },
    )
    print("REGISTER", resp.status_code, resp.get_json())

    # Login
    resp = client.post(
        "/auth/login",
        json={"email": "testuser@example.com", "password": "TestPass123"},
    )
    print("LOGIN", resp.status_code, resp.get_json())
    data = resp.get_json() or {}
    token = data.get("access_token")

    if not token:
        print("No token returned; aborting further tests")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # Get profile
    resp = client.get("/auth/profile", headers=headers)
    print("PROFILE GET", resp.status_code, json.dumps(resp.get_json(), indent=2))

    # Update profile
    resp = client.put(
        "/auth/profile",
        headers=headers,
        json={"preferred_difficulty": "medium", "name": "Updated Name"},
    )
    print("PROFILE PUT", resp.status_code, json.dumps(resp.get_json(), indent=2))


if __name__ == "__main__":
    run_tests()
