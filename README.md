# Arabic Audiobook Production

Produce Arabic audiobooks from raw book files (PDF/TXT) using Azure Neural TTS.
Two-voice (narrator + dialogue) as primary goal. Multi-voice (per-character) as stretch.

---

## Status

| What | Status |
|------|--------|
| POC-1: Book Ingestion | Pending |
| POC-2: Chapter Splitting | Pending |
| POC-3a: Two-Voice (narrator/dialogue) | Pending |
| POC-3b: Multi-Voice (per-character) | Stretch |

## How It Works

```
data/books/book.pdf
    | ingest.py        → output/{book}/ingestion/  (clean text + paragraphs.csv)
    | chapters.py      → output/{book}/chapters/   (chapter files + chapters.csv)
    | dialogue.py      → output/{book}/segments/   (narrator/dialogue tags + per-chapter CSV)
    | ssml.py          → output/{book}/ssml/       (SSML with voice tags)
    | azure_client.py  → output/{book}/audio/      (MP3 per chapter)
```

Each step produces a CSV for review. Review chapter by chapter, perfect each step before moving on.

## Approach

- **Text processing is the product.** Once text is correctly broken into parts, SSML is just markup.
- **Let Azure handle pronunciation.** We handle text structure (chapters, paragraphs, dialogue boundaries).
- **Two voices first.** Binary narration/dialogue classification. Voice switching masks TTS artifacts.
- **No dialect switching.** A book is a book. One voice profile per book.
- **POCs isolated by data.** Each reads from the previous step's file output, not its code.

## Repo Structure

```
src/audiobook/          # Pipeline modules (one file per POC)
    ingest.py           #   POC-1: PDF/TXT → clean text
    chapters.py         #   POC-2: chapter detection & splitting
    dialogue.py         #   POC-3: narrator/dialogue/character detection
    azure_client.py     #   Azure TTS wrapper
    voice_pool.py       #   Voice selection, gender matching
    ssml.py             #   SSML generation
    review.py           #   CSV export at every stage

tests/audiobook/        # Tests per POC
data/books/             # Input books (PDF/TXT)
output/                 # Per-book working output (gitignored)
docs/                   # Documentation
```

## Quick Start

```bash
pip install -r requirements.txt

# Set Azure credentials
cp .env.example .env
# Edit .env with your AZURE_SPEECH_KEY and AZURE_SPEECH_REGION
```

## Docs

| Doc | What |
|-----|------|
| [Documentation Hub](docs/README.md) | Full documentation navigation |
| [Plan](docs/02-features/azure-audiobooks/PLAN.md) | Execution plan, POC details, architecture decisions |
| [Repo Structure](docs/02-features/azure-audiobooks/REPO_STRUCTURE.md) | Directory layout, data flow, migration details |

## Cost

- Azure free tier: 5M chars/month for 12 months
- ~$8-12 per 150-page book at standard pricing ($16/1M chars)
- 14+ Arabic neural voices across 7 dialects

---

## Archive

The `archive/` directory contains a previous IPA phonological pipeline (329 tests, 5 dialects, syllabification, gemination, sun letters, allophones, emphatic spread). It produced accurate linguistic processing but unusable audio output — letter-by-letter phoneme control through SSML was too robotic. The audiobook pipeline takes a different approach entirely. See [archive/](archive/) for reference.

POC reference material (prototype history, production detector, research findings) lives in [docs/02-features/azure-audiobooks/reference/](docs/02-features/azure-audiobooks/reference/).
