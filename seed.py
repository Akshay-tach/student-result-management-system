"""Create demo accounts and sample grades. Run after schema.sql and pip install."""
from werkzeug.security import generate_password_hash
from app import db_connection

conn = db_connection()
cur = conn.cursor()
users = [
    ("admin", "Admin@123", "admin", "Avery Admin", "admin@example.com"),
    ("teacher", "Teacher@123", "teacher", "Taylor Teacher", "teacher@example.com"),
    ("student", "Student@123", "student", "Sam Student", "student@example.com"),
]
ids = {}
for username, password, role, name, email in users:
    cur.execute("INSERT INTO users (username,password_hash,role,full_name,email) VALUES (%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)",
                (username, generate_password_hash(password), role, name, email))
    ids[username] = cur.lastrowid
cur.execute("INSERT INTO students (user_id,student_no,program,year_level) VALUES (%s,'STU-1001','Computer Science',2) ON DUPLICATE KEY UPDATE id=LAST_INSERT_ID(id)", (ids['student'],))
student_id = cur.lastrowid
cur.execute("SELECT id FROM courses WHERE code='CS101'")
course_id = cur.fetchone()[0]
cur.execute("INSERT INTO results (student_id,course_id,assessment,marks,max_marks,entered_by) VALUES (%s,%s,'Final',88,100,%s) ON DUPLICATE KEY UPDATE marks=88,max_marks=100", (student_id, course_id, ids['teacher']))
conn.commit()
cur.close(); conn.close()
print("Demo data ready. Logins: admin/Admin@123, teacher/Teacher@123, student/Student@123")
