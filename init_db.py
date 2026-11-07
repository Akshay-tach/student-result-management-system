"""Initialize the MySQL schema before the production web server starts."""
import os
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def connection_config(include_database=True):
    config = {
        "host": os.getenv("DB_HOST") or os.getenv("MYSQLHOST", "localhost"),
        "port": int(os.getenv("DB_PORT") or os.getenv("MYSQLPORT", "3306")),
        "user": os.getenv("DB_USER") or os.getenv("MYSQLUSER", "root"),
        "password": os.getenv("DB_PASSWORD") or os.getenv("MYSQLPASSWORD", ""),
    }
    if include_database:
        config["database"] = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "student_results")
    return config


def initialize_schema():
    database = os.getenv("DB_NAME") or os.getenv("MYSQLDATABASE", "student_results")
    conn = mysql.connector.connect(**connection_config(include_database=False))
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{database.replace('`', '``')}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        cursor.execute(f"USE `{database.replace('`', '``')}`")
        statements = Path("schema.sql").read_text(encoding="utf-8").split(";")
        for statement in statements:
            statement = statement.strip()
            if statement and not statement.upper().startswith(("CREATE DATABASE", "USE ")):
                cursor.execute(statement)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    initialize_schema()
    print("Database schema is ready.")
