# System State

**Last updated:** February 2026

## Current Status

Pipeline skeleton is in place. No POCs implemented yet.

## Architecture

```
Raw Book (PDF/TXT) → Ingestion → Chapter Splitting → Dialogue Detection → SSML → Azure TTS → Audio
```

Each stage produces CSV output for human review. POCs are isolated by data boundaries (file output), not code imports.

## Active Code

```
src/audiobook/          # Pipeline modules (skeleton)
├── __init__.py
├── ingest.py           # POC-1: PDF/TXT → clean text
├── chapters.py         # POC-2: chapter detection & splitting
├── dialogue.py         # POC-3: dialogue detection
├── azure_client.py     # Azure SDK wrapper
├── voice_pool.py       # Voice selection, gender matching
├── ssml.py             # SSML generation
└── review.py           # CSV export at every stage

tests/audiobook/        # Test skeletons
data/books/             # Input books (awalad-7aretna.txt, book2.txt)
output/                 # Per-book working output (gitignored)
```

## Data Flow

```
data/books/book.txt
    ↓ ingest.py
output/book/ingestion/clean_text.txt + paragraphs.csv    ← REVIEW
    ↓ chapters.py
output/book/chapters/chapter_*.txt + chapters.csv         ← REVIEW
    ↓ dialogue.py
output/book/segments/chapter_*.csv                        ← REVIEW
    ↓ ssml.py
output/book/ssml/chapter_*.ssml
    ↓ azure_client.py
output/book/audio/chapter_*.mp3
```

## POC Progress

| POC | Module | Status |
|-----|--------|--------|
| POC-1: Book Ingestion | `ingest.py` | Not started |
| POC-2: Chapter Splitting | `chapters.py` | Not started |
| POC-3a: Two-Voice Detection | `dialogue.py` | Not started |
| POC-3b: Multi-Voice Attribution | `dialogue.py` | Not started (stretch) |
| POC-4: Emotion/Prosody | — | Future |

## Dependencies

- Python 3.x
- pdfplumber (PDF extraction)
- azure-cognitiveservices-speech (Azure TTS SDK)
- python-arabic-reshaper (Arabic text handling)
- pytest (testing)

## Archive

The `archive/` directory contains a previous IPA phonological pipeline (329 tests, 5 dialects). It produced accurate linguistic processing but unusable audio output. Zero code shared with the audiobook pipeline. Reference only.

Prototype history (7 iterations of dialogue detection R&D) lives in `docs/02-features/azure-audiobooks/reference/prototypes/`.
