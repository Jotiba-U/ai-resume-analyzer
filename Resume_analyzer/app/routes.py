import os
import json
import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from .utils import allowed_file, extract_text_from_pdf, extract_text_from_docx, analyze_resume_ai
from app.user_routes import get_db_connection

main = Blueprint('main', __name__)

# -------------------- AUTH GUARD -------------------- #
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please login first.", "warning")
            return redirect(url_for("main.login"))
        return f(*args, **kwargs)
    return wrapper

# -------------------- STATIC PAGES -------------------- #
@main.route('/')
def home():
    return render_template('home.html')

@main.route('/start')
def start():
    return render_template("start.html")

# -------------------- REGISTER -------------------- #
@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not all([username, email, password, confirm]):
            flash("Please fill out all fields.", "error")
        elif password != confirm:
            flash("Passwords do not match.", "error")
        else:
            try:
                with sqlite3.connect("database.db") as conn:
                    cursor = conn.cursor()
                    if cursor.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
                        flash("Email already registered.", "error")
                    else:
                        cursor.execute(
                            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                            (username, email, generate_password_hash(password))
                        )
                        conn.commit()
                        session.update({
                            'user_id': cursor.lastrowid,
                            'username': username,
                            'email': email
                        })
                        return redirect(url_for("main.upload_resume"))
            except sqlite3.Error:
                flash("Registration failed. Please try again.", "error")

    return render_template("register.html")

# -------------------- LOGIN -------------------- #
@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not all([email, password]):
            flash("Please fill out all fields.", "error")
        else:
            with sqlite3.connect("database.db") as conn:
                cursor = conn.cursor()
                user = cursor.execute(
                    "SELECT id, username, password_hash FROM users WHERE email = ?",
                    (email,)
                ).fetchone()

            if user and check_password_hash(user[2], password):
                session.update({
                    'user_id': user[0],
                    'username': user[1],
                    'email': email
                })
                return redirect(url_for("main.upload_resume"))
            flash("Invalid credentials.", "error")

    return render_template("login.html")

# -------------------- LOGOUT -------------------- #
@main.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("main.login"))

# -------------------- UPLOAD RESUME -------------------- #
@main.route("/upload", methods=["GET", "POST"])
@login_required
def upload_resume():
    if request.method == "POST":
        job_profile = request.form.get("job_profile")
        file = request.files.get("resume_file")

        if not job_profile or not file or not allowed_file(file.filename):
            flash("Invalid input. Check file and job profile.", "error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(path)

        ext = filename.rsplit('.', 1)[-1].lower()
        resume_text = (
            extract_text_from_pdf(path) if ext == "pdf" else
            extract_text_from_docx(path) if ext in ("doc", "docx") else
            open(path, 'r', encoding='utf-8', errors='ignore').read()
        )

        if not resume_text.strip():
            flash("Resume is empty or unreadable.", "error")
            return redirect(request.url)

        analysis = analyze_resume_ai(resume_text, job_profile)
        if not analysis:
            flash("AI feedback failed.", "error")
            return redirect(request.url)

        user_id = session["user_id"]
        with sqlite3.connect("database.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
            user_row = cursor.fetchone()
            username = user_row[0] if user_row else "Unknown"

            cursor.execute("""
                INSERT INTO resumes (filename, job_profile, score, feedback, user_id, username)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                filename, job_profile, analysis['score'],
                json.dumps(analysis), user_id, username
            ))
            conn.commit()

        session.update({
            'filename': filename,
            'job_profile': job_profile,
            'score': analysis['score'],
            'strengths': analysis['strengths'],
            'weaknesses': analysis['weaknesses'],
            'suggestions': analysis['suggestions'],
            'feedback_text': analysis.get('match_summary')
        })

        return redirect(url_for("main.feedback"))

    return render_template("upload.html")

# -------------------- FEEDBACK -------------------- #
@main.route("/feedback")
@login_required
def feedback():
    user_id = session["user_id"]
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM resumes WHERE user_id = ?
            ORDER BY uploaded_on DESC LIMIT 1
        """, (user_id,))
        resume = cursor.fetchone()

    if not resume:
        flash("No resume found for feedback.", "error")
        return redirect(url_for("main.upload_resume"))

    try:
        analysis = json.loads(resume["feedback"])
    except Exception:
        analysis = {
            "score": resume["score"],
            "match_summary": "Could not parse AI feedback.",
            "strengths": [], "weaknesses": [], "suggestions": []
        }

    return render_template("feedback.html",
        filename=resume["filename"],
        job_profile=resume["job_profile"],
        score=analysis.get("score", 0),
        strengths=analysis.get("strengths", []),
        weaknesses=analysis.get("weaknesses", []),
        suggestions=analysis.get("suggestions", []),
        feedback_text=analysis.get("match_summary", "")
    )

# -------------------- DELETE RESUME -------------------- #
@main.route("/delete_resume/<int:resume_id>", methods=["POST"])
@login_required
def delete_resume(resume_id):
    user_id = session["user_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT filename, user_id FROM resumes WHERE id = ?", (resume_id,))
        resume = cursor.fetchone()

        if resume and resume["user_id"] == user_id:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], resume["filename"])
            if os.path.exists(file_path):
                os.remove(file_path)

            cursor.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
            conn.commit()
            flash("Resume deleted successfully.", "success")
        else:
            flash("Unauthorized or resume not found.", "error")

    return redirect(url_for("user.user_dashboard"))
