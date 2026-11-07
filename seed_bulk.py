"""Create a repeatable demo dataset of teachers and students."""
from werkzeug.security import generate_password_hash

from app import db_connection


def create_demo_users():
    conn = db_connection()
    cur = conn.cursor()
    try:
        teacher_password = generate_password_hash("Teacher@123")
        student_password = generate_password_hash("Student@123")

        for number in range(1, 21):
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (%s, %s, 'teacher', %s, %s)
                ON DUPLICATE KEY UPDATE
                  password_hash = VALUES(password_hash),
                  full_name = VALUES(full_name),
                  email = VALUES(email)
                """,
                (
                    f"teacher{number:02d}",
                    teacher_password,
                    f"Teacher {number:02d}",
                    f"teacher{number:02d}@example.com",
                ),
            )

        for number in range(1, 121):
            username = f"student{number:03d}"
            cur.execute(
                """
                INSERT INTO users (username, password_hash, role, full_name, email)
                VALUES (%s, %s, 'student', %s, %s)
                ON DUPLICATE KEY UPDATE
                  password_hash = VALUES(password_hash),
                  full_name = VALUES(full_name),
                  email = VALUES(email)
                """,
                (
                    username,
                    student_password,
                    f"Student {number:03d}",
                    f"{username}@example.com",
                ),
            )
            user_id = cur.lastrowid
            cur.execute(
                """
                INSERT INTO students (user_id, student_no, program, year_level)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  program = VALUES(program),
                  year_level = VALUES(year_level)
                """,
                (
                    user_id,
                    f"STU-{number:04d}",
                    "Computer Science",
                    ((number - 1) % 4) + 1,
                ),
            )

        conn.commit()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_demo_users()
    print("Created or updated 20 teachers and 120 students.")
    print("Teachers: teacher01 through teacher20 / Teacher@123")
    print("Students: student001 through student120 / Student@123")
