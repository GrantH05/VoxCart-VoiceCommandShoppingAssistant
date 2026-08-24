from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "shopping.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with closing(connect()) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS shopping_list (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                quantity INTEGER NOT NULL DEFAULT 1,
                unit TEXT NOT NULL DEFAULT 'item',
                category TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit TEXT NOT NULL,
                action TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        )
        conn.commit()


def list_items() -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT id, name, quantity, unit, category, created_at, updated_at FROM shopping_list ORDER BY category, name"
        ).fetchall()
        return [dict(r) for r in rows]


def add_item(name: str, quantity: int, unit: str, category: str) -> None:
    with closing(connect()) as conn:
        existing = conn.execute("SELECT quantity, unit FROM shopping_list WHERE name = ? COLLATE NOCASE", (name,)).fetchone()
        if existing:
            new_quantity = existing["quantity"] + quantity
            new_unit = unit if unit != "item" else existing["unit"]
            conn.execute(
                "UPDATE shopping_list SET quantity=?, unit=?, category=?, updated_at=CURRENT_TIMESTAMP WHERE name=? COLLATE NOCASE",
                (new_quantity, new_unit, category, name),
            )
        else:
            conn.execute(
                "INSERT INTO shopping_list(name, quantity, unit, category) VALUES (?, ?, ?, ?)",
                (name, quantity, unit, category),
            )
        conn.execute(
            "INSERT INTO history(name, quantity, unit, action) VALUES (?, ?, ?, 'add')",
            (name, quantity, unit),
        )
        conn.commit()


def remove_item(name: str) -> bool:
    with closing(connect()) as conn:
        row = conn.execute("SELECT quantity, unit, name FROM shopping_list WHERE name=? COLLATE NOCASE", (name,)).fetchone()
        if not row:
            return False
        conn.execute("DELETE FROM shopping_list WHERE name=? COLLATE NOCASE", (name,))
        conn.execute(
            "INSERT INTO history(name, quantity, unit, action) VALUES (?, ?, ?, 'remove')",
            (row["name"], row["quantity"], row["unit"]),
        )
        conn.commit()
        return True


def update_item(name: str, quantity: int, unit: str | None = None) -> bool:
    with closing(connect()) as conn:
        row = conn.execute("SELECT unit, name FROM shopping_list WHERE name=? COLLATE NOCASE", (name,)).fetchone()
        if not row:
            return False
        final_unit = unit if unit and unit != "item" else row["unit"]
        conn.execute(
            "UPDATE shopping_list SET quantity=?, unit=?, updated_at=CURRENT_TIMESTAMP WHERE name=? COLLATE NOCASE",
            (quantity, final_unit, name),
        )
        conn.execute(
            "INSERT INTO history(name, quantity, unit, action) VALUES (?, ?, ?, 'update')",
            (row["name"], quantity, final_unit),
        )
        conn.commit()
        return True


def clear_list() -> None:
    with closing(connect()) as conn:
        rows = conn.execute("SELECT name, quantity, unit FROM shopping_list").fetchall()
        for row in rows:
            conn.execute(
                "INSERT INTO history(name, quantity, unit, action) VALUES (?, ?, ?, 'remove')",
                (row["name"], row["quantity"], row["unit"]),
            )
        conn.execute("DELETE FROM shopping_list")
        conn.commit()


def history(limit: int = 50) -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            "SELECT name, quantity, unit, action, created_at FROM history ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


def frequent_added_items(limit: int = 5) -> list[dict]:
    with closing(connect()) as conn:
        rows = conn.execute(
            """
            SELECT name, COUNT(*) AS times_added, SUM(quantity) AS total_quantity
            FROM history
            WHERE action='add'
            GROUP BY name COLLATE NOCASE
            ORDER BY times_added DESC, MAX(id) DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
