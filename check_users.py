from main import app
from backend.models import User, db

with app.app_context():
    users = User.query.all()
    if not users:
        print("No users found in database.")
    else:
        for u in users:
            print(f"User: {u.username} ({u.email})")
