# memory.py
#!/usr/bin/env python3
import sqlite3
import re
from pathlib import Path
from typing import List, Tuple

APP_DIR = Path.home() / ".alice"
APP_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = APP_DIR / "alice_memory.db"

SAFE_CATEGORIES = {"identity", "preferences", "goals", "workflow", "skills", "projects", "constraints"}

_CACHE_TEXT = None
_CACHE_DIRTY = True


def _connect() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    con.execute("PRAGMA journal_mode=WAL;")
    con.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            pinned INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    con.execute("CREATE INDEX IF NOT EXISTS idx_mem_pin ON memories(pinned)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_mem_cat ON memories(category)")
    return con


def _mark_dirty():
    global _CACHE_DIRTY
    _CACHE_DIRTY = True


def normalize(s: str) -> str:
    s = s.lower().strip()
    s = re.sub(r"\s+", " ", s)
    return s


def exists_similar(content: str, con: sqlite3.Connection = None) -> bool:
    c = normalize(content)
    own = False
    if con is None:
        con = _connect()
        own = True
    cur = con.cursor()
    cur.execute("SELECT content FROM memories ORDER BY id DESC LIMIT 400")
    rows = cur.fetchall()
    if own:
        con.close()
    for (existing,) in rows:
        if normalize(existing) == c:
            return True
    return False


def add(category: str, content: str, pinned: bool = False) -> int:
    category = (category or "preferences").strip().lower()
    content = (content or "").strip()
    if not content:
        return 0
    if category not in SAFE_CATEGORIES:
        category = "preferences"

    con = _connect()
    try:
        if exists_similar(content, con=con):
            return 0
        with con:
            cur = con.execute(
                "INSERT INTO memories (category, content, pinned) VALUES (?, ?, ?)",
                (category, content, 1 if pinned else 0),
            )
            mem_id = int(cur.lastrowid)
        _mark_dirty()
        return mem_id
    finally:
        con.close()


def add_many(items):
    con = _connect()
    added = 0
    try:
        with con:
            for category, content, pinned in items:
                category = (category or "preferences").strip().lower()
                content = (content or "").strip()
                if not content:
                    continue
                if category not in SAFE_CATEGORIES:
                    category = "preferences"
                if exists_similar(content, con=con):
                    continue
                con.execute(
                    "INSERT INTO memories (category, content, pinned) VALUES (?, ?, ?)",
                    (category, content, 1 if pinned else 0),
                )
                added += 1
        if added:
            _mark_dirty()
        return added
    finally:
        con.close()


def list_memories(limit: int = 60) -> List[Tuple[int, str, str, int, str]]:
    con = _connect()
    try:
        cur = con.cursor()
        cur.execute(
            """
            SELECT id, category, content, pinned, created_at
            FROM memories
            ORDER BY pinned DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        return cur.fetchall()
    finally:
        con.close()


def delete(mem_id: int) -> None:
    con = _connect()
    try:
        with con:
            con.execute("DELETE FROM memories WHERE id = ?", (mem_id,))
        _mark_dirty()
    finally:
        con.close()


def reset_all() -> None:
    global _CACHE_TEXT, _CACHE_DIRTY
    if DB_PATH.exists():
        DB_PATH.unlink()
    _CACHE_TEXT = None
    _CACHE_DIRTY = True


def memories_for_prompt(max_chars: int = 1800) -> str:
    global _CACHE_TEXT, _CACHE_DIRTY

    if _CACHE_TEXT is not None and not _CACHE_DIRTY:
        return _CACHE_TEXT[:max_chars]

    rows = list_memories(limit=80)
    if not rows:
        _CACHE_TEXT = "None."
        _CACHE_DIRTY = False
        return _CACHE_TEXT

    lines = []
    for _id, cat, content, pinned, _created in reversed(rows):
        lines.append(f"- {cat}{' (PIN)' if pinned else ''}: {content}")

    _CACHE_TEXT = "\n".join(lines).strip()
    _CACHE_DIRTY = False
    return _CACHE_TEXT[:max_chars]


def seed_minimal_identity():
    items = [
        ("identity", "Name: Alice.", True),
        ("identity", "Created by: Siv (software project).", True),
        ("workflow", "No roleplay actions like *smiles*.", True),
        ("workflow", "No fabricated shared history.", True),
        ("workflow", "If unsure: say unsure + ask one short question.", True),
        
    ]
    add_many(items)
