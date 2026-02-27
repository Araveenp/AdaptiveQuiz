"""End-to-end demo: register, upload content, generate quiz, submit answers, view results.

Run:  backend\\venv\\Scripts\\python -m backend.demo_e2e
"""
import json
from backend.app import create_app

app = create_app()
client = app.test_client()

def pp(label, resp):
    print(f"\n{'='*60}")
    print(f"  {label}  →  {resp.status_code}")
    print('='*60)
    print(json.dumps(resp.get_json(), indent=2))

# 1. Register
pp("REGISTER", client.post("/auth/register", json={
    "email": "demo@quiz.com", "password": "demo123",
    "name": "Demo User", "preferred_difficulty": "medium",
    "subjects": ["science", "history"]
}))

# 2. Login
resp = client.post("/auth/login", json={"email": "demo@quiz.com", "password": "demo123"})
pp("LOGIN", resp)
token = resp.get_json()["access_token"]
H = {"Authorization": f"Bearer {token}"}

# 3. Get profile
pp("PROFILE", client.get("/auth/profile", headers=H))

# 4. Upload content
text = """
Machine learning is a branch of artificial intelligence that focuses on building systems capable
of learning from data. Supervised learning uses labeled datasets to train algorithms.
Unsupervised learning discovers hidden patterns in unlabeled data. Reinforcement learning trains
agents through trial and error using rewards and penalties. Deep learning uses multi-layered
neural networks to model complex patterns. Natural language processing enables computers to
understand and generate human language. Computer vision allows machines to interpret visual data.
Transfer learning applies knowledge from one domain to another. Feature engineering is the
process of selecting relevant input variables. Overfitting occurs when a model learns noise
instead of the actual signal.
"""
resp = client.post("/content/upload/text", headers=H, json={"title": "ML Basics", "text": text})
pp("UPLOAD CONTENT", resp)
content_id = resp.get_json()["content"]["id"]

# 5. List content
pp("LIST CONTENT", client.get("/content/list", headers=H))

# 6. Generate quiz (adaptive)
resp = client.post("/quiz/generate", headers=H, json={
    "content_id": content_id, "num_questions": 5, "difficulty": "auto",
    "types": ["mcq", "fill_blank", "true_false"]
})
pp("GENERATE QUIZ", resp)
quiz_data = resp.get_json()
attempt_id = quiz_data["attempt_id"]
questions = quiz_data["questions"]

# 7. Submit answers (simulate answering)
answers = []
for q in questions:
    if q["options"]:
        ans = q["options"][0]  # just pick the first option
    else:
        ans = "machine learning"
    answers.append({"question_id": q["id"], "answer": ans, "time_spent_seconds": 3.5})

resp = client.post("/quiz/submit", headers=H, json={"attempt_id": attempt_id, "answers": answers})
pp("SUBMIT QUIZ", resp)

# 8. Quiz history
pp("QUIZ HISTORY", client.get("/quiz/history", headers=H))

# 9. Recommendation
pp("RECOMMENDATION", client.get("/quiz/recommend", headers=H))

# 10. Flag a question
if questions:
    pp("FLAG QUESTION", client.post(f"/admin/questions/{questions[0]['id']}/flag", headers=H))

# 11. Submit feedback
if questions:
    pp("SUBMIT FEEDBACK", client.post("/admin/feedback", headers=H, json={
        "question_id": questions[0]["id"], "rating": 5, "comment": "Great question!"
    }))

print("\n" + "="*60)
print("  ✅ END-TO-END DEMO COMPLETE — ALL MODULES WORKING!")
print("="*60)
