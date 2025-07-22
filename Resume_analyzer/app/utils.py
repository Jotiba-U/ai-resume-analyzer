import os
import json
import sqlite3
import pdfplumber
import docx2txt
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-1.5-flash")

# -------------------- DB INITIALIZATION -------------------- #
def init_db():
    with sqlite3.connect("database.db") as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                username TEXT NOT NULL,
                filename TEXT,
                job_profile TEXT,
                score REAL,
                feedback TEXT,
                uploaded_on TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        conn.commit()

# -------------------- FILE VALIDATION -------------------- #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[-1].lower() in {"pdf", "doc", "docx", "txt"}

# -------------------- TEXT EXTRACTION -------------------- #
def extract_text_from_pdf(file_path):
    try:
        with pdfplumber.open(file_path) as pdf:
            return ''.join(page.extract_text() or '' for page in pdf.pages)
    except Exception as e:
        print(f"[PDF Error] {e}")
        return ""

def extract_text_from_docx(file_path):
    try:
        return docx2txt.process(file_path)
    except Exception as e:
        print(f"[DOCX Error] {e}")
        return ""

# -------------------- AI RESUME ANALYSIS -------------------- #
def analyze_resume_ai(resume_text, job_profile):
    prompt = f"""
You are a strict, professional AI resume evaluator with expertise in HR, recruitment, and ATS systems.

Evaluate the following resume for the role of: **"{job_profile}"**

Criteria (weightage):
1. Relevance (40%)
2. Formatting (20%)
3. Professionalism (20%)
4. ATS Optimization (20%)

📄 Resume:
\"\"\"{resume_text}\"\"\"

Respond strictly in JSON:
{{
"score": integer (0-100),
"match_summary": "Summary...",
"strengths": ["...", "..."],
"weaknesses": ["...", "..."],
"suggestions": ["...", "..."]
}}

Rules:
- Honest, industry-level feedback
- No markdown/comments/explanations
- Avoid generic statements
"""

    try:
        response = model.generate_content(prompt)
        raw = response.text.strip() if response and response.text else ""
        if not raw:
            raise ValueError("Empty response from Gemini")

        json_start = raw.find("{")
        json_end = raw.rfind("}") + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("Invalid JSON format in response")

        parsed = json.loads(raw[json_start:json_end])
        parsed["score"] = round(min(max(float(parsed.get("score", 0)), 0), 100))

        return parsed

    except Exception as e:
        print("[AI Error]", e)
        return {
            "score": 0,
            "match_summary": "Could not generate feedback. Please try again later.",
            "strengths": [],
            "weaknesses": [],
            "suggestions": ["Please try again later or check your API quota."]
        }
