# 🧠 Adaptive Quiz & Question Generator

An open-source, full-stack adaptive quiz platform that generates personalized quizzes from any educational content using NLP. Built with **Flask** (Python) backend and **React** frontend.

---

## 📋 Features

| Module | Description |
|--------|-------------|
| **User & Profile Management** | Registration, JWT login, profile with difficulty preferences & subjects |
| **Content Ingestion** | Upload text, URLs, or PDFs → auto-chunked into knowledge segments |
| **Question Generator Engine** | NLP-based generation of MCQ, Fill-in-the-blank, True/False, Short Answer |
| **Adaptive Learning Engine** | Tracks performance history, adjusts difficulty automatically |
| **Quiz Interface** | Interactive quiz UI with live scoring, progress tracking, result review |
| **Admin Dashboard** | User analytics, question moderation, flagging, feedback collection |
| **Dockerized Deployment** | Ready for cloud hosting with Docker Compose |

---

## 🏗️ Architecture

```
┌─────────────────┐     HTTP/JSON      ┌──────────────────────────┐
│   React Frontend │ ◄──────────────► │     Flask REST API         │
│   (port 3000)    │                   │     (port 5000)            │
└─────────────────┘                   ├──────────────────────────┤
                                       │  Auth Blueprint (/auth)   │
                                       │  Content Blueprint        │
                                       │  Quiz Blueprint (/quiz)   │
                                       │  Admin Blueprint (/admin) │
                                       ├──────────────────────────┤
                                       │  Question Generator (NLP) │
                                       │  Adaptive Engine          │
                                       ├──────────────────────────┤
                                       │  SQLite / PostgreSQL      │
                                       └──────────────────────────┘
```

---

## 📂 Project Structure

```
AdaptiveQuiz/
├── backend/
│   ├── app.py              # Flask app factory
│   ├── config.py           # Configuration
│   ├── database.py         # SQLAlchemy setup
│   ├── models.py           # DB models (User, Content, Question, etc.)
│   ├── auth.py             # Auth endpoints (register, login, profile)
│   ├── content.py          # Content ingestion (text, URL, PDF)
│   ├── quiz.py             # Quiz generation, submission, adaptive logic
│   ├── admin.py            # Admin dashboard endpoints
│   ├── generator.py        # NLP question generator engine
│   ├── utils.py            # Password hashing utilities
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Backend Docker image
│   └── tests/
│       └── test_api.py     # Comprehensive API tests
├── frontend/
│   ├── public/index.html
│   ├── src/
│   │   ├── App.js          # Main app with routing
│   │   ├── api.js          # API client (axios)
│   │   ├── App.css         # Global styles
│   │   └── pages/
│   │       ├── Login.js
│   │       ├── Register.js
│   │       ├── Profile.js
│   │       ├── ContentUpload.js
│   │       ├── ContentList.js
│   │       ├── QuizSetup.js
│   │       ├── QuizPlay.js
│   │       ├── QuizHistory.js
│   │       └── AdminPanel.js
│   ├── package.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

Start the server:
```bash
# From the project root (AdaptiveQuiz/)
python -m backend.app
```
Backend runs at **http://127.0.0.1:5000**

### Frontend

```bash
cd frontend
npm install
npm start
```
Frontend runs at **http://localhost:3000** and proxies API requests to the backend.

---

## 🐳 Docker Deployment

```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

---

## 📡 API Reference

### Auth (`/auth`)
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | `{email, password, name?, preferred_difficulty?, subjects?}` | Register a new user |
| POST | `/auth/login` | `{email, password}` | Login, returns JWT token |
| GET | `/auth/profile` | — | Get user profile (🔒 JWT) |
| PUT | `/auth/profile` | `{name?, preferred_difficulty?, subjects?}` | Update profile (🔒 JWT) |

### Content (`/content`)
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/content/upload/text` | `{title, text}` | Upload raw text (🔒 JWT) |
| POST | `/content/upload/url` | `{title?, url}` | Fetch & parse a URL (🔒 JWT) |
| POST | `/content/upload/pdf` | `multipart: file, title?` | Upload a PDF file (🔒 JWT) |
| GET | `/content/list` | — | List user's content (🔒 JWT) |
| GET | `/content/<id>` | — | Get content + chunks (🔒 JWT) |
| DELETE | `/content/<id>` | — | Delete content (🔒 JWT) |

### Quiz (`/quiz`)
| Method | Endpoint | Body | Description |
|--------|----------|------|-------------|
| POST | `/quiz/generate` | `{content_id, num_questions?, difficulty?, types?}` | Generate quiz (🔒 JWT) |
| POST | `/quiz/submit` | `{attempt_id, answers: [{question_id, answer, time_spent_seconds}]}` | Submit answers (🔒 JWT) |
| GET | `/quiz/history` | — | Quiz history (🔒 JWT) |
| GET | `/quiz/attempt/<id>` | — | Attempt details (🔒 JWT) |
| GET | `/quiz/recommend` | — | Get adaptive recommendation (🔒 JWT) |

### Admin (`/admin`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/stats` | Platform statistics (🔒 Admin) |
| GET | `/admin/users` | List all users (🔒 Admin) |
| GET | `/admin/questions?flagged=true` | List/filter questions (🔒 Admin) |
| POST | `/admin/questions/<id>/flag` | Flag a question (🔒 JWT) |
| DELETE | `/admin/questions/<id>` | Delete a question (🔒 Admin) |
| POST | `/admin/feedback` | `{question_id, rating, comment}` — Submit feedback (🔒 JWT) |
| GET | `/admin/feedback` | List all feedback (🔒 Admin) |
| POST | `/admin/promote/<user_id>` | Promote user to admin (🔒 Admin) |

---

## 🧪 Running Tests

```bash
# From project root
backend\venv\Scripts\python -m pytest backend/tests/test_api.py -v
```

---

## 📊 Database Schema

```
users
├── id, email, password_hash, name
├── preferred_difficulty, subjects_json, is_admin
└── created_at

contents
├── id, user_id (FK), title, source_type, raw_text
└── created_at

content_chunks
├── id, content_id (FK), chunk_text, chunk_index

questions
├── id, content_id (FK), question_text, question_type
├── correct_answer, options_json, difficulty
├── explanation, is_flagged
└── created_at

quiz_attempts
├── id, user_id (FK), content_id (FK), difficulty
├── total_questions, correct_count, score_percent
├── time_taken_seconds, started_at, completed_at

quiz_responses
├── id, attempt_id (FK), question_id (FK)
├── user_answer, is_correct, time_spent_seconds

feedback
├── id, user_id (FK), question_id (FK)
├── rating, comment, created_at
```

---

## 🔧 Question Types & Adaptive Logic

### Question Types
1. **MCQ** — Multiple choice with auto-generated distractors
2. **Fill-in-the-blank** — Key noun removed from sentence
3. **True/False** — Statement with random negation
4. **Short Answer** — Open-ended concept questions

### Adaptive Difficulty
- Tracks last 5 quiz scores
- If average ≥ 80%: difficulty increases
- If average < 50%: difficulty decreases
- Otherwise: stays the same
- User's `preferred_difficulty` is auto-updated after each quiz

---

## 📝 License

MIT License — free for academic and personal use.
