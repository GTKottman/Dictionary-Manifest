from __future__ import annotations

import asyncio
import random
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.db import save_search
from app.models.datamuse import DatamuseClient, DatamuseError, WordResult
from app.models.phonetics import enrich_word
from app.models.query import (
    SearchParams,
    filter_by_pos,
    lexicon_search,
    sort_by_preference,
    wiktionary_lexicon_search,
)
from app.models.rhymezone import RhymezoneClient, RhymezoneError

router = APIRouter(prefix="/api")
_dm_client = DatamuseClient()
_rz_client = RhymezoneClient()


class SearchRequest(BaseModel):
    theme: str
    emotions: list[str] = Field(default_factory=list)
    topics: str = ""
    spelling_pattern: str = ""
    starts_with: str = ""
    ends_with: str = ""
    contains: str = ""
    rhyme_with: str = ""
    sounds_like: str = ""
    max_results: int = Field(default=30, ge=1, le=100)
    prefer_common: bool = False
    pos_filter: str = ""
    syllable_min: int | None = None
    syllable_max: int | None = None
    stress_pattern: str = ""
    phonetic_match: str = "none"
    phonetic_anchor: str = ""


class WordOut(BaseModel):
    word: str
    score: int | None = None
    defs: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    syllables: int | None = None
    frequency: float | None = None
    stress_pattern: str | None = None
    phonemes: list[str] | None = None
    syllables_cmu: int | None = None


class SearchResponse(BaseModel):
    bank_a: list[WordOut] = Field(default_factory=list)
    bank_b: list[WordOut] = Field(default_factory=list)
    bank_a_source: str = ""
    bank_b_source: str = ""
    info: str | None = None
    warnings: list[str] = Field(default_factory=list)
    search_id: int | None = None


def _word_result_to_out(r: WordResult) -> WordOut:
    phon = enrich_word(r.word)
    return WordOut(
        word=r.word,
        score=r.score,
        defs=r.defs,
        tags=r.tags,
        syllables=r.syllables,
        frequency=r.frequency,
        stress_pattern=phon.get("stress_pattern"),
        phonemes=phon.get("phonemes"),
        syllables_cmu=phon.get("syllables_cmu"),
    )


def _params_from_request(req: SearchRequest) -> SearchParams:
    return SearchParams(
        theme=req.theme,
        emotions=req.emotions,
        topics=req.topics,
        spelling_pattern=req.spelling_pattern,
        starts_with=req.starts_with,
        ends_with=req.ends_with,
        contains=req.contains,
        rhyme_with=req.rhyme_with,
        sounds_like=req.sounds_like,
        max_results=req.max_results,
        prefer_common=req.prefer_common,
        pos_filter=req.pos_filter,
        syllable_min=req.syllable_min,
        syllable_max=req.syllable_max,
        stress_pattern=req.stress_pattern,
        phonetic_match=req.phonetic_match,
        phonetic_anchor=req.phonetic_anchor,
    )


@router.post("/search", response_model=SearchResponse)
async def search(req: SearchRequest) -> SearchResponse:
    if not req.theme.strip():
        return SearchResponse(info="Enter a theme so the search has a direction (e.g. horror, longing).")

    params = _params_from_request(req)
    warnings: list[str] = []

    # Run Datamuse and Wiktionary in parallel using threads (both are sync)
    dm_task = asyncio.to_thread(lexicon_search, _dm_client, params)
    wikt_task = asyncio.to_thread(wiktionary_lexicon_search, _dm_client, params)

    try:
        dm_result, wikt_result = await asyncio.gather(dm_task, wikt_task, return_exceptions=True)
    except Exception as e:
        return SearchResponse(info=f"Search failed: {e}")

    # Handle Datamuse result
    raw_dm: list[WordResult] = []
    dm_info: str | None = None
    if isinstance(dm_result, Exception):
        warnings.append(f"Primary search error: {dm_result}")
    elif isinstance(dm_result, tuple):
        raw_dm, dm_info = dm_result
        if dm_info:
            warnings.append(dm_info)

    # Handle Wiktionary result
    raw_wikt: list[WordResult] = []
    wikt_info: str | None = None
    if isinstance(wikt_result, Exception):
        warnings.append(f"Expanded search error: {wikt_result}")
    elif isinstance(wikt_result, tuple):
        raw_wikt, wikt_info = wikt_result
        if wikt_info:
            warnings.append(wikt_info)

    # Apply POS filter and preference sort
    bank_dm = sort_by_preference(filter_by_pos(raw_dm, params.pos_filter), params.prefer_common)
    bank_wikt = sort_by_preference(filter_by_pos(raw_wikt, params.pos_filter), params.prefer_common)

    # If user set rhyme_with, try near-rhymes as the third source for bank B supplementation
    if req.rhyme_with.strip() and not bank_wikt:
        try:
            rz_results = await asyncio.to_thread(
                _rz_client.near_rhymes, req.rhyme_with.strip(), req.max_results
            )
            bank_wikt = sort_by_preference(
                filter_by_pos(rz_results, params.pos_filter), params.prefer_common
            )
        except RhymezoneError:
            pass

    # Randomize which bank is A/B (blind comparison)
    sources = [("datamuse", bank_dm), ("wiktionary", bank_wikt)]
    random.shuffle(sources)
    source_a, words_a = sources[0]
    source_b, words_b = sources[1]

    # Enrich with CMU phonetics
    out_a = [_word_result_to_out(r) for r in words_a]
    out_b = [_word_result_to_out(r) for r in words_b]

    total = len(out_a) + len(out_b)

    # Save to history
    query_dict: dict[str, Any] = {
        "theme": req.theme,
        "emotions": req.emotions,
        "rhyme_with": req.rhyme_with,
        "sounds_like": req.sounds_like,
        "spelling_pattern": req.spelling_pattern,
        "starts_with": req.starts_with,
        "ends_with": req.ends_with,
        "contains": req.contains,
        "pos_filter": req.pos_filter,
        "syllable_min": req.syllable_min,
        "syllable_max": req.syllable_max,
        "stress_pattern": req.stress_pattern,
        "phonetic_match": req.phonetic_match,
        "phonetic_anchor": req.phonetic_anchor,
    }
    try:
        search_id = await save_search(query_dict, total)
    except Exception:
        search_id = None

    info: str | None = None
    if not out_a and not out_b:
        info = "No matches found. Try a broader theme, remove spelling constraints, or adjust filters."

    return SearchResponse(
        bank_a=out_a,
        bank_b=out_b,
        bank_a_source=source_a,
        bank_b_source=source_b,
        info=info,
        warnings=warnings,
        search_id=search_id,
    )
