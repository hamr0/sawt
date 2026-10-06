---
title: Architecture Decisions
theme: architecture-decisions
sources:
  - docs/archive/PLAN.md
description: Architecture decision table, repo structure and data flow between POCs.
---

# Architecture Decisions

This page covers the repo layout, how data moves between POCs, and the table of architecture decisions with their rationale. Details of the layout live in `docs/product/REPO_STRUCTURE.md` (docs/archive/PLAN.md:243-246).

## Repo structure

The IPA pipeline is archived. The audiobook pipeline is the active project (docs/archive/PLAN.md:245-246).

| Path | Status | Contents |
|------|--------|----------|
| `src/audiobook/` | ACTIVE | Audiobook production pipeline |
| `tests/audiobook/` | ACTIVE | Audiobook tests |
| `data/books/` | ACTIVE | Input books |
| `output/` | ACTIVE | Per-book working output (gitignored) |
| `docs/` | ACTIVE | Documentation |
| `archive/` | PAUSED | IPA pipeline preserved intact |

(docs/archive/PLAN.md:248-273)

### Modules in `src/audiobook/`

| Module | Role |
|--------|------|
| `ingest.py` | POC-1: EPUB/DOCX/TXT to clean text |
| `chapters.py` | POC-2: chapter detection and splitting |
| `dialogue.py` | POC-3: dialogue detection |
| `azure_client.py` | Azure SDK wrapper |
| `ssml.py` | POC-4: SSML generation + voice selection (voice_pool folded in) |
| `review.py` | CSV export at every stage |

(docs/archive/PLAN.md:250-256)

### Input and archive folders

- `data/books/epub/`: EPUB books, the primary content source.
- `data/books/docx/`: DOCX books, author submissions.
- `data/books/txt/`: TXT files, internal/corpus use.
- `data/books/pdf/`: PDF archive, descoped, reference only.
- `output/pdf/`: PDF test outputs, archived and descoped.

(docs/archive/PLAN.md:258-264)

The archive holds `src/` (core/, dialects/, integrations/, utils/), `tests/` (329 tests), `data/` (masterTTS.json, test cases), `scripts/` (demo, test scripts), `tools/` (all tools including prototype history) and `app.py` (Flask API) (docs/archive/PLAN.md:266-272).

## Data flow between POCs

POCs are isolated by file output, not code imports (docs/archive/PLAN.md:276).

```
data/books/{epub,docx,txt}/book.*
    | ingest.py
output/{format}/book/01_ingestion/clean_text.txt + paragraphs.csv      <- REVIEW
    | chapters.py
output/{format}/book/02_chapters/chapter_*.txt + chapters.csv           <- REVIEW
    | dialogue.py
output/{format}/book/03_segments/segments.csv                           <- REVIEW (book summary)
output/{format}/book/03_segments/ssml/chapter_*.csv                     <- machine segments
output/{format}/book/03_segments/review/chapter_*.txt                   <- human review text
    | [OPTIONAL] ssml.py (Azure only: voice selection + SSML templates)
output/{format}/book/04_ssml/chapter_*.ssml + voice_config.json
    | audio_gen.py (multi-provider: Google/ElevenLabs/Azure)
output/{format}/book/05_audio/{provider}/chapter_*.mp3
```

(docs/archive/PLAN.md:278-291)

Hand-off rules:

- The step 3 segments CSV is the universal hand-off point (docs/archive/PLAN.md:293).
- Google and ElevenLabs skip step 4: plain text per segment plus silence concatenation (docs/archive/PLAN.md:294).
- Azure can use the step 4 SSML or build it inline from step 3 (docs/archive/PLAN.md:295).

## Decision table

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Input formats | EPUB + DOCX (first-class), TXT (internal) | EPUB = content source, DOCX = author format. PDF descoped, intractable. |
| Language | Python | EPUB/DOCX libs, Azure SDK, existing prototypes, Arabic text handling |
| Pronunciation | Let Azure handle it (plain text) | IPA letter-by-letter approach was unusable, validated the hard way |
| Voice per book | Single dialect, matched to book origin | A book is a book. Dialect changes meaning, not just accent. Match voice dialect to author/setting |
| Repo structure | Same repo, IPA archived | Zero code overlap. Archive preserves history without interference |
| Dialogue detection | Code-first (state machine + patterns) | LLM only if code can't solve it |
| Review workflow | CSV export, chapter-by-chapter review | Proven in prototypes, manageable scope |
| Character names source | External list (Wikipedia, book info) | Heuristic extraction had 19% false positive rate |
| POC isolation | Data boundaries between POCs | Each POC reads previous POC's file output, not its code |
| SSML generation | Templates + voice selection in one module | voice_pool folded into ssml; two-voice is a 3-field config, not a separate module |
| Voice selection | M/F switch per dialect, not prosody-only | Azure Arabic prosody (rate/pitch/volume) too crude to signal dialogue alone; voice switch creates clear contrast |
| Voice sampling | 8-10 test files across 3 dialects, human picks | Don't pre-optimize: listen first, then commit to defaults |
| Audio stitching | Per-chapter files, concatenated | Matches review workflow (review by chapter) |
| PDF handling | Out of scope | No OSS tool extracts Arabic PDF text correctly. See research. |

(docs/archive/PLAN.md:829-844)
