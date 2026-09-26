import os
import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_PATH = Path(
    os.getenv("DATABASE_PATH", Path(__file__).resolve().with_name("summaries.db"))
)


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    with closing(get_connection()) as connection, connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute("""
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                source_name TEXT NOT NULL,
                original_text TEXT NOT NULL,
                summary_text TEXT NOT NULL,
                summary_length TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(summaries)")
        }
        if "user_id" not in columns:
            connection.execute(
                "ALTER TABLE summaries ADD COLUMN user_id INTEGER REFERENCES users(id)"
            )
        connection.execute(
            "CREATE INDEX IF NOT EXISTS summaries_user_id ON summaries(user_id)"
        )


def create_user(username, password_hash):
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        return cursor.lastrowid


def get_user_by_username(username):
    with closing(get_connection()) as connection:
        return connection.execute(
            "SELECT id, username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()


def save_summary(user_id, source_name, original_text, summary_text, summary_length):
    with closing(get_connection()) as connection, connection:
        cursor = connection.execute(
            """
            INSERT INTO summaries (
                user_id, source_name, original_text, summary_text, summary_length
            ) VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, source_name, original_text, summary_text, summary_length),
        )
        return cursor.lastrowid


def get_all_summaries(user_id):
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT id, source_name, summary_text, summary_length, created_at
            FROM summaries
            WHERE user_id = ?
            ORDER BY id DESC
            """,
            (user_id,),
        ).fetchall()


def get_summary_by_id(summary_id, user_id):
    with closing(get_connection()) as connection:
        return connection.execute(
            "SELECT * FROM summaries WHERE id = ? AND user_id = ?",
            (summary_id, user_id),
        ).fetchone()


def delete_summary(summary_id, user_id):
    with closing(get_connection()) as connection, connection:
        connection.execute(
            "DELETE FROM summaries WHERE id = ? AND user_id = ?",
            (summary_id, user_id),
        )
