from __future__ import annotations

import json
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator

import aiosqlite

DB_PATH = Path(__file__).resolve().parent.parent / "lexicon.db"


async def init_db() -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS searches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_json TEXT NOT NULL,
                result_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS collection_words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                collection_id INTEGER NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
                word TEXT NOT NULL,
                metadata_json TEXT NOT NULL DEFAULT '{}',
                added_at TEXT NOT NULL,
                UNIQUE(collection_id, word)
            )
        """)
        await db.commit()


@asynccontextmanager
async def get_db() -> AsyncIterator[aiosqlite.Connection]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        yield db


async def save_search(query: dict[str, Any], result_count: int) -> int:
    async with get_db() as db:
        cur = await db.execute(
            "INSERT INTO searches (query_json, result_count, created_at) VALUES (?, ?, ?)",
            (json.dumps(query), result_count, datetime.utcnow().isoformat()),
        )
        await db.commit()
        return cur.lastrowid or 0


async def get_history(limit: int = 50) -> list[dict[str, Any]]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT id, query_json, result_count, created_at FROM searches ORDER BY id DESC LIMIT ?",
            (limit,),
        )
        rows = await cur.fetchall()
        return [
            {
                "id": r["id"],
                "query": json.loads(r["query_json"]),
                "result_count": r["result_count"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]


async def delete_history_entry(entry_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute("DELETE FROM searches WHERE id = ?", (entry_id,))
        await db.commit()
        return cur.rowcount > 0


async def clear_history() -> None:
    async with get_db() as db:
        await db.execute("DELETE FROM searches")
        await db.commit()


async def get_collections() -> list[dict[str, Any]]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT id, name, created_at FROM collections ORDER BY id DESC"
        )
        rows = await cur.fetchall()
        result = []
        for r in rows:
            wc = await db.execute(
                "SELECT COUNT(*) as cnt FROM collection_words WHERE collection_id = ?",
                (r["id"],),
            )
            wrow = await wc.fetchone()
            count = wrow["cnt"] if wrow else 0
            result.append(
                {"id": r["id"], "name": r["name"], "created_at": r["created_at"], "word_count": count}
            )
        return result


async def create_collection(name: str) -> dict[str, Any]:
    async with get_db() as db:
        cur = await db.execute(
            "INSERT INTO collections (name, created_at) VALUES (?, ?)",
            (name.strip(), datetime.utcnow().isoformat()),
        )
        await db.commit()
        return {"id": cur.lastrowid, "name": name.strip(), "word_count": 0}


async def delete_collection(collection_id: int) -> bool:
    async with get_db() as db:
        cur = await db.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
        await db.commit()
        return cur.rowcount > 0


async def rename_collection(collection_id: int, name: str) -> bool:
    async with get_db() as db:
        cur = await db.execute(
            "UPDATE collections SET name = ? WHERE id = ?",
            (name.strip(), collection_id),
        )
        await db.commit()
        return cur.rowcount > 0


async def get_collection_words(collection_id: int) -> list[dict[str, Any]]:
    async with get_db() as db:
        cur = await db.execute(
            "SELECT word, metadata_json, added_at FROM collection_words WHERE collection_id = ? ORDER BY added_at DESC",
            (collection_id,),
        )
        rows = await cur.fetchall()
        return [
            {
                "word": r["word"],
                "metadata": json.loads(r["metadata_json"]),
                "added_at": r["added_at"],
            }
            for r in rows
        ]


async def add_word_to_collection(
    collection_id: int, word: str, metadata: dict[str, Any]
) -> bool:
    async with get_db() as db:
        try:
            await db.execute(
                "INSERT OR IGNORE INTO collection_words (collection_id, word, metadata_json, added_at) VALUES (?, ?, ?, ?)",
                (collection_id, word.lower().strip(), json.dumps(metadata), datetime.utcnow().isoformat()),
            )
            await db.commit()
            return True
        except Exception:
            return False


async def remove_word_from_collection(collection_id: int, word: str) -> bool:
    async with get_db() as db:
        cur = await db.execute(
            "DELETE FROM collection_words WHERE collection_id = ? AND word = ?",
            (collection_id, word.lower().strip()),
        )
        await db.commit()
        return cur.rowcount > 0
