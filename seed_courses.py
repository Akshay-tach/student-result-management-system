"""Create the additional demo courses."""
from app import db_connection


COURSES = [
    ("SE301", "Software Engineering"),
    ("WD202", "Web Development"),
    ("AI301", "Artificial Intelligence"),
    ("NT201", "Computer Networks"),
    ("OS202", "Operating Systems"),
]


def create_courses():
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.executemany(
            "INSERT INTO courses (code, name) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE name=VALUES(name)",
            COURSES,
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    create_courses()
    print("Created or updated 5 additional courses.")
