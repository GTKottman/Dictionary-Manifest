from __future__ import annotations

import random
from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.models.datamuse import DatamuseClient, DatamuseError
from app.models.query import (
    SearchParams,
    filter_by_pos,
    lexicon_search,
    sort_by_preference,
    wiktionary_lexicon_search,
)

_views = Path(__file__).resolve().parent.parent / "views" / "templates"
templates = Jinja2Templates(directory=str(_views))

router = APIRouter()
_client = DatamuseClient()


def _parse_max(raw: str | None, default: int = 30) -> int:
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _comparison_context(
    results_left: list | None,
    results_right: list | None,
) -> dict:
    return {
        "comparison": results_left is not None and results_right is not None,
        "results_left": results_left,
        "results_right": results_right,
    }


@router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    ctx = {
        "error": None,
        "info": None,
        "values": _default_form_values(),
    }
    ctx.update(_comparison_context(None, None))
    return templates.TemplateResponse(request, "index.html", ctx)


@router.post("/search", response_class=HTMLResponse)
async def search(
    request: Request,
    theme: str = Form(""),
    topics: str = Form(""),
    spelling_pattern: str = Form(""),
    starts_with: str = Form(""),
    ends_with: str = Form(""),
    contains: str = Form(""),
    rhyme_with: str = Form(""),
    sounds_like: str = Form(""),
    max_results: str = Form("30"),
    prefer_common: str | None = Form(None),
    pos_filter: str = Form(""),
) -> HTMLResponse:
    values = {
        "theme": theme,
        "topics": topics,
        "spelling_pattern": spelling_pattern,
        "starts_with": starts_with,
        "ends_with": ends_with,
        "contains": contains,
        "rhyme_with": rhyme_with,
        "sounds_like": sounds_like,
        "max_results": max_results or "30",
        "prefer_common": prefer_common in ("on", "true", "1"),
        "pos_filter": pos_filter,
    }

    if not theme.strip():
        ctx = {
            "error": "Enter a theme so the search has a direction (e.g. horror, longing).",
            "info": None,
            "values": values,
        }
        ctx.update(_comparison_context(None, None))
        return templates.TemplateResponse(request, "index.html", ctx)

    params = SearchParams(
        theme=theme,
        topics=topics,
        spelling_pattern=spelling_pattern,
        starts_with=starts_with,
        ends_with=ends_with,
        contains=contains,
        rhyme_with=rhyme_with,
        sounds_like=sounds_like,
        max_results=_parse_max(max_results),
        prefer_common=prefer_common in ("on", "true", "1"),
        pos_filter=pos_filter,
    )

    try:
        raw_dm, _dm_info = lexicon_search(_client, params)
    except ValueError as e:
        ctx = {"error": str(e), "info": None, "values": values}
        ctx.update(_comparison_context(None, None))
        return templates.TemplateResponse(request, "index.html", ctx)
    except DatamuseError as e:
        ctx = {"error": str(e), "info": None, "values": values}
        ctx.update(_comparison_context(None, None))
        return templates.TemplateResponse(request, "index.html", ctx)

    try:
        raw_wikt, _wikt_info = wiktionary_lexicon_search(_client, params)
    except (ValueError, DatamuseError):
        raw_wikt = []

    bank_dm = sort_by_preference(
        filter_by_pos(raw_dm, params.pos_filter),
        params.prefer_common,
    )
    bank_wikt = sort_by_preference(
        filter_by_pos(raw_wikt, params.pos_filter),
        params.prefer_common,
    )

    pair = [bank_dm, bank_wikt]
    random.shuffle(pair)
    left, right = pair[0], pair[1]

    ctx = {
        "error": None,
        "info": None,
        "values": values,
    }
    ctx.update(_comparison_context(left, right))
    return templates.TemplateResponse(request, "index.html", ctx)


def _default_form_values() -> dict:
    return {
        "theme": "",
        "topics": "",
        "spelling_pattern": "",
        "starts_with": "",
        "ends_with": "",
        "contains": "",
        "rhyme_with": "",
        "sounds_like": "",
        "max_results": "30",
        "prefer_common": False,
        "pos_filter": "",
    }
