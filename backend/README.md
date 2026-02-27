# Adaptive Quiz Backend (Auth)

This folder contains a minimal Flask backend implementing user authentication (registration, login, profile) using JWT and SQLite.

Quick start (Windows cmd.exe):

1. Create and activate a virtual environment (recommended):

   python -m venv venv
   venv\Scripts\activate

2. Install dependencies:

   pip install -r requirements.txt

3. Run the app:

   set FLASK_APP=backend.app
   set FLASK_ENV=development
   flask run

Endpoints:
- POST /auth/register  {email, password, name?, preferred_difficulty?, subjects?}
- POST /auth/login     {email, password}
- GET/PUT /auth/profile (requires Bearer access token)
