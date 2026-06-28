from __future__ import annotations

import re
from functools import lru_cache
from typing import Any
import httpx

WIKTIONARY_API = "https://en.wiktionary.org/w/api.php"
USER_AGENT = (
    "LexiconShaper/1.0 (https://meta.wikimedia.org/wiki/User-Agent_policy; "
    "theme word lookup) httpx"
)
DEFAULT_TIMEOUT = 20.0


def theme_tokens(theme: str) -> list[str]:
    """Split theme into lookup tokens (commas and whitespace)."""
    raw = re.split(r"[\s,]+", theme.strip())
    seen: set[str] = set()
    out: list[str] = []
    for t in raw:
        t = t.strip().strip(",")
        if not t:
            continue
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _normalize_title(token: str) -> str:
    return token.strip().replace(" ", "_")


# ---
# Wikitext extraction (English section: Synonyms + Related terms + syn templates)
# Examples:
#   [[word]], [[word|alt]]
#   {{syn|en|foo|bar}}
#   {{synonyms|en|foo|bar}}
# ---

_LINK = re.compile(r"\[\[([^]|#]+)(?:\|[^\]]+)?\]\]")
# syn / synonyms: language code then lemma parameters (skip qualifiers like {{sense|...}})
_SYN_TEMPLATE = re.compile(
    r"\{\{\s*synonyms?\s*\|\s*(?:en|EN)\s*\|([^}]+)\}\}",
    re.IGNORECASE | re.DOTALL,
)
# Lemma templates: {{l|en|word}}, {{m|en|word}}
_LM_EN_TEMPLATE = re.compile(
    r"\{\{\s*[lm]\s*\|\s*en\s*\|([^}|#]+)",
    re.IGNORECASE,
)


def _clean_lemma(raw: str) -> str | None:
    s = raw.strip()
    if not s or s.startswith("("):
        return None
    # Take first segment if template garbage remains
    s = re.split(r"[\[\]{}]", s)[0].strip()
    if not s or len(s) > 64:
        return None
    if ":" in s:  # interwiki, category
        return None
    if not re.match(r"^[a-zA-Z][a-zA-Z\-']*$", s):
        return None
    return s.lower()


def _extract_from_syn_templates(text: str) -> list[str]:
    out: list[str] = []
    for m in _SYN_TEMPLATE.finditer(text):
        inner = m.group(1)
        for part in inner.split("|"):
            lemma = _clean_lemma(part)
            if lemma:
                out.append(lemma)
    return out


def _extract_from_l_templates(text: str) -> list[str]:
    out: list[str] = []
    for m in _LM_EN_TEMPLATE.finditer(text):
        raw = m.group(1).strip()
        raw = raw.split("#")[0].strip()
        if "|" in raw:
            raw = raw.split("|", 1)[0].strip()
        lemma = _clean_lemma(raw.replace("_", " "))
        if lemma:
            out.append(lemma)
    return out


def _extract_wikilinks(text: str) -> list[str]:
    out: list[str] = []
    for m in _LINK.finditer(text):
        target = m.group(1).strip()
        if ":" in target or target.startswith("/"):
            continue
        target = target.split("#")[0].strip()
        lemma = _clean_lemma(target.replace("_", " "))
        if lemma:
            out.append(lemma)
    return out


def _english_section(wikitext: str) -> str:
    m = re.search(r"^==\s*English\s*==\s*$", wikitext, re.MULTILINE | re.IGNORECASE)
    if not m:
        return ""
    rest = wikitext[m.end() :]
    m2 = re.search(r"^==\s*[A-Za-z]", rest, re.MULTILINE)
    end = m2.start() if m2 else len(rest)
    return rest[:end]


def _named_subsection(section: str, name: str) -> str:
    pat = re.compile(rf"^=+\s*{re.escape(name)}\s*=+\s*$", re.MULTILINE | re.IGNORECASE)
    m = pat.search(section)
    if not m:
        return ""
    rest = section[m.end() :]
    m2 = re.search(r"^={3,}\s*\S", rest, re.MULTILINE)
    end = m2.start() if m2 else len(rest)
    return rest[:end]


def extract_lemmas_from_wikitext(wikitext: str) -> list[str]:
    """Pull synonym / related-term style lemmas from English Wiktionary wikitext."""
    english = _english_section(wikitext)
    if not english:
        english = wikitext

    chunks: list[str] = []
    for heading in ("Synonyms", "Related terms", "Near synonyms"):
        sub = _named_subsection(english, heading)
        if sub:
            chunks.append(sub)

    lemmas: list[str] = []
    for ch in chunks:
        lemmas.extend(_extract_wikilinks(ch))
        lemmas.extend(_extract_from_syn_templates(ch))
        lemmas.extend(_extract_from_l_templates(ch))

    lemmas.extend(_extract_from_syn_templates(english))
    lemmas.extend(_extract_from_l_templates(english))

    seen: set[str] = set()
    out: list[str] = []
    for w in lemmas:
        if w not in seen:
            seen.add(w)
            out.append(w)
    return out


@lru_cache(maxsize=256)
def _fetch_wikitext_cached(title_norm: str) -> str | None:
    """Internal cached fetch; title_norm is underscore form."""
    params: dict[str, Any] = {
        "action": "parse",
        "page": title_norm,
        "prop": "wikitext",
        "formatversion": "2",
        "format": "json",
        "redirects": "1",
    }
    headers = {"User-Agent": USER_AGENT, "Api-User-Agent": "LexiconShaper/1.0"}
    try:
        with httpx.Client(timeout=DEFAULT_TIMEOUT, headers=headers) as client:
            r = client.get(WIKTIONARY_API, params=params)
            r.raise_for_status()
            data = r.json()
    except (httpx.HTTPError, ValueError):
        return None

    if not isinstance(data, dict):
        return None
    err = data.get("error")
    if isinstance(err, dict) and err.get("code"):
        return None
    parse = data.get("parse")
    if not isinstance(parse, dict):
        return None
    wt = parse.get("wikitext")
    if isinstance(wt, str):
        return wt
    if isinstance(wt, dict) and "body" in wt:
        b = wt.get("body")
        if isinstance(b, str):
            return b
    return None


def fetch_lemmas_for_token(token: str) -> list[str]:
    """Resolve a theme token to synonym/related lemmas via the Wiktionary API."""
    title = _normalize_title(token)
    if not title:
        return []
    wikitext = _fetch_wikitext_cached(title)
    if not wikitext:
        return []
    return extract_lemmas_from_wikitext(wikitext)


def collect_lemmas_for_theme(theme: str, cap: int = 200) -> list[str]:
    """Merge lemmas for all theme tokens; dedupe; cap length."""
    all_lemmas: list[str] = []
    seen: set[str] = set()
    for tok in theme_tokens(theme):
        for lem in fetch_lemmas_for_token(tok):
            if lem not in seen:
                seen.add(lem)
                all_lemmas.append(lem)
            if len(all_lemmas) >= cap:
                return all_lemmas
    return all_lemmas
