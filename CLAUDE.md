# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

<!-- AURORA:START -->
# Aurora Instructions

These instructions are for AI assistants working in this project.

Always open `@/.aurora/AGENTS.md` when the request:
- Mentions planning or proposals (words like plan, create, implement)
- Introduces new capabilities, breaking changes, or architecture shifts
- Sounds ambiguous and you need authoritative guidance before coding

Use `@/.aurora/AGENTS.md` to learn:
- How to create and work with plans
- Aurora workflow and conventions
- Project structure and guidelines

## MCP Tools Available

Aurora provides MCP tools for code intelligence (automatically available in Claude):

**`lsp`** - LSP code intelligence with 3 actions:
- `deadcode` - Find unused symbols, generates CODE_QUALITY_REPORT.md
- `impact` - Analyze symbol usage, show callers and risk level
- `check` - Quick usage check before editing

**`mem_search`** - Search indexed code with LSP enrichment:
- Returns code snippets with metadata (type, symbol, lines)
- Enriched with LSP context (used_by, called_by, calling)
- Includes git info (last_modified, last_author)

**When to use:**
- Before edits: Use `lsp check` to see usage impact
- Before refactoring: Use `lsp deadcode` or `lsp impact` to find all references
- Code search: Use `mem_search` instead of grep for semantic results
- After large changes: Use `lsp deadcode` to find orphaned code

Keep this managed block so 'aur init --config' can refresh the instructions.

<!-- AURORA:END -->

# Sawt — Arabic Audiobook Production

Produce Arabic audiobooks from raw book files (EPUB/DOCX/TXT) using neural TTS. Two-voice
(narrator + dialogue) for fiction is the product. Multi-voice per-character is **closed** —
Azure Arabic has only 2 voices per dialect, so characters C through Z would share voices anyway.

**Text processing IS the product.** Once text is correctly broken into parts, SSML is just
markup and TTS is a commodity API call. Let the TTS engine handle pronunciation — we handle
structure (chapters, paragraphs, dialogue boundaries). An earlier IPA/phoneme pipeline tried to
control pronunciation letter-by-letter and produced robotic, unintelligible audio. It is
archived in `archive/` as a learning artifact and shares **zero** code with this pipeline.

## Dev Rules

**POC first.** Validate logic with a ~15min proof-of-concept before building. Cover happy path
+ common edges. POC works → design properly → build with tests. Never ship the POC.

**Build incrementally.** Small independent modules. Each must work on its own before integrating.

**Dependency hierarchy — follow strictly:** vanilla language → standard library → external
(only when stdlib can't do it in <100 lines). External deps must be maintained, lightweight,
widely adopted. Exception: always use vetted libraries for security-critical code.

**Lightweight over complex.** Fewer moving parts, fewer deps, less config. Simple > clever.
Readable > elegant.

**Open-source only.** No vendor lock-in. Every line of code must have a purpose — no
speculative code, no premature abstractions.

## Commands

```bash
pip install -r requirements.txt

pytest tests/ -v                                    # Full suite (491 tests)
pytest -m "not corpus" -q                           # Skip tests that need the git-ignored data/books corpus
SAWT_CI=1 pytest tests/ -q -rs                      # What CI runs: fails if any non-corpus test skips
pytest tests/audiobook/dialogue/ -v                 # One module
pytest tests/audiobook/dialogue/test_core.py::TestDetectMarkers -v            # One class
pytest tests/audiobook/dialogue/test_core.py::TestDetectMarkers::test_em_dash -v   # One test

python -m src.audiobook.runner <book-or-folder> [--ssml] [--non-fiction] [--name N]   # Steps 1-4 → <book dir>/<name>_sawt/
python -m src.audiobook.runner --list | --retry <job> | --rename OLD NEW | --import-existing   # also --new-job, --yes (skip overwrite confirm); History in ~/.config/sawt/jobs.json (SAWT_HOME overrides)

python -m src.audiobook.ui [--port 8765] [--no-open]   # Local UI on http://127.0.0.1:8765 (jobs, live run log, history)
```

Note: `.env.example` is stale — it still lists AWS Polly keys. The code uses Azure
(`AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`). TTS credentials are only needed for audio
generation (POC-5); everything through SSML runs offline.

## Pipeline Architecture

Five stages. Each is a package under `src/audiobook/` with the implementation in `core.py`.
Tests mirror the structure exactly: `tests/audiobook/<module>/test_core.py`.

```
data/books/{epub,docx,txt}/book.*
  ├─ ingest/     → output/{format}/{book}/01_ingestion/  clean_text.txt + paragraphs.csv
  ├─ chapters/   → output/{format}/{book}/02_chapters/   chapter_*.txt + chapters.csv
  ├─ dialogue/   → output/{format}/{book}/03_segments/   ssml/*.csv + review/*.txt + segments.csv
  ├─ ssml/       → output/{format}/{book}/04_ssml/       chapter_*.ssml + voice_config.json
  └─ (POC-5)     → output/{format}/{book}/05_audio/{provider}/chapter_*.mp3
```

| Module | Status | Entry point |
|--------|--------|-------------|
| `ingest/` | Production ready | `ingest(book_path, output_dir)` |
| `chapters/` | Production ready | `split_book(ingestion_dir)` |
| `dialogue/` | Production ready (~95%) | `segment_book(chapters_dir)`, `sync_review(segments_dir)` |
| `ssml/` | Done (POC-4) | `generate_book_ssml()`, `make_voice_config()` |
| `runner/` | Done (module 0, CLI only) | `run_book()`, `retry_job()`; `python -m src.audiobook.runner` |
| `ui/` | Modules 2 + 3 built (jobs, live log, history, artifacts tab, file viewer, stop/delete, re-attach); module 3 real-browser check done | `make_server()`, `serve()`; `python -m src.audiobook.ui` |
| `voice_pool/`, `shared/` | **Stubs** — docstrings only, no code yet | — |
| POC-5 audio generation | **Next** — not built | — |

`output/` is gitignored working state, not build artifacts. Regenerate freely.

### The two rules that shape everything

**POCs are isolated by DATA boundaries, not code imports.** Each stage reads the previous
stage's *file output*, never its Python. Any stage can be rewritten without breaking the next.
Don't add cross-stage imports — that would collapse the property the whole design rests on.

**Every stage emits a CSV for human review**, reviewed chapter by chapter. Don't advance to the
next stage until the current chapter's output is verified. `03_segments/` is the universal
hand-off point for all TTS providers.

### Module conventions

`__init__.py` re-exports from `core.py` via `from .core import *`, then explicitly imports the
underscore-prefixed helpers that tests need (`_find_dialogue_colon`, `_strip_diacritics`,
`_find_dominant_delimiter`, …). If you add a private helper that tests exercise, add it to that
explicit import list.

Constants are named, not magic (`MAX_UNIT_CHARS = 25_000`, `SPEECH_ATTRIBUTION_LEN = 150`).
Errors carry pipeline context (`IngestionError(ValueError)`). Return types are `TypedDict`
(`NormStats`, `IngestSummary`, `VoiceConfig`). Use `logging`, not `print()`.

## Domain Knowledge (hard-won — don't relitigate)

**Arabic text**
- NFKC normalization eliminates 100% of Arabic Presentation Forms (U+FE70–FEFF). Ornate
  parentheses (U+FD3E/FD3F) survive it and are replaced manually.
- Harakat (diacritics, U+064B–065F, U+0670) must be stripped before any speech-verb regex.
- **PDF is out of scope, permanently.** Arabic PDFs store word spacing as positional
  coordinates, not space characters — words extract fused (`أﻗﻄﻊُﻫﺬا`). PyMuPDF closed this
  wontfix; no OSS tool solves it. PDFs stay in `data/books/pdf/` for reference only.

**Dialogue detection** (`dialogue/core.py`)
- **The colon `:` is THE universal Arabic dialogue marker** — not quotation marks. Attribution
  always comes *before* the quote.
- Marker priority: em dash → colon → trailing colon → plain (narrator).
- **Guillemets `«»` are NOT dialogue.** They're scare quotes and inner thoughts. Voice-switching
  for a 3-word `«phrase»` mid-narration is jarring. Deliberate decision — don't "fix" it.
- **No continuation heuristic.** A plain paragraph after dialogue resets to narrator. Arabic
  authors mark every speaker turn; the heuristic caused more false positives than it solved.
- Colon filtering: skip time colons (`١٢:٣٠`), URLs, heading-style trailing colons. Text
  <150 chars before a colon assumes dialogue; ≥150 chars requires an explicit speech verb in
  the last 100. Passive `قيل` is excluded from the verb regex.

**Chapter splitting** (`chapters/core.py`)
- Split on delimiter OR 25K chars, whichever comes first. **Never cut mid-paragraph** —
  paragraphs are atomic through the entire pipeline.
- 25K is the Azure ceiling: 64KB SSML/request ÷ ~2 bytes per Arabic UTF-8 char, minus markup.
  (The 50-tag limit counts *distinct* voice names — two-voice never approaches it.)
- Detection picks the *dominant* delimiter per book and ignores stray noise. 5 of 12 test books
  have no delimiters at all — pure size-based fallback is a supported path, not a failure.
- **EPUB spine is unreliable** (only 1 of 5 Hindawi EPUBs maps cleanly; 3 are single-file).
  Text-based regex on `clean_text.txt` is primary; spine is a bonus.
- DOCX Shamela files carry page markers `(1/406)` — filter as noise, never split on them.

**Voice & TTS**
- **Fiction = two voices. Non-fiction = single voice, skip dialogue detection entirely.**
  Quranic verses, `قال العلماء:`, and scholarly citations are not dramatic dialogue — the
  detector produces false positives on them by design.
- **FF (female narrator + female dialogue) is the smoothest pairing**, validated in listening
  tests. Same-gender pairings are the most cohesive.
- **One dialect per book, matched to the book's origin.** Egyptian author → `ar-EG`, Levantine
  → `ar-SY/JO/LB`. Dialect changes meaning, not just accent. Never mix within a book.
- Azure Arabic has **zero** `mstts:express-as` support (no emotion styles, no HD voices). Only
  rate/pitch/volume. Emotion work is blocked on the platform, not on us.
- **Production provider: Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`, decided 2026-10-05).
  Sulafat narrator + Leda dialogue, with `speech_metadata.style` direction. It beat ElevenLabs
  in listening tests at about Google cost (~$54 for 5 novels with batch pricing vs ElevenLabs
  ~$167). Its content filter blocks some violent literary passages in context; split and retry,
  and fall back to Google Chirp3-HD (same voice names). OpenAI has no Arabic voices. Mishkal
  diacritization makes pronunciation *worse* — send plain text.

## Docs

| Topic | Location |
|-------|----------|
| Product requirements (single source of truth) | `docs/product/prd.md` |
| Learnings from POCs and research | `docs/product/learnings.md` |
| Documentation hub | `docs/README.md` |
| POC results (1–4) | `docs/logs/POC{1,2,3,4}_RESULTS.md` |
| Voice inventory (19 pairing-tested voices) | `docs/logs/final_voices.csv` |

Some docs still reference the old flat layout (`src/audiobook/ingest.py`,
`docs/02-features/azure-audiobooks/…`). The tree above is authoritative.

`archive/` holds the superseded IPA phonological pipeline. Reference only — never extend it.

<!-- MEMORY:START -->
@.claude/remember/MEMORY.md
<!-- MEMORY:END -->

<!-- AGENT_RULES:START -->
Consult when building something new or adding a feature — a standards guide, not hot
context like MEMORY.md above:
.claude/remember/AGENT_RULES.md
<!-- AGENT_RULES:END -->

<!-- DOCS_INDEX:START -->
Docs map: `docs/index.md` — every doc in this project, with line counts.
Search this corpus instead of reading it whole: `/docs-builder search <query words>`
<!-- DOCS_INDEX:END -->
