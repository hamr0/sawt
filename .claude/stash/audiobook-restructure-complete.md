# Stash: Audiobook Pipeline Restructure Complete

**Timestamp:** 2026-02-05
**Branch:** main
**Last commit:** 8089e97 — refactor: Archive IPA pipeline, scaffold audiobook production structure

---

## What Happened This Session

1. **Strategic analysis** — Discussed single/two/multi-voice approaches with market research. Concluded: two-voice first (narrator + dialogue), multi-voice is stretch goal.

2. **Plan created** — `docs/02-features/azure-audiobooks/PLAN.md`
   - POC-1: Book ingestion (PDF/TXT → clean text)
   - POC-2: Chapter detection & splitting
   - POC-3a: Dialogue detection + two-voice output (THE GOAL)
   - POC-3b: Character attribution + multi-voice (THE BEAST, stretch)
   - POC-4: Emotion/prosody (future layer)

3. **Repo structure designed** — `docs/02-features/azure-audiobooks/REPO_STRUCTURE.md`
   - POCs isolated by data boundaries (file output), not code imports
   - CSV review at every stage, chapter-by-chapter review cadence
   - One file per POC, start simple

4. **Repo restructured and pushed** (360 files moved):
   - IPA pipeline → `archive/` (329 tests, 5 dialects, Polly, Flask — unusable audio output)
   - Azure TTS POC reference → `docs/02-features/azure-audiobooks/reference/` (7 prototype iterations, production detector, research findings)
   - New skeleton: `src/audiobook/` (7 modules), `tests/audiobook/` (4 test files), `data/books/` (2 test books)
   - Updated: README.md, CLAUDE.md, requirements.txt, .gitignore

---

## Key Decisions Made

| Decision | Choice |
|----------|--------|
| Voice approach | Two-voice primary, multi-voice stretch |
| Pronunciation | Let Azure handle it (plain text), NOT IPA phoneme control |
| Dialect switching | None — a book is a book |
| Language | Python (PDF libs, Azure SDK, existing prototypes) |
| Repo strategy | Same repo, IPA archived, audiobook is active project |
| POC isolation | Data boundaries between POCs (file output contracts) |
| Review workflow | CSV at every stage, chapter-by-chapter |
| LLM usage | Minimize — code-first, LLM only for text detection where proven |

---

## Active Structure

```
src/audiobook/          # Skeleton modules (ingest, chapters, dialogue, azure_client, voice_pool, ssml, review)
tests/audiobook/        # Test skeletons (test_ingest, test_chapters, test_dialogue, test_ssml)
data/books/             # awalad-7aretna.txt, book2.txt
output/                 # Per-book working output (gitignored)
docs/02-features/azure-audiobooks/
    PLAN.md             # Execution plan
    REPO_STRUCTURE.md   # Directory layout and migration
    reference/          # Old azure_tts POCs (prototypes, production detector, research)
archive/                # IPA pipeline (preserved, not active)
```

---

## Next Steps

- **POC-1: Book Ingestion** — implement `src/audiobook/ingest.py`
  - PDF text extraction (pdfplumber)
  - TXT reading with encoding detection
  - Arabic encoding normalization (Presentation Forms → Standard)
  - Output: clean_text.txt + paragraphs.csv
  - Test with awalad-7aretna.txt first, then a PDF book

---

## Important Context

- User is building for profit + personal goal (making Arabic audiobooks accessible)
- MEA audiobook market: $237.6M (2024) → $1.24B (2030), 31.5% CAGR
- Text processing IS the product. SSML is just markup after that.
- Review was painful in prototypes — CSV workflow developed to manage it
- Colon `:` is primary Arabic dialogue marker (not quotation marks)
- Production detector: 63.5% attribution, 99.7% text preservation (prototype 06)
- Azure free tier: 5M chars/month, 12 months. ~$8-12 per 150-page book.
