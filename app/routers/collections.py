from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.db import (
    add_word_to_collection,
    create_collection,
    delete_collection,
    get_collection_words,
    get_collections,
    remove_word_from_collection,
    rename_collection,
)

router = APIRouter(prefix="/api/collections")


class CollectionOut(BaseModel):
    id: int
    name: str
    created_at: str
    word_count: int


class CollectionWordOut(BaseModel):
    word: str
    metadata: dict
    added_at: str


class CreateCollectionBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class RenameCollectionBody(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class AddWordBody(BaseModel):
    word: str = Field(min_length=1, max_length=100)
    metadata: dict = Field(default_factory=dict)


@router.get("", response_model=list[CollectionOut])
async def list_collections() -> list[CollectionOut]:
    rows = await get_collections()
    return [CollectionOut(**r) for r in rows]


@router.post("", response_model=CollectionOut, status_code=201)
async def create(body: CreateCollectionBody) -> CollectionOut:
    row = await create_collection(body.name)
    return CollectionOut(id=row["id"], name=row["name"], created_at="", word_count=0)


@router.patch("/{collection_id}", response_model=CollectionOut)
async def rename(collection_id: int, body: RenameCollectionBody) -> CollectionOut:
    ok = await rename_collection(collection_id, body.name)
    if not ok:
        raise HTTPException(status_code=404, detail="Collection not found.")
    rows = await get_collections()
    match = next((r for r in rows if r["id"] == collection_id), None)
    if not match:
        raise HTTPException(status_code=404, detail="Collection not found.")
    return CollectionOut(**match)


@router.delete("/{collection_id}", status_code=204)
async def delete(collection_id: int) -> None:
    ok = await delete_collection(collection_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Collection not found.")


@router.get("/{collection_id}/words", response_model=list[CollectionWordOut])
async def list_words(collection_id: int) -> list[CollectionWordOut]:
    rows = await get_collection_words(collection_id)
    return [CollectionWordOut(**r) for r in rows]


@router.post("/{collection_id}/words", status_code=201)
async def add_word(collection_id: int, body: AddWordBody) -> dict:
    ok = await add_word_to_collection(collection_id, body.word, body.metadata)
    if not ok:
        raise HTTPException(status_code=409, detail="Word already in collection.")
    return {"word": body.word.lower().strip()}


@router.delete("/{collection_id}/words/{word}", status_code=204)
async def remove_word(collection_id: int, word: str) -> None:
    ok = await remove_word_from_collection(collection_id, word)
    if not ok:
        raise HTTPException(status_code=404, detail="Word not found in collection.")


@router.get("/{collection_id}/export")
async def export_collection(collection_id: int, fmt: str = "text") -> dict:
    rows = await get_collection_words(collection_id)
    if not rows:
        return {"content": "", "format": fmt}
    words = [r["word"] for r in rows]
    if fmt == "tsv":
        lines = ["word\tsyllables\tdefinition"]
        for r in rows:
            meta = r["metadata"]
            syl = str(meta.get("syllables", ""))
            defn = (meta.get("defs") or [""])[0].split("\t")[-1] if meta.get("defs") else ""
            lines.append(f"{r['word']}\t{syl}\t{defn}")
        return {"content": "\n".join(lines), "format": "tsv"}
    return {"content": "\n".join(words), "format": "text"}
