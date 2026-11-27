
import sqlite3
from contextlib import contextmanager

DB_NAME = "tasks.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


@contextmanager
def db_connection():
    conn = get_connection()

    try:
        with conn:
            yield conn
    finally:
        conn.close()


def create_table():
    with db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0
            )
        """)


def add_task(title):
    title = title.strip()

    if not title:
        return "Error: Task title cannot be empty."

    with db_connection() as conn:
        conn.execute(
            "INSERT INTO tasks (title) VALUES (?)",
            (title,)
        )

    return f"Task added: {title}"


def list_tasks():
    with db_connection() as conn:
        cursor = conn.execute(
            "SELECT id, title, completed FROM tasks"
        )
        tasks = cursor.fetchall()

    return tasks


def complete_task(task_id):
    with db_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET completed = 1 WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return f"Error: Task {task_id} not found."

    return f"Task {task_id} marked as completed."


def delete_task(task_id):
    with db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        if cursor.rowcount == 0:
            return f"Error: Task {task_id} not found."

    return f"Task {task_id} deleted."
