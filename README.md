# 📄 Resume Analyzer

> An AI-powered web application that analyzes resumes against a target job profile and provides intelligent, structured feedback — scored out of 100.

![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.3.3-black?style=flat-square&logo=flask&logoColor=white)
![SQLite](https://img.shields.io/badge/Database-SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-FF6F00?style=flat-square&logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📑 Table of Contents

- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Environment Variables](#environment-variables)
  - [Run the App](#run-the-app)
- [Usage](#-usage)
- [Database Schema](#-database-schema)
- [API & AI Integration](#-api--ai-integration)
- [Security](#-security)
- [Contributing](#-contributing)

---

## 🚀 About the Project

**Resume Analyzer** is a full-stack web application built with Python Flask. Users can upload their resume (PDF, DOCX, or TXT) and select a target job profile. The app extracts the resume text, sends it to **Google's Gemini 1.5 Flash** AI model, and returns:

- ✅ A **score out of 100** based on relevance, formatting, professionalism, and ATS optimization
- 💪 **Strengths** of the resume
- ⚠️ **Weaknesses** identified by AI
- 💡 **Actionable suggestions** for improvement
- 📝 A **match summary** tailored to the job profile

All results are saved to a database, allowing users to track their resume history over time on their personal dashboard. An admin panel provides a global view of all submissions.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔐 **User Authentication** | Register, login, and logout with hashed passwords |
| 📤 **Resume Upload** | Supports PDF, DOCX, DOC, and TXT file formats |
| 🤖 **AI-Powered Analysis** | Google Gemini AI evaluates the resume and returns structured feedback |
| 📊 **Score & Feedback** | Score out of 100 with strengths, weaknesses, and suggestions |
| 🗂️ **User Dashboard** | View all past resume submissions and average score |
| 🛡️ **Admin Panel** | Admin can view and delete all resumes across all users |
| 🗄️ **Persistent Storage** | All results saved to SQLite database |
| 🔒 **Secure File Handling** | File type validation and secure filename sanitization |

---

## 🛠️ Tech Stack

| Layer | Technology | Version |
|---|---|---|
| **Backend** | Python Flask | 2.3.3 |
| **Database** | SQLite | Built-in |
| **AI Model** | Google Gemini 1.5 Flash | via `google-generativeai` |
| **PDF Parsing** | pdfplumber | 0.10.2 |
| **DOCX Parsing** | docx2txt | 0.8 |
| **Security** | Werkzeug | 2.3.7 |
| **Config** | python-dotenv | 1.0.1 |
| **Templating** | Jinja2 (Flask built-in) | — |

---

## 🗂️ Project Structure

```
Resume_analyzer/
│
├── run.py                   # Entry point — starts the Flask server
├── .env                     # Environment variables (API keys, secrets)
├── requirements.txt         # Python dependencies
├── database.db              # SQLite database (auto-created on first run)
│
├── uploads/                 # Uploaded resume files stored here
│
├── app/                     # Core application package
│   ├── __init__.py          # App Factory — creates and configures Flask app
│   ├── routes.py            # Main routes: register, login, upload, feedback
│   ├── user_routes.py       # User dashboard + DB connection helper
│   ├── admin_routes.py      # Admin login, dashboard, resume deletion
│   └── utils.py             # Helpers: DB init, AI analysis, text extraction
│
├── templates/               # Jinja2 HTML templates
│   ├── home.html
│   ├── start.html
│   ├── register.html
│   ├── login.html
│   ├── upload.html
│   ├── feedback.html
│   ├── user_dashboard.html
│   ├── admin_login.html
│   └── admin_dashboard.html
│
└── static/
    └── css/                 # Page stylesheets
```

---

## 🏁 Getting Started

### Prerequisites

Ensure you have the following installed:

- Python 3.10 or higher
- pip (Python package manager)
- A valid [Google Gemini API Key](https://aistudio.google.com/app/apikey)

---

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/your-username/resume-analyzer.git
cd resume-analyzer
```

**2. Create and activate a virtual environment** *(recommended)*

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

---

### Environment Variables

Create a `.env` file in the root directory with the following:

```env
GOOGLE_GEMINI_API_KEY=your_gemini_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
```

> ⚠️ **Never commit your `.env` file to version control.** Add it to `.gitignore`.

To get a Gemini API key, visit: [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

---

### Run the App

```bash
python run.py
```

Open your browser and navigate to:

```
http://localhost:5000
```

The SQLite database (`database.db`) will be **automatically created** on the first run.

---

## 📖 Usage

### 👤 Regular User

| Step | Action | URL |
|---|---|---|
| 1 | Create an account | `/register` |
| 2 | Log in | `/login` |
| 3 | Upload resume + select job profile | `/upload` |
| 4 | View AI feedback and score | `/feedback` |
| 5 | Review full history & average score | `/dashboard` |

### 🛡️ Admin

| Step | Action | URL |
|---|---|---|
| 1 | Log in as admin | `/admin/login` |
| 2 | View all user resumes | `/admin/dashboard` |
| 3 | Delete any resume | Available on dashboard |

> **Default Admin Credentials:** `username: admin` | `password: admin`

---

## 🗄️ Database Schema

### `users` Table

```sql
CREATE TABLE users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);
```

### `resumes` Table

```sql
CREATE TABLE resumes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    username    TEXT NOT NULL,
    filename    TEXT,
    job_profile TEXT,
    score       REAL,
    feedback    TEXT,                        -- Stored as JSON string
    uploaded_on TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

> The `feedback` column stores the full Gemini AI response as a **serialized JSON string**, which is parsed back to a dictionary when displayed.

---

## 🤖 API & AI Integration

The app uses **Google Gemini 1.5 Flash** to analyze resumes.

### Scoring Criteria

| Criterion | Weight |
|---|---|
| Relevance to Job Role | 40% |
| Formatting & Structure | 20% |
| Professionalism | 20% |
| ATS Optimization | 20% |

### AI Response Format

The model is instructed via prompt engineering to return **strictly JSON**:

```json
{
  "score": 78,
  "match_summary": "The resume is well-suited for a backend developer role...",
  "strengths": ["Strong Python skills", "Good project experience"],
  "weaknesses": ["Missing keywords for ATS", "No quantified achievements"],
  "suggestions": ["Add measurable impact to each role", "Include relevant certifications"]
}
```

### Supported File Formats

| Format | Library Used |
|---|---|
| `.pdf` | `pdfplumber` |
| `.docx` / `.doc` | `docx2txt` |
| `.txt` | Python built-in `open()` |

---

## 🔐 Security

- **Password Hashing** — Passwords stored using `werkzeug.security.generate_password_hash()` (bcrypt-style). Never stored as plain text.
- **Session Management** — Flask server-side sessions track authenticated users via `user_id`.
- **Route Protection** — `@login_required` and `@admin_login_required` decorators guard all sensitive routes.
- **File Validation** — Only whitelisted extensions (`pdf`, `doc`, `docx`, `txt`) are accepted.
- **Filename Sanitization** — `werkzeug.utils.secure_filename()` prevents path traversal attacks.
- **Ownership Enforcement** — Users can only delete their own resumes (verified against `session["user_id"]`).
- **API Key Safety** — Gemini API key loaded from `.env` via `python-dotenv`, never hardcoded.

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -m "Add: your feature description"`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

---

## 📃 License

This project is licensed under the **MIT License**.

---

<div align="center">

Made with ❤️ using Flask & Google Gemini AI

</div>
