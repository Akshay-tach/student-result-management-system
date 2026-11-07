"""Create repeatable demo final results for every student and course."""
from app import db_connection


def create_results():
    conn = db_connection()
    cur = conn.cursor(dictionary=True)
    try:
        cur.execute("SELECT id FROM users WHERE role='teacher' ORDER BY id LIMIT 1")
        teacher = cur.fetchone()
        if not teacher:
            raise RuntimeError("Create at least one teacher before seeding results.")

        cur.execute("SELECT id, student_no FROM students ORDER BY student_no")
        students = cur.fetchall()
        cur.execute("SELECT id, code FROM courses ORDER BY code")
        courses = cur.fetchall()

        values = []
        for student_index, student in enumerate(students, start=1):
            for course_index, course in enumerate(courses, start=1):
                percentage = 55 + ((student_index * 7 + course_index * 5) % 41)
                values.append(
                    (
                        student["id"],
                        course["id"],
                        "Final",
                        percentage,
                        100,
                        teacher["id"],
                    )
                )

        cur.executemany(
            """
            INSERT INTO results
              (student_id, course_id, assessment, marks, max_marks, entered_by)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
              marks = VALUES(marks),
              max_marks = VALUES(max_marks),
              entered_by = VALUES(entered_by)
            """,
            values,
        )
        conn.commit()
        return len(values)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    count = create_results()
    print(f"Created or updated {count} student course results.")
