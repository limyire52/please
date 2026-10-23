"""Python 내장 sqlite3로 방명록 테이블 하나만 관리한다."""

from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

PAGE_SIZE = 10
MAX_ENTRIES = 1000


class GuestbookFull(Exception):
    pass


class GuestbookStore:
    def __init__(self, path: Path):
        self.path = path

    def connect(self):
        connection = sqlite3.connect(self.path, timeout=5)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as connection, connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS entries (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL CHECK(length(name) BETWEEN 1 AND 20),
                    message TEXT NOT NULL CHECK(length(message) BETWEEN 1 AND 500),
                    created_at TEXT NOT NULL
                )
            """)

    def list_page(self, page: int):
        with closing(self.connect()) as connection, connection:
            total = connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            rows = connection.execute(
                "SELECT id, name, message, created_at FROM entries "
                "ORDER BY id DESC LIMIT ? OFFSET ?",
                (PAGE_SIZE, (page - 1) * PAGE_SIZE),
            ).fetchall()
        return rows, total

    def add(self, name: str, message: str):
        with closing(self.connect()) as connection, connection:
            # 개수 확인과 INSERT 사이에 다른 요청이 끼어 상한을 넘지 않게 한다.
            connection.execute("BEGIN IMMEDIATE")
            total = connection.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
            if total >= MAX_ENTRIES:
                raise GuestbookFull
            connection.execute(
                "INSERT INTO entries (name, message, created_at) VALUES (?, ?, ?)",
                (name, message, datetime.now(timezone.utc).isoformat(timespec="seconds")),
            )
