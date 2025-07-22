import os
import json
import sqlite3
from flask import Blueprint, render_template, session, redirect, url_for, current_app

user = Blueprint('user', __name__)

# -------------------- DB CONNECTION -------------------- #
def get_db_connection():
    db_path = os.path.abspath(os.path.join(os.getcwd(), "database.db"))
    print(f"[DB DEBUG] Connecting to: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# -------------------- USER DASHBOARD -------------------- #
@user.route("/dashboard")
def user_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("main.login"))

    user_id = session["user_id"]

    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Fetch resumes and user info
        cursor.execute("SELECT * FROM resumes WHERE user_id = ?", (user_id,))
        resumes_raw = cursor.fetchall()

        cursor.execute("SELECT username, email FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        username = user_row["username"] if user_row else "Unknown"
        user_email = user_row["email"] if user_row else "user@example.com"

    # Process resume records
    resumes = []
    for r in resumes_raw:
        try:
            feedback = json.loads(r["feedback"]) if r["feedback"] else {}
        except Exception as e:
            print(f"[Feedback Parse Error] Resume ID {r['id']}: {e}")
            feedback = {}

        resumes.append({
            "id": r["id"],
            "filename": r["filename"],
            "job_profile": r["job_profile"],
            "score": r["score"],
            "uploaded_on": r["uploaded_on"],
            "match_summary": feedback.get("match_summary", "N/A"),
            "strengths": feedback.get("strengths", []),
            "weaknesses": feedback.get("weaknesses", []),
            "suggestions": feedback.get("suggestions", [])
        })

    total_resumes = len(resumes)
    average_score = round(sum(r['score'] for r in resumes) / total_resumes, 2) if resumes else 0

    return render_template(
        "user_dashboard.html",
        username=username,
        user_email=user_email,
        resume_data=resumes,
        total_resumes=total_resumes,
        average_score=average_score
    )
