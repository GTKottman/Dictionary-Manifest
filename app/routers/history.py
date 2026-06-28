from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.db import clear_history, delete_history_entry, get_history

router = APIRouter(prefix="/api/history")


class HistoryEntry(BaseModel):
    id: int
    query: dict
    result_count: int
    created_at: str


@router.get("", response_model=list[HistoryEntry])
async def list_history(limit: int = Query(default=50, ge=1, le=200)) -> list[HistoryEntry]:
    rows = await get_history(limit=limit)
    return [HistoryEntry(**r) for r in rows]


@router.delete("/{entry_id}", status_code=204)
async def delete_entry(entry_id: int) -> None:
    ok = await delete_history_entry(entry_id)
    if not ok:
        raise HTTPException(status_code=404, detail="History entry not found.")


@router.delete("", status_code=204)
async def clear_all_history() -> None:
    await clear_history()
