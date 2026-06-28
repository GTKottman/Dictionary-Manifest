from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx

DATAMUSE_URL = "https://api.datamuse.com/words"
DEFAULT_TIMEOUT = 15.0


class DatamuseError(Exception):
    """Raised when the Datamuse API fails or returns an unexpected response."""


@dataclass
class WordResult:
    word: str
    score: int | None
    defs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    syllables: int | None = None
    frequency: float | None = None

    @classmethod
    def from_api_item(cls, item: dict[str, Any]) -> WordResult:
        word = str(item.get("word", "")).strip()
        score = item.get("score")
        if score is not None:
            try:
                score = int(score)
            except (TypeError, ValueError):
                score = None

        defs: list[str] = []
        raw_defs = item.get("defs")
        if isinstance(raw_defs, list):
            defs = [str(d) for d in raw_defs if d]
        elif isinstance(raw_defs, str):
            defs = [raw_defs]

        tags: list[str] = []
        raw_tags = item.get("tags")
        if isinstance(raw_tags, list):
            tags = [str(t) for t in raw_tags]

        syllables = None
        for t in tags:
            if t.startswith("syllables:"):
                try:
                    syllables = int(t.split(":", 1)[1])
                except (IndexError, ValueError):
                    pass
                break

        frequency = None
        for t in tags:
            if t.startswith("f:"):
                try:
                    frequency = float(t.split(":", 1)[1])
                except (IndexError, ValueError):
                    pass
                break

        return cls(
            word=word,
            score=score,
            defs=defs,
            tags=tags,
            syllables=syllables,
            frequency=frequency,
        )


class DatamuseClient:
    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout

    def search(self, params: dict[str, str | int | list[str]]) -> list[WordResult]:
        flat: list[tuple[str, str]] = []
        for key, value in params.items():
            if value is None or value == "":
                continue
            if isinstance(value, list):
                for v in value:
                    if v is not None and str(v) != "":
                        flat.append((key, str(v)))
            else:
                flat.append((key, str(value)))

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(DATAMUSE_URL, params=flat)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise DatamuseError(f"Could not reach the word API: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise DatamuseError("The word API returned invalid data.") from e

        if not isinstance(data, list):
            raise DatamuseError("Unexpected response from the word API.")

        return [WordResult.from_api_item(item) for item in data if isinstance(item, dict)]
