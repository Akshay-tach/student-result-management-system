import os
from functools import wraps

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "local-development-key-change-me")


def db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST") or os.getenv("MYSQLHOST", "localhost"),
        port=int(os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306")),
        user=os.getenv("DB_USER") or os.getenv("MYSQLUSER", "root"),
        password=os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD", ""),
        database=os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "student_results"),
    )


def query(sql, params=(), one=False):
    conn = db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql, params)
        if cursor.with_rows:
            result = cursor.fetchone() if one else cursor.fetchall()
        else:
            conn.commit()
            result = None
        return result
    finally:
        cursor.close()
        conn.close()


def login_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("user_id"):
                return redirect(url_for("login"))
            if roles and session.get("role") not in roles:
                flash("You do not have permission to view that page.", "error")
                return redirect(url_for("dashboard"))
            return view(*args, **kwargs)
        return wrapped
    return decorator


def grade_for(mark):
    if mark >= 90: return "A+"
    if mark >= 80: return "A"
    if mark >= 70: return "B"
    if mark >= 60: return "C"
    if mark >= 50: return "D"
    return "F"


@app.route("/")
def index():
    return redirect(url_for("dashboard") if session.get("user_id") else url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = query("SELECT id, username, password_hash, role, full_name FROM users WHERE username=%s", (username,), one=True)
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session.update(user_id=user["id"], username=user["username"], role=user["role"], full_name=user["full_name"])
            return redirect(url_for("dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required()
def dashboard():
    role = session["role"]
    if role == "student":
        student = query("SELECT id, student_no FROM students WHERE user_id=%s", (session["user_id"],), one=True)
        results = query("""SELECT c.code, c.name AS course, r.assessment, r.marks, r.max_marks,
                          ROUND(100*r.marks/r.max_marks,1) AS percentage
                          FROM results r JOIN courses c ON c.id=r.course_id WHERE r.student_id=%s ORDER BY c.code""",
                        (student["id"],)) if student else []
        results = [dict(row, grade=grade_for(float(row["percentage"]))) for row in results]
        return render_template("student_dashboard.html", results=results, student_no=student["student_no"] if student else "Not linked")
    students = query("SELECT s.id, s.student_no, u.full_name, u.email, s.program, s.year_level FROM students s JOIN users u ON u.id=s.user_id ORDER BY u.full_name")
    courses = query("SELECT id, code, name FROM courses ORDER BY code")
    results = query("""SELECT r.id, u.full_name, s.student_no, c.code, c.name AS course, r.assessment, r.marks, r.max_marks
                      FROM results r JOIN students s ON s.id=r.student_id JOIN users u ON u.id=s.user_id
                      JOIN courses c ON c.id=r.course_id ORDER BY r.updated_at DESC LIMIT 100""")
    return render_template("staff_dashboard.html", students=students, courses=courses, results=results)


@app.route("/students", methods=["POST"])
@login_required("admin")
def add_student():
    name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip()
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    student_no = request.form.get("student_no", "").strip()
    if not all((name, email, username, password, student_no)):
        flash("Complete all required student fields.", "error")
    else:
        from werkzeug.security import generate_password_hash
        conn = db_connection()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO users (username,password_hash,role,full_name,email) VALUES (%s,%s,'student',%s,%s)",
                        (username, generate_password_hash(password), name, email))
            cur.execute("INSERT INTO students (user_id,student_no,program,year_level) VALUES (%s,%s,%s,%s)",
                        (cur.lastrowid, student_no, request.form.get("program", ""), request.form.get("year_level", 1)))
            conn.commit()
            flash("Student account created.", "success")
        except mysql.connector.IntegrityError:
            conn.rollback()
            flash("That username, email, or student number is already in use.", "error")
        finally:
            cur.close(); conn.close()
    return redirect(url_for("dashboard") + "#students")


@app.route("/results", methods=["POST"])
@login_required("admin", "teacher")
def save_result():
    try:
        student_id = int(request.form["student_id"])
        course_id = int(request.form["course_id"])
        marks = float(request.form["marks"])
        max_marks = float(request.form["max_marks"])
        assessment = request.form.get("assessment", "Final").strip() or "Final"
        if max_marks <= 0 or marks < 0 or marks > max_marks:
            raise ValueError
        query("""INSERT INTO results (student_id,course_id,assessment,marks,max_marks,entered_by)
                 VALUES (%s,%s,%s,%s,%s,%s)
                 ON DUPLICATE KEY UPDATE marks=VALUES(marks), max_marks=VALUES(max_marks), entered_by=VALUES(entered_by)""",
              (student_id, course_id, assessment, marks, max_marks, session["user_id"]))
        flash("Result saved. Grade: " + grade_for(marks / max_marks * 100), "success")
    except (ValueError, KeyError):
        flash("Enter valid marks (from 0 up to the maximum).", "error")
    return redirect(url_for("dashboard") + "#results")


@app.route("/results/<int:result_id>/delete", methods=["POST"])
@login_required("admin")
def delete_result(result_id):
    query("DELETE FROM results WHERE id=%s", (result_id,))
    flash("Result deleted.", "success")
    return redirect(url_for("dashboard") + "#results")


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "0") == "1")
