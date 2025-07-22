import sqlite3
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from functools import wraps

admin = Blueprint('admin', __name__)

# Static admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin"

# ---------------- AUTH DECORATOR ---------------- #
def admin_login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Admin login required.", "error")
            return redirect(url_for("admin.admin_login"))
        return f(*args, **kwargs)
    return wrapper

# ---------------- ADMIN LOGIN ---------------- #
@admin.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect(url_for("admin.admin_dashboard"))
        flash("Invalid admin credentials", "error")

    return render_template("admin_login.html")

# ---------------- ADMIN DASHBOARD ---------------- #
@admin.route("/admin/dashboard")
@admin_login_required
def admin_dashboard():
    with sqlite3.connect("database.db") as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT resumes.id, resumes.filename, resumes.job_profile, resumes.score, resumes.feedback,
                   users.username
            FROM resumes
            JOIN users ON resumes.user_id = users.id
            ORDER BY resumes.id DESC
        """)
        rows = cursor.fetchall()

    resumes = []
    for row in rows:
        try:
            feedback = json.loads(row["feedback"])
        except Exception:
            feedback = {}

        resumes.append({
            "id": row["id"],
            "filename": row["filename"],
            "job_profile": row["job_profile"],
            "score": int(row["score"]),
            "feedback": feedback,
            "username": row["username"]
        })

    return render_template("admin_dashboard.html", resumes=resumes)

# ---------------- DELETE RESUME ---------------- #
@admin.route("/admin/delete_resume/<int:resume_id>", methods=["POST"])
@admin_login_required
def delete_resume(resume_id):
    with sqlite3.connect("database.db") as conn:
        conn.execute("DELETE FROM resumes WHERE id = ?", (resume_id,))
        conn.commit()
    flash("Resume deleted successfully.", "info")
    return redirect(url_for("admin.admin_dashboard"))

# ---------------- LOGOUT ---------------- #
@admin.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("admin.admin_login"))
