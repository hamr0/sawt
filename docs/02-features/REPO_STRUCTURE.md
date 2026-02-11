# Audiobook Pipeline - Repo Structure

**Date:** February 2026
**Purpose:** Clean structure for audiobook POCs, isolated from core IPA pipeline

---

## Context: Why Archive the IPA Pipeline

The repo originally built a full IPA phonological pipeline (src/core/, 329 tests, 5 dialects).
The letter-by-letter processing through SSML phoneme tags was academically correct but produced
unusable audio — too robotic, unintelligible. The assumption was never validated early enough.

The audiobook pipeline takes a fundamentally different approach: send plain Arabic text to Azure
neural voices and let Azure handle pronunciation. Our job is TEXT STRUCTURE, not pronunciation.

**LSP confirms: 0 imports connect the IPA pipeline to the audiobook code.** They share nothing.
Archive the IPA work (preserve history) and make the audiobook pipeline the active project.

---

## Current State (what gets archived)

```
src/                              # IPA pipeline → moves to archive/src/
│   ├── core/                     #   Phonological processors, syllabifier, IPA mapper
│   ├── dialects/                 #   MSA, Egyptian, Gulf, Levantine, Maghrebi
│   ├── integrations/             #   eSpeak, Polly
│   └── utils/                    #   Shared utilities
│
tools/azure_tts/                  # Audiobook POCs → moves to docs/02-features/azure-audiobooks/reference/
│   ├── azure_integration.py      #   Production code (evolve into src/audiobook/)
│   ├── character_voice_assignment.py
│   ├── prototypes/               #   7 iterations of R&D (valuable reference)
│   └── (mixed test scripts, data, docs)
│
tests/                            # 329 IPA tests → moves to archive/tests/
scripts/                          # Demo scripts → moves to archive/scripts/
app.py                            # Flask API → moves to archive/
audio/                            # Generated audio → moves to archive/audio/
```

Everything above moves to `archive/` in one commit. Clean slate for audiobook pipeline.

---

## Proposed Structure

```
Sawt/
│
├── src/audiobook/                     # ACTIVE - audiobook production pipeline
│   ├── __init__.py
│   ├── ingest/                        # POC-1: File ingestion (PDF/TXT/EPUB → text)
│   │   ├── __init__.py
│   │   └── core.py                    # Main ingestion logic
│   ├── chapters/                      # POC-2: Chapter splitting
│   │   ├── __init__.py
│   │   └── core.py                    # Chapter detection and splitting
│   ├── dialogue/                      # POC-3: Dialogue detection
│   │   ├── __init__.py
│   │   └── core.py                    # Narrator/dialogue segmentation
│   ├── ssml/                          # POC-4: SSML generation + voice selection
│   │   ├── __init__.py
│   │   └── core.py                    # SSML templates + dialect-matched voice config
│   └── shared/                        # Shared utilities
│       ├── __init__.py
│       ├── azure_client.py            # Azure SDK wrapper
│       └── review.py                  # CSV export at every stage
│
├── tests/audiobook/                   # ACTIVE - audiobook-specific tests
│   ├── __init__.py
│   ├── ingest/                        # POC-1 tests
│   │   ├── __init__.py
│   │   └── test_core.py
│   ├── chapters/                      # POC-2 tests
│   │   ├── __init__.py
│   │   └── test_core.py
│   ├── dialogue/                      # POC-3 tests
│   │   ├── __init__.py
│   │   └── test_core.py
│   └── ssml/                          # POC-4 tests
│       ├── __init__.py
│       └── test_core.py
│
├── data/books/                        # ACTIVE - test book inputs
│   ├── awalad-7aretna.txt             # MOVED from docs/02-features/azure-audiobooks/reference/
│   └── book2.txt                      # MOVED from docs/02-features/azure-audiobooks/reference/
│
├── output/                            # ACTIVE - per-book working output (gitignored)
│   └── {book-name}/                   # One directory per book
│       ├── ingestion/                 # POC-1 output
│       │   ├── clean_text.txt         #   Cleaned book text
│       │   └── paragraphs.csv         #   Paragraph inventory for review
│       ├── chapters/                  # POC-2 output
│       │   ├── chapter_01.txt         #   Individual chapter files
│       │   ├── chapter_02.txt
│       │   └── chapters.csv           #   Chapter inventory for review
│       ├── segments/                  # POC-3 output
│       │   ├── chapter_01.csv         #   Segments with narrator/dialogue tags
│       │   └── chapter_02.csv
│       ├── ssml/                      # SSML output
│       │   ├── chapter_01.ssml
│       │   └── chapter_02.ssml
│       └── audio/                     # Final audio
│           ├── chapter_01.mp3
│           └── chapter_02.mp3
│
├── docs/                              # ACTIVE - documentation
│   └── 02-features/azure-audiobooks/  # Plan and structure docs
│       ├── PLAN.md
│       └── REPO_STRUCTURE.md (this file)
│
├── archive/                           # PAUSED - IPA pipeline preserved intact
│   ├── src/                           #   core/, dialects/, integrations/, utils/, main.py
│   ├── tests/                         #   329 tests (unit, integration, smoke)
│   ├── data/                          #   masterTTS.json, test cases, reference audio
│   ├── scripts/                       #   demo, test, polly scripts
│   ├── tools/                         #   azure_tts (prototypes!), festival, xtts, syllabifier
│   ├── audio/                         #   generated audio files
│   ├── tasks/                         #   task management, LLM experiments
│   ├── templates/                     #   Flask templates
│   ├── demo_output/                   #   demo outputs
│   ├── app.py                         #   Flask API
│   └── KNOWLEDGE_BASE.md              #   reference docs
│
├── .env.example                       # KEEP - Azure key config
├── .gitignore                         # UPDATE - add output/
├── requirements.txt                   # UPDATE - audiobook dependencies only
├── pyproject.toml                     # UPDATE
├── CLAUDE.md                          # UPDATE - reflect new structure
└── README.md                          # UPDATE - audiobook project description
```

---

## Design Principles

### 1. POCs are isolated by DATA, not imports

Each POC reads from the previous POC's output directory, not from its code.
This means you can rewrite POC-1 completely without breaking POC-2,
as long as the output format stays the same.

```
data/books/book.txt
    ↓ ingest.py writes to:
output/book/ingestion/clean_text.txt + paragraphs.csv
    ↓ chapters.py reads from ↑, writes to:
output/book/chapters/chapter_*.txt + chapters.csv
    ↓ dialogue.py reads from ↑, writes to:
output/book/segments/chapter_*.csv
    ↓ ssml.py reads from ↑, writes to:
output/book/ssml/chapter_*.ssml
    ↓ azure_client.py reads from ↑, writes to:
output/book/audio/chapter_*.mp3
```

Each arrow is a file boundary. Each step is independently runnable and reviewable.

### 2. CSV review at every stage

Every POC produces a CSV in the book's output directory.
Review workflow: run POC → open CSV → fix issues → re-run → next POC.

| POC | CSV | What you review |
|-----|-----|-----------------|
| POC-1 | `paragraphs.csv` | Paragraph boundaries, char counts, encoding issues |
| POC-2 | `chapters.csv` | Chapter boundaries, split points, naming |
| POC-3 | `chapter_XX.csv` | Narration/dialogue tags per segment (per chapter) |

### 3. Package-based POCs (scalable structure)

Each POC is organized as a Python package (directory with `__init__.py` and `core.py`).
This provides room for future growth without refactoring:

- `ingest/` → can add `pdf_parser.py`, `epub_parser.py`, `validators.py` as needed
- `chapters/` → can add `strategies.py`, `validators.py` for different splitting approaches
- `dialogue/` → can add `llm_detector.py`, `patterns.py`, `rules.py` for multi-strategy detection

The `__init__.py` exports the main API, keeping imports clean: `from src.audiobook.ingest import ingest`

### 4. Shared utilities in shared/ package

Common code used across POCs lives in `src/audiobook/shared/`:
- `azure_client.py` — Azure SDK wrapper (evolved from `azure_integration.py`)
- `review.py` — CSV export (shared by all POCs)

SSML is a POC package (pipeline stage, not utility):
- `ssml/` — SSML generation + voice selection (POC 4, voice_pool folded in)

### 5. Archive is reference, not active code

`archive/` preserves the entire IPA pipeline and prototype history.
- Don't delete it (prototypes document the R&D journey, findings are the spec)
- Don't add to it (new work goes in `src/audiobook/`)
- Reference it when evolving code — especially `docs/02-features/azure-audiobooks/reference/prototypes/`

---

## What evolves from where

| Archive file | Becomes | What changes |
|--------------|---------|--------------|
| `docs/02-features/azure-audiobooks/reference/azure_integration.py` | `src/audiobook/azure_client.py` | Evolve, clean up, keep Azure SDK calls |
| `docs/02-features/azure-audiobooks/reference/character_voice_assignment.py` | `src/audiobook/ssml/core.py` | Voice selection folded into SSML generation (two-voice = simple config) |
| `docs/02-features/azure-audiobooks/reference/prototypes/06_simplified_detector.py` | `src/audiobook/dialogue.py` | Evolve state machine, adapt for chapter input |
| `docs/02-features/azure-audiobooks/reference/awalad-7aretna.txt` | `data/books/awalad-7aretna.txt` | Move test books to active data directory |
| `docs/02-features/azure-audiobooks/reference/book2` | `data/books/book2.txt` | Move test books to active data directory |

---

## What goes to archive/ (everything IPA-related)

| What | Why archived |
|------|-------------|
| `src/core/` | IPA pipeline. Letter-by-letter approach produced unusable audio |
| `src/dialects/` | Dialect rules for IPA pipeline. Not needed for audiobook text processing |
| `src/integrations/` | eSpeak + Polly. Azure audiobooks use azure_client.py directly |
| `src/main.py` | IPA pipeline orchestrator |
| `tests/` (329 tests) | All test the IPA pipeline, not audiobook processing |
| `data/dictionaries/masterTTS.json` | Phonetic lookup for IPA. Audiobooks don't do pronunciation |
| `tools/` | All POC tools. Prototype findings referenced but code not reused directly |
| `scripts/` | Demo and test scripts for IPA/Polly |
| `app.py` | Flask API for IPA pipeline |
| `audio/` | Generated test audio from IPA/Polly/Azure experiments |

---

## output/ directory convention

Each book gets its own output directory named after the book file (minus extension):

```
output/
├── awalad-7aretna/          # From data/books/awalad-7aretna.txt
│   ├── ingestion/
│   ├── chapters/
│   ├── segments/
│   ├── ssml/
│   └── audio/
├── book2/                   # From data/books/book2.txt
│   └── ...
└── my-new-book/             # From data/books/my-new-book.pdf
    └── ...
```

**Gitignored.** Output is working data, not source code. Audio files can be large.
Review CSVs are ephemeral — you review, fix, re-generate.

---

## Migration steps

**Phase 1: Archive (one commit)**
1. Create `archive/` directory
2. Move into archive: `src/`, `tests/`, `scripts/`, `tools/`, `audio/`, `tasks/`, `templates/`, `demo_output/`, `app.py`, `KNOWLEDGE_BASE.md`, `attached_assets/`
3. Move `data/dictionaries/` and `data/test_cases/` into `archive/data/`
4. Keep at root: `docs/`, `.env.example`, `.gitignore`, `requirements.txt`, `pyproject.toml`, `CLAUDE.md`, `README.md`

**Phase 2: Scaffold (same commit or next)**
5. Create `src/audiobook/` with `__init__.py`
6. Create `tests/audiobook/`
7. Create `data/books/`
8. Copy test books from `docs/02-features/azure-audiobooks/reference/` to `data/books/` (copy, not move — archive stays intact)
9. Add `output/` to `.gitignore`
10. Update `requirements.txt` (audiobook deps: pdfplumber, azure-cognitiveservices-speech)
11. Update `CLAUDE.md` and `README.md` to reflect new structure

**Phase 3: Build (one POC at a time)**
12. Start POC-1 in `src/audiobook/ingest.py` (fresh code)
13. When POC-3 starts, evolve `06_simplified_detector.py` into `dialogue.py`
14. When voice output starts, evolve `azure_integration.py` into `azure_client.py`

Don't build everything upfront. Archive once, scaffold once, then fill as you build each POC.
