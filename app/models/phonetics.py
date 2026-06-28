from __future__ import annotations

import re
from typing import Any

try:
    import pronouncing as _p
    _PRONOUNCING_AVAILABLE = True
except ImportError:
    _p = None  # type: ignore[assignment]
    _PRONOUNCING_AVAILABLE = False

# CMU vowel phoneme bases (without stress digit)
_VOWELS = {
    "AA", "AE", "AH", "AO", "AW", "AY",
    "EH", "ER", "EY", "IH", "IY",
    "OW", "OY", "UH", "UW",
}


def _strip_stress(ph: str) -> str:
    return ph.rstrip("012")


def _is_vowel(ph: str) -> bool:
    return _strip_stress(ph) in _VOWELS


def get_phones(word: str) -> list[str] | None:
    """Return the first CMU phoneme string list for a word, or None."""
    if not _PRONOUNCING_AVAILABLE or not word:
        return None
    word_clean = word.lower().strip()
    phones_list = _p.phones_for_word(word_clean)
    if not phones_list:
        return None
    return phones_list[0].split()


def get_stress(word: str) -> str | None:
    """Return the stress pattern string (e.g. '10' for iambic foot)."""
    phones = get_phones(word)
    if phones is None:
        return None
    if not _PRONOUNCING_AVAILABLE:
        return None
    phones_str = " ".join(phones)
    stress = _p.stresses(phones_str)
    return stress or None


def get_syllable_count(word: str) -> int | None:
    """Return syllable count from CMU dict, or None."""
    phones = get_phones(word)
    if phones is None:
        return None
    return sum(1 for ph in phones if ph[-1].isdigit())


def get_stressed_vowels(phones: list[str]) -> list[str]:
    """Extract primary-stressed vowel phoneme bases for assonance matching."""
    return [_strip_stress(ph) for ph in phones if ph[-1:] == "1" and _is_vowel(ph)]


def get_onset_consonants(phones: list[str]) -> list[str]:
    """Extract leading consonant cluster for alliteration matching."""
    onset: list[str] = []
    for ph in phones:
        if not _is_vowel(ph):
            onset.append(_strip_stress(ph))
        else:
            break
    return onset


def get_all_consonants(phones: list[str]) -> list[str]:
    """Extract all consonant phoneme bases for consonance matching."""
    return [_strip_stress(ph) for ph in phones if not _is_vowel(ph)]


def enrich_word(word: str) -> dict[str, Any]:
    """Return a phonetics dict for a word: stress, syllables, phonemes, assonance/consonance keys."""
    phones = get_phones(word)
    if phones is None:
        return {
            "stress_pattern": None,
            "phonemes": None,
            "syllables_cmu": None,
            "assonance_vowels": [],
            "alliteration_onset": [],
            "consonance_consonants": [],
        }
    phones_str = " ".join(phones)
    stress = _p.stresses(phones_str) if _PRONOUNCING_AVAILABLE else None
    syllables = sum(1 for ph in phones if ph[-1:].isdigit())
    return {
        "stress_pattern": stress,
        "phonemes": phones,
        "syllables_cmu": syllables,
        "assonance_vowels": get_stressed_vowels(phones),
        "alliteration_onset": get_onset_consonants(phones),
        "consonance_consonants": get_all_consonants(phones),
    }


def stress_matches(word: str, pattern: str) -> bool:
    """Check if a word's stress pattern matches the requested pattern string.

    Pattern uses '1' for stressed syllable, '0' for unstressed.
    Partial prefix matching: pattern '10' matches any word that starts '10…'.
    """
    if not pattern:
        return True
    actual = get_stress(word)
    if actual is None:
        return True  # unknown words pass through
    # Strip 2s (secondary stress) to binary for comparison
    binary = actual.replace("2", "1")
    return binary.startswith(pattern)


def syllable_in_range(word: str, syl_min: int | None, syl_max: int | None) -> bool:
    """Check if a word's syllable count falls within the requested range."""
    if syl_min is None and syl_max is None:
        return True
    count = get_syllable_count(word)
    if count is None:
        return True  # unknown words pass through
    if syl_min is not None and count < syl_min:
        return False
    if syl_max is not None and count > syl_max:
        return False
    return True


def _anchor_set(anchor_word: str, mode: str) -> set[str] | None:
    """Compute the phoneme set for the anchor word under the given mode."""
    phones = get_phones(anchor_word)
    if phones is None:
        return None
    if mode == "assonance":
        vals = get_stressed_vowels(phones)
        return set(vals) if vals else None
    if mode == "alliteration":
        vals = get_onset_consonants(phones)
        return set(vals) if vals else None
    if mode == "consonance":
        vals = get_all_consonants(phones)
        return set(vals) if vals else None
    return None


def phonetic_matches(word: str, anchor_set: set[str] | None, mode: str) -> bool:
    """Check if a word shares the phonetic feature defined by anchor_set and mode."""
    if mode == "none" or anchor_set is None:
        return True
    phones = get_phones(word)
    if phones is None:
        return True
    if mode == "assonance":
        candidate = set(get_stressed_vowels(phones))
    elif mode == "alliteration":
        candidate = set(get_onset_consonants(phones))
    elif mode == "consonance":
        candidate = set(get_all_consonants(phones))
    else:
        return True
    return bool(candidate & anchor_set)


def build_anchor_set(anchor_word: str, mode: str) -> set[str] | None:
    """Public wrapper to compute anchor phoneme set."""
    if not anchor_word or mode == "none":
        return None
    return _anchor_set(anchor_word.strip().lower(), mode)
