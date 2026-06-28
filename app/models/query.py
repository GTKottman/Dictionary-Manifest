from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.models.datamuse import DatamuseClient, WordResult
from app.models.moods import get_emotion_seeds
from app.models.phonetics import (
    build_anchor_set,
    enrich_word,
    phonetic_matches,
    stress_matches,
    syllable_in_range,
)
from app.models.wiktionary import collect_lemmas_for_theme


@dataclass
class SearchParams:
    theme: str
    emotions: list[str] = field(default_factory=list)
    topics: str = ""
    spelling_pattern: str = ""
    starts_with: str = ""
    ends_with: str = ""
    contains: str = ""
    rhyme_with: str = ""
    sounds_like: str = ""
    max_results: int = 30
    prefer_common: bool = False
    pos_filter: str = ""
    syllable_min: int | None = None
    syllable_max: int | None = None
    stress_pattern: str = ""
    phonetic_match: str = "none"
    phonetic_anchor: str = ""


def _normalize_piece(s: str) -> str:
    return s.strip().lower().replace(" ", "")


def build_spelling_pattern(p: SearchParams) -> str | None:
    raw = p.spelling_pattern.strip()
    if raw:
        return raw

    start = _normalize_piece(p.starts_with)
    end = _normalize_piece(p.ends_with)
    mid = _normalize_piece(p.contains)

    if not start and not end and not mid:
        return None

    if mid:
        core = f"*{mid}*"
        if start and end:
            return f"{start}{core}{end}"
        if start:
            return f"{start}{core}*"
        if end:
            return f"*{core}{end}"
        return core

    if start and end:
        return f"{start}*{end}"
    if start:
        return f"{start}*"
    if end:
        return f"*{end}"
    return None


def build_datamuse_params(p: SearchParams) -> dict[str, str | int | list[str]]:
    theme = p.theme.strip()
    if not theme:
        raise ValueError("Theme is required.")

    md: list[str] = ["d", "p", "s", "f"]
    params: dict[str, str | int | list[str]] = {
        "ml": theme,
        "max": max(1, min(100, int(p.max_results))),
        "md": md,
    }

    topics = p.topics.strip()
    if topics:
        params["topics"] = topics

    sp = build_spelling_pattern(p)
    if sp:
        params["sp"] = sp

    rhyme = p.rhyme_with.strip()
    if rhyme:
        params["rel_rhy"] = rhyme

    sl = p.sounds_like.strip()
    if sl:
        params["sl"] = sl

    return params


def filter_by_pos(results: list[WordResult], pos_filter: str) -> list[WordResult]:
    if not pos_filter:
        return results
    want = pos_filter.strip().lower()
    out: list[WordResult] = []
    for r in results:
        for t in r.tags:
            head = t.split(":", 1)[0]
            if t == want or head == want:
                out.append(r)
                break
    return out


def sort_by_preference(results: list[WordResult], prefer_common: bool) -> list[WordResult]:
    if not prefer_common:
        return results
    return sorted(
        results,
        key=lambda r: (r.frequency is None, -(r.frequency or 0)),
    )


def datamuse_sp_to_regex(sp: str) -> re.Pattern[str]:
    parts: list[str] = []
    for ch in sp.lower():
        if ch == "*":
            parts.append(".*")
        elif ch == "?":
            parts.append(".")
        else:
            parts.append(re.escape(ch))
    return re.compile("^" + "".join(parts) + "$", re.IGNORECASE)


def _base_md() -> list[str]:
    return ["d", "p", "s", "f"]


def _apply_phonetic_filters(
    results: list[WordResult],
    p: SearchParams,
) -> list[WordResult]:
    """Filter results by syllable range, stress pattern, and phonetic match mode."""
    has_syl = p.syllable_min is not None or p.syllable_max is not None
    has_stress = bool(p.stress_pattern.strip())
    has_phonetic = p.phonetic_match not in ("", "none") and bool(p.phonetic_anchor.strip())

    if not has_syl and not has_stress and not has_phonetic:
        return results

    anchor_set = build_anchor_set(p.phonetic_anchor, p.phonetic_match) if has_phonetic else None

    filtered: list[WordResult] = []
    for r in results:
        if has_syl and not syllable_in_range(r.word, p.syllable_min, p.syllable_max):
            continue
        if has_stress and not stress_matches(r.word, p.stress_pattern.strip()):
            continue
        if has_phonetic and not phonetic_matches(r.word, anchor_set, p.phonetic_match):
            continue
        filtered.append(r)
    return filtered


def _emotion_search(
    client: DatamuseClient,
    p: SearchParams,
    cap: int,
) -> list[WordResult]:
    """Run additional Datamuse searches for each emotion seed and union results."""
    seeds = get_emotion_seeds(p.emotions)
    if not seeds:
        return []

    sp = build_spelling_pattern(p)
    md = _base_md()
    seen: set[str] = set()
    results: list[WordResult] = []

    for seed in seeds:
        ep: dict[str, str | int | list[str]] = {
            "ml": seed,
            "max": min(50, max(20, cap // max(1, len(seeds)))),
            "md": md,
        }
        if sp:
            ep["sp"] = sp
        rhyme = p.rhyme_with.strip()
        if rhyme:
            ep["rel_rhy"] = rhyme
        try:
            rows = client.search(ep)
        except Exception:
            continue
        for r in rows:
            key = r.word.lower()
            if key not in seen:
                seen.add(key)
                results.append(r)
        if len(results) >= cap * 2:
            break

    return results[:cap]


def lexicon_search(
    client: DatamuseClient,
    p: SearchParams,
) -> tuple[list[WordResult], str | None]:
    """Run Datamuse search with fallbacks when ml+sp intersection is empty.

    Also layers in emotion-seeded results when p.emotions is set.
    """
    api_params = build_datamuse_params(p)
    sp = build_spelling_pattern(p)
    cap = max(1, min(100, int(p.max_results)))

    results = client.search(api_params)

    # Merge emotion-based results
    if p.emotions:
        emotion_results = _emotion_search(client, p, cap)
        seen = {r.word.lower() for r in results}
        for r in emotion_results:
            if r.word.lower() not in seen:
                seen.add(r.word.lower())
                results.append(r)

    if results:
        results = _apply_phonetic_filters(results, p)
        return results[:cap], None

    if sp:
        loose = {k: v for k, v in api_params.items() if k != "sp"}
        loose["max"] = min(400, max(cap * 4, 120))
        loose["md"] = _base_md()
        wide = client.search(loose)
        pat = datamuse_sp_to_regex(sp)
        filtered = [r for r in wide if pat.fullmatch(r.word)]
        if filtered:
            filtered = _apply_phonetic_filters(filtered, p)
            return filtered[:cap], (
                "The dictionary had no single hit for theme and pattern together; "
                "these are theme-related words filtered by your spelling shape."
            )

        sp_only_params: dict[str, str | int | list[str]] = {
            "sp": sp,
            "max": min(100, max(cap, 50)),
            "md": _base_md(),
        }
        sp_only = client.search(sp_only_params)
        sp_only = _apply_phonetic_filters(sp_only, p)
        if sp_only:
            return sp_only[:cap], (
                "No overlap between your theme and this pattern in one API pass; "
                "showing strong pattern matches you can still weigh against your theme by ear."
            )

    return [], (
        "No matches. Try a looser pattern (fewer letters fixed), a broader theme, "
        "or remove rhyme / sounds-like for more hits."
    )


def _datamuse_word_set(
    client: DatamuseClient,
    params: dict[str, str | int | list[str]],
) -> set[str]:
    rows = client.search(params)
    return {r.word.lower() for r in rows}


def wiktionary_lexicon_search(
    client: DatamuseClient,
    p: SearchParams,
) -> tuple[list[WordResult], str | None]:
    """Expand theme tokens via English Wiktionary synonyms/related terms, then align with Datamuse metadata."""
    theme = p.theme.strip()
    if not theme:
        raise ValueError("Theme is required.")

    try:
        raw_lemmas = collect_lemmas_for_theme(theme, cap=200)
    except Exception as e:
        return [], f"Wiktionary expansion failed: {e}"

    if not raw_lemmas:
        return [], (
            "One list had no matches for this theme; try another phrasing or a single-word theme."
        )

    lemmas = raw_lemmas
    sp = build_spelling_pattern(p)
    if sp:
        pat = datamuse_sp_to_regex(sp)
        lemmas = [w for w in lemmas if pat.fullmatch(w)]

    rhyme = p.rhyme_with.strip()
    if rhyme:
        try:
            allow = _datamuse_word_set(
                client,
                {"rel_rhy": rhyme, "max": 500, "md": ["d"]},
            )
            lemmas = [w for w in lemmas if w in allow]
        except Exception:
            pass

    sl = p.sounds_like.strip()
    if sl:
        try:
            allow_sl = _datamuse_word_set(
                client,
                {"sl": sl, "max": 500, "md": ["d"]},
            )
            lemmas = [w for w in lemmas if w in allow_sl]
        except Exception:
            pass

    cap = max(1, min(100, int(p.max_results)))
    md = _base_md()
    enriched: list[WordResult] = []
    seen_word: set[str] = set()
    attempt_pool = lemmas[: min(len(lemmas), 150)]
    for lem in attempt_pool:
        try:
            rows = client.search({"sp": lem, "max": 1, "md": md})
        except Exception:
            continue
        if not rows:
            continue
        row = rows[0]
        key = row.word.lower()
        if key in seen_word:
            continue
        if key != lem:
            continue
        seen_word.add(key)
        enriched.append(row)
        if len(enriched) >= cap:
            break

    if not enriched:
        return [], (
            "One list had no matches for this theme; try another phrasing or a single-word theme."
        )

    enriched = _apply_phonetic_filters(enriched, p)
    return enriched[:cap], None
