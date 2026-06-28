from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.models.phonetics import (
    enrich_word,
    get_all_consonants,
    get_onset_consonants,
    get_phones,
    get_stressed_vowels,
    get_stress,
    get_syllable_count,
)

router = APIRouter(prefix="/api/phonetics")


class PhonemeOut(BaseModel):
    word: str
    phonemes: list[str] | None
    stress_pattern: str | None
    syllables: int | None
    assonance_vowels: list[str]
    alliteration_onset: list[str]
    consonance_consonants: list[str]
    available: bool


@router.get("/{word}", response_model=PhonemeOut)
async def get_phonetics(word: str) -> PhonemeOut:
    data = enrich_word(word.lower().strip())
    available = data.get("phonemes") is not None
    return PhonemeOut(
        word=word.lower().strip(),
        phonemes=data.get("phonemes"),
        stress_pattern=data.get("stress_pattern"),
        syllables=data.get("syllables_cmu"),
        assonance_vowels=data.get("assonance_vowels", []),
        alliteration_onset=data.get("alliteration_onset", []),
        consonance_consonants=data.get("consonance_consonants", []),
        available=available,
    )


class BatchPhoneticRequest(BaseModel):
    words: list[str]


@router.post("/batch", response_model=list[PhonemeOut])
async def get_phonetics_batch(body: BatchPhoneticRequest) -> list[PhonemeOut]:
    results: list[PhonemeOut] = []
    for word in body.words[:50]:
        data = enrich_word(word.lower().strip())
        available = data.get("phonemes") is not None
        results.append(
            PhonemeOut(
                word=word.lower().strip(),
                phonemes=data.get("phonemes"),
                stress_pattern=data.get("stress_pattern"),
                syllables=data.get("syllables_cmu"),
                assonance_vowels=data.get("assonance_vowels", []),
                alliteration_onset=data.get("alliteration_onset", []),
                consonance_consonants=data.get("consonance_consonants", []),
                available=available,
            )
        )
    return results
