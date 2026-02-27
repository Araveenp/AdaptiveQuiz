# 🧠 AdaptiveQuiz — AI-Powered Adaptive Quiz & Study Platform

An intelligent, AI-powered quiz and study platform that generates personalised questions, study materials, and performance analytics using **Groq LLM (Llama 3.3)**.

Built as a capstone project for the **Infosys Springboard Virtual Internship**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **AI Quiz Generation** | Generate MCQ & True/False questions from topics, raw text, or PDF uploads |
| 📚 **Study Hub** | Get AI-generated shorthand notes, ELI10 explanations, mnemonic stories, key concepts & flashcards |
| 📊 **Adaptive Difficulty** | Questions adapt based on your performance history |
| 🏆 **Streak Tracking** | Daily login streaks and gamification |
| 🔍 **Mistake Bank** | Review wrong answers and re-quiz on weak areas |
| 📈 **Performance Analytics** | Score history charts, topic mastery tracking, AI insights |
| 👤 **Guest Mode** | Try without creating an account |
| 🎨 **Glassmorphic UI** | Modern dark-themed design with glass effects |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0, Flask-Login, Flask-SQLAlchemy |
| **AI/LLM** | Groq API — Llama 3.3 70B Versatile |
| **Frontend** | Jinja2 Templates, Vanilla CSS (Glassmorphism) |
| **Database** | SQLite (local) / `/tmp` SQLite (Vercel) |
| **Charts** | Chart.js |
| **PDF Processing** | pypdf |
| **Deployment** | Vercel (Python Serverless) |

---

## 📂 Project Structure

```
AdaptiveQuiz/
├── main.py                    # Flask app entry point
├── requirements.txt           # Python dependencies
├── vercel.json                # Vercel deployment config
├── .env.example               # Environment variables template
│
├── backend/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy models (User, Question, QuizResult, etc.)
│   ├── ai_engine.py           # Groq LLM integration
│   ├── services.py            # PDF extraction, text processing
│   └── routes.py              # All Flask routes & blueprints
│
└── frontend/
    ├── static/
    │   └── css/
    │       └── style.css      # Glassmorphic design system
    └── templates/
        ├── base.html          # Base layout with navbar
        ├── landing.html       # Landing/hero page
        ├── login.html         # Login form
        ├── signup.html        # Registration form
        ├── dashboard.html     # Dashboard with stats & quiz generator
        ├── quiz.html          # Active quiz page
        ├── results.html       # Results with charts & AI insights
        ├── study_hub.html     # Study hub input page
        ├── study_hub_result.html  # Study material display
        ├── library.html       # Quiz history table
        └── review.html        # Mistake bank review
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- A [Groq API Key](https://console.groq.com/) (free tier available)

### 1. Clone & Setup

```bash
git clone https://github.com/Araveenp/AdaptiveQuiz.git
cd AdaptiveQuiz
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
copy .env.example .env
# Edit .env and add your GROQ_API_KEY and a SECRET_KEY
```

### 3. Run Locally

```bash
python main.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🌐 Vercel Deployment

1. Push code to GitHub
2. Import the repo on [vercel.com](https://vercel.com)
3. Add environment variables in Vercel dashboard:
   - `GROQ_API_KEY` — your Groq API key
   - `SECRET_KEY` — any random string
4. Deploy!

---

## 📸 Screenshots

| Landing Page | Dashboard | Quiz |
|:---:|:---:|:---:|
| Glassmorphic hero | Stats & mastery | AI-generated questions |

---

## 👨‍💻 Author

**Araveen P** — [GitHub](https://github.com/Araveenp)

Built for the **Infosys Springboard Virtual Internship** — Adaptive Quiz & Question Generator project.

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).
