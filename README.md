# 🧠 AdaptiveQuiz — AI-Powered Adaptive Quiz Platform

An intelligent, AI-powered quiz platform that generates personalised questions and performance analytics using **OpenRouter LLM (Llama 3.3)**.

Built as a capstone project for the **Infosys Springboard Virtual Internship**.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **AI Quiz Generation** | Generate MCQ & True/False questions from topics, raw text, or PDF uploads |
| 📊 **Adaptive Difficulty** | Questions adapt based on your performance history |
| 📧 **Email OTP Verification** | Secure signup with email OTP verification |
| 🏆 **Streak Tracking** | Daily login streaks and gamification |
| 🔍 **Mistake Bank** | Review wrong answers and re-quiz on weak areas |
| 📈 **Performance Analytics** | Score history charts, topic mastery tracking, AI insights |
| 👤 **Guest Mode** | Try without creating an account |
| 📄 **Client-Side PDF Processing** | PDFs are parsed in the browser — no file size limits |
| 🎨 **Glassmorphic UI** | Modern dark-themed design with glass effects |
| ⏳ **Loading Animation** | Smooth loading overlay while AI generates your quiz |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Flask 3.0, Flask-Login, Flask-SQLAlchemy |
| **AI/LLM** | OpenRouter API — Llama 3.3 70B Instruct |
| **Frontend** | Jinja2 Templates, Vanilla CSS (Glassmorphism), pdf.js |
| **Database** | PostgreSQL (Neon, production) / SQLite (local dev) |
| **Charts** | Chart.js |
| **Email** | Python smtplib (Gmail SMTP for OTP) |
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
│   ├── ai_engine.py           # OpenRouter LLM integration
│   ├── services.py            # PDF extraction, text processing, OTP email
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
        ├── verify_otp.html    # OTP verification page
        ├── dashboard.html     # Dashboard with stats & quiz generator
        ├── quiz.html          # Active quiz page
        ├── results.html       # Results with charts & AI insights
        ├── library.html       # Quiz history table
        └── review.html        # Mistake bank review
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- An [OpenRouter API Key](https://openrouter.ai/keys) (free credits available)
- A Gmail account with [App Password](https://myaccount.google.com/apppasswords) (for OTP emails)

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
# Edit .env and add your keys:
#   OPENROUTER_API_KEY=sk-or-v1-...
#   SECRET_KEY=any-random-string
#   SMTP_EMAIL=your_gmail@gmail.com
#   SMTP_PASSWORD=your_gmail_app_password
#   DATABASE_URL=postgresql://... (optional, uses SQLite locally)
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
   - `OPENROUTER_API_KEY` — your OpenRouter API key
   - `SECRET_KEY` — any random string
   - `SMTP_EMAIL` — Gmail address for sending OTPs
   - `SMTP_PASSWORD` — Gmail App Password
   - `DATABASE_URL` — PostgreSQL connection string (e.g. from [neon.tech](https://neon.tech))
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
