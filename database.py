import sqlite3
from contextlib import closing
from pathlib import Path


DATABASE_NAME = Path(__file__).resolve().with_name("summaries.db")


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    with closing(get_connection()) as connection:
        with connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name TEXT NOT NULL,
                    original_text TEXT NOT NULL,
                    summary_text TEXT NOT NULL,
                    summary_length TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


def save_summary(source_name, original_text, summary_text, summary_length):
    with closing(get_connection()) as connection:
        with connection:
            cursor = connection.execute(
                """
                INSERT INTO summaries (
                    source_name,
                    original_text,
                    summary_text,
                    summary_length
                )
                VALUES (?, ?, ?, ?)
                """,
                (source_name, original_text, summary_text, summary_length),
            )
            return cursor.lastrowid

def get_all_summaries():
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT id, source_name, summary_text, summary_length, created_at
            FROM summaries
            ORDER BY id DESC
            """
        ).fetchall()


def get_summary_by_id(summary_id):
    with closing(get_connection()) as connection:
        return connection.execute(
            """
            SELECT *
            FROM summaries
            WHERE id = ?
            """,
            (summary_id,),
        ).fetchone()


def delete_summary(summary_id):
    with closing(get_connection()) as connection:
        with connection:
            connection.execute(
                "DELETE FROM summaries WHERE id = ?",
                (summary_id,),
            )
