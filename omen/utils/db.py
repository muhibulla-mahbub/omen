"""Local SQLite history storage for OMEN — all data stays on disk, never sent anywhere."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path
from typing import Any, Optional

DEFAULT_DB_PATH = Path.home() / ".omen" / "history.db"


def _ensure_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            method TEXT NOT NULL,
            url TEXT NOT NULL,
            status_code INTEGER,
            response_snippet TEXT
        )
        """
    )
    conn.commit()
    return conn


def save_request(
    method: str,
    url: str,
    status_code: Optional[int],
    response_snippet: str,
    db_path: Path = DEFAULT_DB_PATH,
    max_rows: int = 50,
) -> None:
    """Save a request record, trimming history to the most recent `max_rows` entries."""
    conn = _ensure_db(db_path)
    try:
        conn.execute(
            "INSERT INTO requests (timestamp, method, url, status_code, response_snippet) "
            "VALUES (?, ?, ?, ?, ?)",
            (time.time(), method, url, status_code, response_snippet[:500]),
        )
        conn.execute(
            """
            DELETE FROM requests WHERE id NOT IN (
                SELECT id FROM requests ORDER BY id DESC LIMIT ?
            )
            """,
            (max_rows,),
        )
        conn.commit()
    finally:
        conn.close()


def get_recent_requests(limit: int = 50, db_path: Path = DEFAULT_DB_PATH) -> list[dict[str, Any]]:
    """Return the most recent request records, newest first."""
    if not db_path.exists():
        return []
    conn = _ensure_db(db_path)
    try:
        cursor = conn.execute(
            "SELECT timestamp, method, url, status_code, response_snippet "
            "FROM requests ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = cursor.fetchall()
    finally:
        conn.close()

    return [
        {
            "timestamp": r[0],
            "method": r[1],
            "url": r[2],
            "status_code": r[3],
            "response_snippet": r[4],
        }
        for r in rows
    ]
