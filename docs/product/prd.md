---
title: Sawt Product Requirements
description: Current product requirements for Sawt, the Arabic audiobook pipeline - scope, five-stage pipeline, TTS and voice, the local UI + runner to build next, and success criteria.
updated: 2026-10-05
---

# Sawt (صوت) - Product Requirements

## 1. Product

Sawt turns a raw book file into an Arabic audiobook. Tagline: **كل كتاب له صوت** ("Every book has a voice").

**Core idea.** Text processing is the product. Once text is correctly broken into chapters, paragraphs and narrator/dialogue segments, SSML is markup and TTS is a commodity API call. Sawt owns structure; the TTS engine owns pronunciation.

**Who it is for** (in priority order)

1. Young Arab authors and small publishers who write in DOCX and cannot afford $1,000+ human narration.
2. Listeners, reached through published audiobooks rather than direct marketing.
3. Institutions, later, once the product is proven.

Near-term use is also internal: produce free audiobooks from the Hindawi CC-licensed catalog (Egyptian fiction) to build a portfolio and refine the pipeline.

**Why.** Accessibility (make Arabic books listenable) and commercial (the Arabic audiobook market is underserved and growing: $237.6M in 2024 to $1.24B by 2030, 31.5% CAGR). Nobody offers a raw-book-to-audiobook pipeline for Arabic with voice differentiation; competitors either sell a TTS engine or distribute audiobooks others have produced.

**Go-to-market sequence** (details in `docs/product/learnings.md`): free Hindawi audiobooks (YouTube, Spotify/Anghami) -> manual conversion service at $20-40/book -> self-serve web tool at $15-25/book only if demand validates.

## 2. Scope

### Inputs

| Format | Status | Notes |
|--------|--------|-------|
| EPUB | First-class | Cleanest source (born-digital Hindawi). |
| DOCX | First-class | Author submissions; python-docx handles Arabic cleanly. |
| TXT | Internal use | Hindawi text corpus; not user-facing. |
| PDF | **Permanently out of scope** | Arabic PDFs store word spacing as positional coordinates, so words extract fused; no open-source tool solves it. PDFs stay in `data/books/pdf/` for reference only. |

### Content types

| Type | Treatment |
|------|-----------|
| Fiction | **Two voices**: narrator + dialogue. This is the product. |
| Non-fiction | **Single voice**, dialogue detection skipped entirely. Quranic verses, `قال العلماء:` and scholarly citations are not dramatic dialogue and would be false positives. |
| Special cases (Quranic recitation with tajweed, custom multi-voice academic work) | Manual quote, outside the product. |

Genre is chosen by the user (fiction default); there is no automatic genre detection. Positioning line: "Sawt produces multi-voice audiobooks for Arabic fiction. For non-fiction, academic texts or custom projects, contact us."

### Voice and dialect rules

- Per-character multi-voice is **closed**: Azure Arabic ships only 2 voices per dialect, attribution needs ~36% manual review, and rapid switching sounds robotic. Two-voice delivers most of the listening value.
- **One dialect per book**, matched to the book's origin (author first, setting second, publisher third; Hindawi default is Egyptian `ar-EG`). Never mix dialects within a book. Dialect changes meaning, not just accent.

### Principles

- Each pipeline stage reads the previous stage's file output, never its code (data boundaries, not imports).
- Every stage emits a CSV/text artifact for human review, checked chapter by chapter before advancing.
- Code first; an LLM is used only where it demonstrably beats code.
- File-based: no database. Standard library first, minimal dependencies, open-source only.

## 3. Pipeline requirements

Five stages, each a package under `src/audiobook/` with logic in `core.py`; tests mirror the layout in `tests/audiobook/<module>/test_core.py` (259 tests total). Output lives under `output/{format}/{book}/` and is regenerable working state.

| # | Stage | Entry point | Output folder | Human-review artifact | Status |
|---|-------|-------------|---------------|-----------------------|--------|
| 1 | Ingest | `ingest(book_path, output_dir)` | `01_ingestion/` | `paragraphs.csv` (+ `clean_text.txt`) | Built, tested |
| 2 | Chapters | `split_book(ingestion_dir)` | `02_chapters/` | `chapters.csv` (+ `chapter_*.txt`) | Built, tested |
| 3 | Dialogue | `segment_book(chapters_dir)`, `sync_review(segments_dir)` | `03_segments/` | `review/chapter_*.txt` | Built, tested (~95% split accuracy) |
| 4 | SSML | `generate_book_ssml()`, `make_voice_config()` | `04_ssml/` | `chapter_*.ssml` + `voice_config.json` | Built, tested; opt-in |
| 5 | Audio | - | `05_audio/{provider}/` | per-chapter `chapter_*.mp3` | **Not built** |

### Stage 1 - Ingest (EPUB / DOCX / TXT -> clean text)

- Output: `clean_text.txt` and `paragraphs.csv` (paragraph_number, char_count, word_count, first_50_chars), plus a normalization report.
- Preserve paragraph boundaries; paragraphs are atomic through the whole pipeline.
- Normalize Arabic with NFKC (removes all Presentation Forms U+FE70-FEFF); replace ornate parentheses U+FD3E/FD3F manually.
- Strip headers, footers, page numbers and publisher noise; EPUB extraction prefers `<p>` over container `<div>`.
- Errors carry book/stage context (`IngestionError`).
- Done when a human reads the output and confirms: this is the book, nothing missing, nothing garbled.

### Stage 2 - Chapters (clean text -> chapter files)

- Output: `chapter_*.txt` and `chapters.csv` (unit_number, unit_name, level, title, char_count, paragraph_count, split_part, total_splits).
- **Never cut mid-paragraph.** Split on a structural delimiter or at the 25K-char unit ceiling, whichever comes first. 25K is the Azure ceiling (64KB SSML request / ~2 bytes per Arabic char, minus markup).
- Detection runs on `clean_text.txt` (format-agnostic) and picks the dominant delimiter per book, ignoring stray noise. The EPUB spine is a bonus signal only.
- Delimiter hierarchy: part (الجزء/القسم/الباب) > chapter (الفصل) > lone-number paragraph (Eastern or Western digits) > section (مبحث/مطلب/فرع) > front/back matter (مقدمة/تمهيد/خاتمة/إهداء, named by their title). Parent units with no body fold their title into the first child.
- Heading terms followed by a conjunction (`القسم والشرط`) are grammar, not structure.
- Filter Shamela page markers `(1/406)` as noise; never split on them.
- No delimiters is a supported path: pure size-based units (001, 002, ...). Oversized chapters sub-split as `CH1 - 1/2`.
- Decorative dividers and in-chapter sub-headings are not split points. Paragraph length is not a heading signal.
- Done when unit files concatenate to the original text, every unit is under the ceiling, and `chapters.csv` makes each boundary obvious.

### Stage 3 - Dialogue (chapters -> narrator/dialogue segments)

- Applies to fiction only. Binary classification: `narrator` or `dialogue`; no character attribution.
- Output: `ssml/chapter_*.csv` (segment_number, type, char_count, text) - the machine hand-off; `review/chapter_*.txt` - human review with dialogue wrapped in `// dialogue \\`; `segments.csv` - per-chapter summary (segment counts, chars, dialogue ratio).
- **The colon `:` is the primary Arabic dialogue marker**, not quotation marks; attribution comes before the quote.
- Marker priority: em dash (whole paragraph is dialogue) > colon (before = narrator, after = dialogue) > trailing colon with speech verb (narrator; consumes exactly the next paragraph as dialogue) > plain (narrator).
- **Guillemets `«»` are not dialogue** (scare quotes, inner thoughts). **No continuation heuristic**: a plain paragraph after dialogue resets to narrator.
- Colon filtering: skip time colons (`١٢:٣٠`), URLs and heading-style trailing colons. Fewer than 150 chars before a colon assumes dialogue; 150 or more requires an active speech verb in the last 100. Passive `قيل` is excluded. Harakat (U+064B-065F, U+0670) are stripped before verb matching.
- Review loop: edit `review/*.txt` (add/remove `// \\` markers), then `sync_review(segments_dir)` regenerates the CSVs. The review syntax must never collide with source text.
- Done when boundaries are verified chapter by chapter via review and no text is missing. Reviewed on 5 novels; dialogue ratio 31-45%.

### Stage 4 - SSML (segments -> Azure-style SSML)

- Opt-in: required only by providers that consume SSML (Azure). Skipped for plain-text providers.
- Output: `chapter_*.ssml` and `voice_config.json` (book dialect, narrator voice, dialogue voice).
- Narrator and dialogue segments wrapped in their own `<voice>`; adjacent same-voice segments coalesced; context-aware breaks (500ms narrator-to-narrator, 300ms voice transition, 200ms dialogue-to-dialogue); each request within the 25K-char / 64KB limit. The 50-tag limit counts distinct voice names, so two-voice never approaches it.
- Non-fiction: all text in a single voice.

### Stage 5 - Audio (not built)

- Input: `03_segments/ssml/*.csv` (and `04_ssml/` for SSML providers). Output: `05_audio/{provider}/chapter_*.mp3`, chapter by chapter, then a full-book run.
- Requirements: parameterized by book, chapter range, provider and voice pair; coalesce consecutive same-type segments for plain-text providers (short fragments break language detection); pause durations varied within ranges rather than fixed; content-block handling per section 4; batch pricing for full-book runs.

## 4. TTS and voice

**Hand-off.** `03_segments/` is the universal hand-off for every provider: one row per segment, `type` (narrator|dialogue) plus plain text. SSML (stage 4) is a provider-specific rendering of the same data.

| Provider | Input | Role |
|----------|-------|------|
| **Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`) | Segment CSV -> plain text, native two-speaker mode (max 2 speakers) | **Production** |
| Google Chirp3-HD | Plain text, one call per segment, silence concat | Fallback for blocked content (same voice names) |
| ElevenLabs | Plain text per segment | Premium option; not the quality pick |
| Azure Neural | Segment CSV -> SSML | Supported via stage 4; Arabic has no `express-as` styles (rate/pitch/volume only) |
| OpenAI | - | Not viable: no Arabic voices |

**Production voices.** Sulafat (narrator) + Leda (dialogue), FF pairing, with per-speaker `speech_metadata.style` direction: narrator "warm, calm, measured audiobook narration; soft and unhurried"; dialogue "natural, soft conversational delivery; gentle, not dramatic". Female narrator over male dialogue beats the reverse; same-gender pairings are the most cohesive. Voice taste: warm, soft, narrative; not loud or dramatic; Egyptian/MSA preferred, Levantine acceptable, no Gulf. Voice inventory: `docs/logs/final_voices.csv` (19 pairing-tested voices).

**Text sent to TTS.** Plain text, no diacritization (Mishkal makes pronunciation worse). Do not control pronunciation.

**Content filter.** Gemini refuses some violent literary passages in context (deterministic, passage-level). Required handling: split the group in halves, then at sentence boundaries, and retry; if a single sentence is still blocked, fall back to Chirp3-HD with the same voice name. Violent books will hit this more often.

**Cost** (Gemini, ~3.6 output tokens per character measured): ~$32 per 1M chars at standard pricing through 2026-12-31 ($9/M audio tokens); from 2027-01-01, ~$64/M standard or ~$32/M batch. For 5 Mahfouz novels (1.69M chars): ~$54 (standard to 2026-12-31 or batch) vs ~$109 (standard from 2027) vs ~$167 ElevenLabs. Whether blocked requests are billed is unknown.

**Future: per-segment delivery direction.** An optional column on the segment CSV (e.g. excited, scared, whispering) filled by an LLM pass over segment context, fed to Gemini as style direction. Not specced; to be defined when that work starts. Azure cannot use it (no Arabic styles).

## 5. Next build: local UI + runner

A localhost tool for the owner to run the whole flow without the command line.

**Requirements**

1. **Local and single user.** Binds to localhost; one user (the owner); no auth, hosting or multi-tenancy.
2. **One entry gate.** Upload or drop an EPUB, DOCX or TXT (and choose fiction or non-fiction, dialect/voice config).
3. **One runner** executes the stages in sequence by calling each stage's entry point, and records per-stage status (pending / running / done / failed / paused) so the UI can show progress.
4. **Configurable review stops.** The user chooses which stages to pause after (for example after stage 3, to review the dialogue split before paying for audio), then resumes from that point.
5. **Artifact viewing in the browser** per stage: clean text + `paragraphs.csv`; chapter list; segment CSVs + review text; SSML; per-chapter audio player.
6. **Stage 5 is shown as "not built"** until the audio stage exists.

**Constraints**

- Python standard-library web server; no new dependencies.
- Reads and writes the same files under `output/`; stays file-based, no database.
- Stages remain isolated by data boundaries: the runner calls entry points, stages never import each other.
- Review edits go through the existing review/`sync_review` flow.

**Open questions** (to be specced together with the LLM-call work)

- A single sentence blocked by Gemini on its own: automatic Chirp3-HD fallback, a flag in a CSV for human decision, or both.
- First full book to produce end to end: the rest of *Tharthara Fawq al-Nil* or *Awlad Haretna*.
- Mixed Arabic/English text in a book — how stages and TTS handle embedded Latin script (unresolved; carried from the Feb 2026 assumptions).

## 6. Non-requirements / out of scope

- PDF input.
- Per-character multi-voice and character attribution.
- Dialect switching or mixing within a book.
- Phoneme/IPA pronunciation control (the old IPA pipeline is archived and shares no code).
- Emotion via Azure `express-as` (platform does not support Arabic); delivery direction is handled via Gemini style (section 4).
- Real-time TTS, public API, web hosting, multi-user service, accounts or payments (until the self-serve phase is validated).
- Automatic genre detection.
- An LLM-heavy pipeline; LLM use is limited to delivery direction and similar places where code cannot do the job.
- Diacritization (Mishkal).

## 7. Success criteria

**Per-stage definition of done** (all stages): module in `src/audiobook/`; tests pass; run on at least one real book; CSV/review artifact checked chapter by chapter; no text loss (character counts reconcile); edge cases handled or documented.

**A book is done when**

- Ingestion output is the book: nothing missing, nothing garbled.
- Chapter files concatenate to the source text, no mid-paragraph cuts, every unit under 25K chars.
- Narrator/dialogue boundaries are verified through review (about 5-15 minutes of manual review per book is acceptable); no text missing.
- A complete two-voice audiobook (fiction) or single-voice audiobook (non-fiction) exists as per-chapter MP3s with the dialect-matched voice pair; voice switches sound natural on a listen-through.
- The result is repeatable on a second book with different formatting, with no per-book code changes.

**Pipeline-level checks (met so far).** Stages 1-4 run on all 12 test books (5 EPUB, 4 DOCX, 3 TXT) and 259 tests pass. Listening tests picked the production provider and voice pair. Outstanding: stage 5 and a first complete audiobook.

**Product-level.** Two-voice listening is judged clearly better than single voice; pronunciation is judged ~90%+ with Gemini. Business signal: 5+ paying customers for the manual conversion service before building self-serve.

**Known risks** (open): competitor (Lahajati) builds a similar pipeline - mitigate by shipping and building a published-content moat; Gemini content filter on violent passages - mitigated by split-and-retry plus Chirp3-HD fallback; pricing change from 2027-01-01 - mitigated by batch pricing; AI narration quality for fiction - mitigated by two-voice contrast and style direction.

## References

`docs/product/learnings.md` (lessons, decisions, risks), `docs/wiki/definition-of-done.md`, `docs/logs/POC4_RESULTS.md` (voice/provider evidence). Lessons behind these requirements: see learnings.
