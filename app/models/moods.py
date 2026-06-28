from __future__ import annotations

# Maps mood/emotion labels to concrete Datamuse "means like" seed terms.
# Datamuse's ml= works best with concrete evocative words, not abstract emotion names.
# Multiple seeds are searched and results unioned for wider coverage.
MOOD_SEEDS: dict[str, list[str]] = {
    "melancholic": ["sorrow", "longing", "grief", "lament", "wistful", "ache"],
    "euphoric": ["bliss", "elation", "ecstasy", "rapture", "exhilaration", "joy"],
    "angry": ["rage", "fury", "wrath", "resentment", "defiance", "seething"],
    "fearful": ["dread", "terror", "anguish", "paranoia", "horror", "dread"],
    "hopeful": ["hope", "aspiration", "yearning", "faith", "anticipation", "optimism"],
    "nostalgic": ["memory", "longing", "reminisce", "bittersweet", "past", "childhood"],
    "romantic": ["love", "passion", "desire", "tenderness", "devotion", "adoration"],
    "peaceful": ["calm", "serenity", "tranquil", "solace", "stillness", "quiet"],
    "lonely": ["isolation", "solitude", "emptiness", "desolate", "abandoned", "hollow"],
    "defiant": ["rebellion", "resistance", "bold", "fierce", "unyielding", "refuse"],
    "mysterious": ["enigma", "shadow", "arcane", "cryptic", "unknown", "occult"],
    "dark": ["shadow", "abyss", "void", "sinister", "gloom", "despair"],
    "triumphant": ["victory", "triumph", "glory", "overcome", "prevail", "conquer"],
    "anxious": ["worry", "unease", "tension", "restless", "nervousness", "unsettled"],
    "ethereal": ["celestial", "transcend", "otherworldly", "mystical", "divine", "gossamer"],
    "gritty": ["raw", "rough", "grime", "hustle", "street", "grind"],
    "introspective": ["reflection", "contemplation", "soul", "inner", "ponder", "silence"],
    "sensual": ["desire", "allure", "intimate", "longing", "tempt", "sultry"],
    "bittersweet": ["loss", "beauty", "ache", "tender", "mixed", "poignant"],
    "rebellious": ["break", "defy", "riot", "refuse", "resist", "outcast"],
    "spiritual": ["divine", "sacred", "soul", "transcend", "faith", "prayer"],
    "powerful": ["strength", "force", "might", "dominate", "intense", "surge"],
    "haunting": ["ghost", "linger", "echo", "phantom", "memory", "specter"],
    "urgent": ["rush", "desperate", "pressing", "frantic", "haste", "now"],
    "tender": ["gentle", "soft", "care", "warmth", "fragile", "delicate"],
}

# Ordered list of moods for the palette UI (curated subset)
MOOD_PALETTE: list[dict[str, str]] = [
    {"id": "melancholic", "label": "Melancholic", "emoji": "🌧"},
    {"id": "dark", "label": "Dark", "emoji": "🌑"},
    {"id": "haunting", "label": "Haunting", "emoji": "👻"},
    {"id": "angry", "label": "Angry", "emoji": "🔥"},
    {"id": "defiant", "label": "Defiant", "emoji": "✊"},
    {"id": "rebellious", "label": "Rebellious", "emoji": "⚡"},
    {"id": "fearful", "label": "Fearful", "emoji": "😨"},
    {"id": "anxious", "label": "Anxious", "emoji": "😰"},
    {"id": "lonely", "label": "Lonely", "emoji": "🌫"},
    {"id": "nostalgic", "label": "Nostalgic", "emoji": "📷"},
    {"id": "bittersweet", "label": "Bittersweet", "emoji": "🥀"},
    {"id": "introspective", "label": "Introspective", "emoji": "🔍"},
    {"id": "hopeful", "label": "Hopeful", "emoji": "🌅"},
    {"id": "triumphant", "label": "Triumphant", "emoji": "🏆"},
    {"id": "euphoric", "label": "Euphoric", "emoji": "✨"},
    {"id": "romantic", "label": "Romantic", "emoji": "❤"},
    {"id": "sensual", "label": "Sensual", "emoji": "🌹"},
    {"id": "tender", "label": "Tender", "emoji": "🕊"},
    {"id": "peaceful", "label": "Peaceful", "emoji": "☁"},
    {"id": "ethereal", "label": "Ethereal", "emoji": "🌙"},
    {"id": "spiritual", "label": "Spiritual", "emoji": "🕯"},
    {"id": "mysterious", "label": "Mysterious", "emoji": "🌀"},
    {"id": "powerful", "label": "Powerful", "emoji": "💥"},
    {"id": "urgent", "label": "Urgent", "emoji": "⏱"},
    {"id": "gritty", "label": "Gritty", "emoji": "🏚"},
]


def get_emotion_seeds(emotions: list[str]) -> list[str]:
    """Expand a list of emotion labels into Datamuse seed terms, deduped."""
    seeds: list[str] = []
    seen: set[str] = set()
    for emo in emotions:
        key = emo.strip().lower()
        for seed in MOOD_SEEDS.get(key, [key]):
            if seed not in seen:
                seen.add(seed)
                seeds.append(seed)
    return seeds
