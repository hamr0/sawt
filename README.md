```
            ███████╗ █████╗ ██╗    ██╗████████╗
            ██╔════╝██╔══██╗██║    ██║╚══██╔══╝  ))
            ███████╗███████║██║ █╗ ██║   ██║    )))
            ╚════██║██╔══██║██║███╗██║   ██║   ))))
            ███████║██║  ██║╚███╔███╔╝   ██║    )))
            ╚══════╝╚═╝  ╚═╝ ╚══╝╚══╝   ╚═╝     ))
                     كل كتاب له صوت
```

# Sawt — كل كتاب له صوت

Sawt produces two-voice Arabic audiobooks from raw book files (EPUB/DOCX/TXT). Text extraction, chapter splitting, and dialogue detection are production ready. SSML generation with dialect-matched Azure Neural TTS voices is next.

---

## Status

| Module | Status |
|--------|--------|
| Book Ingestion (EPUB/DOCX/TXT → text) | Production Ready |
| Chapter Splitting (25K char units) | Production Ready |
| Dialogue Detection (~95% accuracy) | Production Ready |
| SSML + Voice Selection (POC 4) | Next |
| Multi-Voice (per-character) | Closed — Azure Arabic has only 2 voices per dialect |

126 tests passing. 12 books validated across 3 formats.

## How It Works

```
data/books/{epub,docx,txt}/book.*
    | ingest/        → output/{format}/{book}/01_ingestion/  (clean text + paragraphs.csv)
    | chapters/      → output/{format}/{book}/02_chapters/   (chapter files + chapters.csv)
    | dialogue/      → output/{format}/{book}/03_segments/   (narrator/dialogue CSVs + review text)
    | ssml/          → output/{format}/{book}/04_ssml/       (SSML with voice tags)
    | azure_client   → output/{format}/{book}/05_audio/      (MP3 per chapter)
```

Each step produces a CSV for review. Review chapter by chapter, perfect each step before moving on.

## Approach

- **Text processing is the product.** Once text is correctly broken into parts, SSML is just markup.
- **Let Azure handle pronunciation.** We handle text structure (chapters, paragraphs, dialogue boundaries).
- **Two voices for fiction.** M/F voice switch for narrator/dialogue. Clear contrast that masks TTS artifacts.
- **Single voice for non-fiction.** Citations aren't performed dialogue.
- **Dialect-matched voices.** Egyptian author → ar-EG voices, Levantine → ar-SY/JO/LB, etc. One dialect per book.
- **POCs isolated by data.** Each reads from the previous step's file output, not its code.

## Repo Structure

```
Sawt/
├── src/audiobook/          # Pipeline modules
│   ├── ingest/             #   EPUB/DOCX/TXT → clean text
│   ├── chapters/           #   Chapter detection & splitting
│   ├── dialogue/           #   Narrator/dialogue segmentation
│   ├── ssml/               #   SSML generation + voice selection (next)
│   └── shared/             #   Azure client, CSV review utilities
├── tests/audiobook/        # Tests per module (126 passing)
├── data/books/             # Input books (epub/, docx/, txt/)
│   ├── epub/               #   EPUB books (primary content source)
│   ├── docx/               #   DOCX books (author submissions)
│   └── txt/                #   TXT files (internal/corpus use)
├── output/                 # Per-book working output (gitignored)
│   └── {format}/{book}/
│       ├── 01_ingestion/   #   clean_text.txt + paragraphs.csv
│       ├── 02_chapters/    #   chapter_*.txt + chapters.csv
│       ├── 03_segments/    #   segments.csv + ssml/*.csv + review/*.txt
│       ├── 04_ssml/        #   chapter_*.ssml (next)
│       └── 05_audio/       #   chapter_*.mp3 (next)
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── archive/                # IPA pipeline (reference only)
```

## Quick Start

```bash
pip install -r requirements.txt

# Run tests
pytest tests/audiobook/ -v

# Set Azure credentials (needed for POC-4 onwards)
cp .env.example .env
# Edit .env with your AZURE_SPEECH_KEY and AZURE_SPEECH_REGION
```

## Docs

| Doc | What |
|-----|------|
| [Documentation Hub](docs/README.md) | Full documentation navigation |
| [Plan](docs/02-features/azure-audiobooks/PLAN.md) | Execution plan, architecture decisions |
| [POC-1 Results](docs/03-logs/POC1_RESULTS.md) | Book ingestion — production ready |
| [POC-2 Results](docs/03-logs/POC2_RESULTS.md) | Chapter splitting — production ready |
| [POC-3 Results](docs/03-logs/POC3_RESULTS.md) | Dialogue detection — production ready |

## Cost

- Azure free tier: 5M chars/month for 12 months
- ~$8-12 per 150-page book at standard pricing ($16/1M chars)
- 32 Arabic neural voices across 16 dialects (2 per locale)

---

## Archive

The `archive/` directory contains a previous IPA phonological pipeline (329 tests, 5 dialects, syllabification, gemination, sun letters, allophones, emphatic spread). It produced accurate linguistic processing but unusable audio output — letter-by-letter phoneme control through SSML was too robotic. The audiobook pipeline takes a different approach entirely. See [archive/](archive/) for reference.

POC reference material (prototype history, production detector, research findings) lives in [docs/02-features/azure-audiobooks/reference/](docs/02-features/azure-audiobooks/reference/).
