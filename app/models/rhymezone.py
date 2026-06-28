from __future__ import annotations

import httpx

from app.models.datamuse import WordResult

RHYMEZONE_URL = "https://api.rhymezone.com/words"
DEFAULT_TIMEOUT = 12.0


class RhymezoneError(Exception):
    pass


class RhymezoneClient:
    """Thin client for the RhymeZone near-rhymes API.

    Used specifically for `rel_nry` (near/imperfect rhymes) to supplement
    Datamuse's perfect-rhyme results with a broader phonetically similar set.
    """

    def __init__(self, timeout: float = DEFAULT_TIMEOUT) -> None:
        self._timeout = timeout

    def near_rhymes(self, word: str, max_results: int = 50) -> list[WordResult]:
        """Fetch near-rhymes for a word from RhymeZone."""
        params: list[tuple[str, str]] = [
            ("rel_nry", word.strip()),
            ("max", str(max(1, min(100, max_results)))),
            ("md", "d"),
            ("md", "p"),
            ("md", "s"),
            ("md", "f"),
        ]
        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.get(RHYMEZONE_URL, params=params)
                response.raise_for_status()
        except httpx.HTTPError as e:
            raise RhymezoneError(f"RhymeZone API unavailable: {e}") from e

        try:
            data = response.json()
        except ValueError as e:
            raise RhymezoneError("RhymeZone returned invalid data.") from e

        if not isinstance(data, list):
            raise RhymezoneError("Unexpected response from RhymeZone.")

        return [WordResult.from_api_item(item) for item in data if isinstance(item, dict)]
