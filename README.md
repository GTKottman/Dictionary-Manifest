# Dictionary Puller (Lexicon Shaper)

A word-finding tool for writers. You describe a theme or mood, set some filters, and it pulls back a list of words that fit. Good for lyrics, poetry, creative writing, or any time you need the right word and can't think of it.

---

## What it does

You give it a theme (like "horror" or "longing") and it searches multiple word databases to find words that match. You can narrow things down with filters like:

- **Mood / Emotion** -- pick from a mood palette to bias the results
- **Spelling shape** -- find words that start with, end with, or contain certain letters
- **Sound** -- find words that rhyme with or sound like a target word
- **Syllables and meter** -- set a syllable range or a stress pattern (useful for fitting words into a poetic meter)
- **Phonetic match** -- filter by assonance, alliteration, or consonance relative to an anchor word
- **Part of speech** -- limit results to nouns, verbs, adjectives, or adverbs

Results come back in two banks (from different sources) so you can compare. You can save words you like into named collections, and your past searches are saved to a history panel.

---

## Requirements

- **Python 3.10+**
- **Node.js** (only needed the first time, to build the frontend)

---

## Setup

**1. Create a Python virtual environment**

```
py -3 -m venv venv
```

**2. Install Python dependencies**

```
venv\Scripts\pip install -r requirements.txt
```

That's it. The frontend builds itself automatically the first time you run the app.

---

## Running

Double-click `start.bat`, or run it from a terminal:

```
start.bat
```

Then open your browser to:

```
http://127.0.0.1:8000
```

Press `Ctrl+C` in the terminal to stop the server.

---

## Project layout

```
Dictionary Puller/
  main.py              # FastAPI entry point
  requirements.txt     # Python dependencies
  start.bat            # One-click launcher
  app/
    routers/           # API endpoints (search, history, collections, phonetics)
    models/            # Data models and external API wrappers
    controllers/       # Search logic
    db.py              # SQLite database (history + collections)
  frontend/
    src/               # React + TypeScript UI
```

---

## Notes

- History and collections are stored in a local SQLite database, so everything stays on your machine.
- No API keys are required. The app pulls word data from free public sources (Datamuse, RhymeZone, Wiktionary).
- Dark mode is supported and remembers your preference.
