import sqlite3

from backend.app.core.config import (
    settings,
)


def connect(
) -> sqlite3.Connection:

    db_path = (
        settings
        .resolved_database_path
    )

    db_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    conn = sqlite3.connect(
        db_path
    )

    conn.row_factory = (
        sqlite3.Row
    )

    return conn


def init_db() -> None:

    with connect() as conn:

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                source_name TEXT NOT NULL,
                title TEXT NOT NULL,
                response_json TEXT NOT NULL,
                generated_at TEXT NOT NULL
            )
            """
        )

        conn.commit()