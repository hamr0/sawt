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

Status: Spec signed off 2026-10-05. Modules 0, 1, 2 and 3 built (feat/runner, feat/ui); module 3 real-browser check pending.

### Problem & goal

Take a book file through the pipeline without the terminal. Steps 1–4 run straight through (mechanical, free); inspect each step's output by clicking.

### Go / no-go

The runner chains steps 1–4, stops on an error, and resumes from the failed step using only files on disk, with every completed step's output untouched. Proven first from the command line (module 0). If it fails, no UI.

### Out of scope

Hosting, other users, logins; a database; editing files in the browser; audio generation (step 5 gets its own spec); LLM calls; PDF and legacy `.doc`; voice/dialect pickers; accuracy-based auto-stops; styling beyond plain.

### Behaviour

| Area | Spec |
|------|------|
| Input | A local path box (not a browser upload — output must sit next to the source, and uploads don't reveal the source path). Accepts one file, or a folder that is scanned for `.epub`, `.docx`, `.txt`; anything else is skipped and listed. Legacy `.doc` is rejected with a reason. |
| Job | One job = one book = one card. Re-running a book appends a new dated run to the same job; a separate job/card exists only when the user explicitly chooses "new job" for the same book. Later, regenerating with a different TTS engine or API key is another run on the same job (audio lands in `05_audio/{provider}/`). |
| Name | Every job has a unique name, defaulting to the book's file name, editable. Duplicates rejected with a message. |
| Output | `<book's folder>/<job name>_sawt/` containing `01_ingestion/ … 04_ssml/` (`05_audio/` later). Folder name fixed at job creation; renaming a job changes only its display label. |
| Run | Steps 1–4 straight through. SSML is opt-in (off by default). Fiction/non-fiction toggle, default fiction; non-fiction skips dialogue detection. A folder's books run one after another; one run at a time. |
| Stops | Only on an error, or at the fixed gate before the paid audio step. In v1 every successful run ends "ready for audio — paused". When audio exists, the gate gets a "Generate audio" button with estimated cost. |
| Errors | ✗ + error message; Retry reruns from the failed step. |
| Re-run | Overwrites steps 1–4 output in that job's folder. Before starting, a warning: overwriting the last run's files — start a new job instead to keep them. Old runs' logs stay in history; old files do not. |
| Progress | A live log, one line per step with ✓/✗, plus `>` detail lines with numbers (e.g. "> 415 paragraphs, 81,025 chars", "> 4 chapters (size-based fallback)", "> 619 segments, 43% dialogue", "generating SSML — skipped (off)", "ready for audio — paused before paid step"). |
| History | One file `~/.config/sawt/jobs.json`, one entry per job: name, source path, output path, list of runs; each run: date, settings, per-step status, `>` log lines, errors. Single writer (the runner), atomic writes. A job whose folder is gone shows as missing. The 12 books already in the repo's `output/` are imported into history in place (not moved); new runs follow the next-to-source rule. |
| Layout | Left pane = one card per job (name, latest run status, date). Right pane tabs: `[1] Run` live/selected run log + details; `[2] History` all runs of this job, newest first, dated, expandable to log; `[3] Artifacts` one entry per step folder with an "open folder" button (opens in the file manager) and clickable files. |
| Look | Monospace, light and plain, with a dark theme; style reference is the owner's bareloop UI (bracketed buttons, numbered tabs, `[✓]`/`[×]` status marks, pale blue-grey palette). Chosen from 5 `/live-canvas` variations. |
| Stack | Python standard library HTTP server, no new dependencies. Binds 127.0.0.1 only; opens folders/serves files only inside known job `_sawt/` folders and the repo `output/`. |

### Modules (in order; each proven before the next)

| # | Module | Proof |
|---|--------|-------|
| 0 | Runner, CLI only, POC first: takes a path, runs steps 1–4, writes `jobs.json`, retries from the failed step. | Real runs on 2–3 test books plus tests; one run forced to fail, then retried. |
| 1 | Look: 5 `/live-canvas` variations; owner picks one. | Owner picked variant D (light + dark themes, independently scrolling job list). |
| 2 | UI shell: path input, start, live log, job cards, history. | Tests (337 passing, including a Node fake-DOM page test) plus a real-browser check of themes, live run, new-job flow and Arabic paths/names. |
| 3 | Artifacts tab: step folders, open-folder, file links. | Tests (383 passing: listing, path guard, viewer, open-folder, Node fake-DOM tab test); real-browser check pending. |

After the last module: propose `/self-review`.

**Done =** the owner points the UI at a book or folder, watches steps 1–4 tick through, opens every step folder from the page, and finds the job and its runs in history after a server restart.

### Decided during build

- On first launch with no history, an `[ import existing output/ ]` button imports the repo's existing output folders.
- When the typed book already has a job, a "new job" checkbox appears. Unchecked = a new run on the existing job.
- One run at a time: while a run is going, other start/retry actions are refused with a message.
- A job left "running" after a crash or server stop shows as interrupted, with Retry available.
- In a folder run, a book whose job name is already taken is skipped and listed; the rest of the folder still runs.
- Arabic display: paths render left-to-right with segments that break only at `/`; names and paths embedded in messages are bidi-isolated and don't wrap.
- Folder pick list: when the path box holds a folder, the detected books (one level deep) appear as rows, updating as the path is typed. Each row has a tick (all ticked by default), the file name, an editable job name and a status ("new job" or "existing job → new run", the latter with the "new job" checkbox). `[ all ]` / `[ none ]` sit above; skipped files are listed greyed with their reason. Names are checked live against existing jobs and other ticked rows; `[ start N books ]` runs only the ticked rows, in list order, and is disabled with 0 ticked or any name error. A single file keeps the plain form. `GET /api/scan?path=` feeds the list; `POST /api/runs` takes `{"books": [{path, name, new_job}]}` and re-validates every path and name. The single-path form of `POST /api/runs` is kept (single files, CLI-style tests).
- Artifacts layout: every step block starts collapsed (header row only; reset on tab open and job change). Headers show the folder name without underscores, the file count and the newest file's date; a missing step is a greyed `04 ssml · not produced` header. Subfolders get a muted `dir/ · N files` subheader, root files come first; files are a responsive grid of `name (size)` cells, up to 4 columns, with ellipsis and the full name in a tooltip.
- Queue view: every queued book has a card at once (`[…] queued`, "2 of 5"), built from worker status, so books that never ran write nothing to history. Selecting one shows its Run tab with "queued — position N".
- Job actions live in an action row at the top of the Run tab: `[ retry ]` (restart), `[ stop ]`, `[ delete ]`. `[ stop ]` clears the queue and lets the running book finish its current step (cancel flag checked between steps, never mid-step); the run ends `stopped` with a log line `■ stopped by user after <step>`, and Retry resumes from the next undone step like a failed run.
- `[ delete ]` asks first ("Remove <name> from history? Files on disk stay: <path>"), removes the job from `jobs.json` only, and is refused while the job is running or queued (400) or while any run is active (409, jobs.json has one writer).

- Job list: a search box filters cards live (case-insensitive, on job name or source file name; Arabic works) with a "jobs (3 of 14)" count and a `[ × ]` clear; client-side only, and the selected job stays selected even when filtered out. Cards are two lines: `<mark> <name> <date> · N runs`, then `<status word> · <explanation>` (partial / complete / failed · step / running · step / queued · N of M / stopped · after step / interrupted / imported / missing; "missing" wins, "ready for audio — paused" shows as partial). One JS function maps latest run + worker status to the card; the Run-tab log line is unchanged.
- `jobs.json` is shared safely: every write is read → apply only this writer's change → atomic write, under an exclusive `fcntl.flock` on a sidecar `jobs.json.lock` (no lock, one logged warning, where fcntl is missing). Each job has a stable `id` (uuid4 hex; old files get a deterministic id derived from the output folder, persisted on the next save). A run saves only its own job's runs, matched by id, so a rename made meanwhile survives; a job deleted mid-run is not resurrected (the run logs it and stops). Deleting is therefore allowed while another job runs; it is still refused for the job that is running or queued.

- Job names (CLI and UI, one `_check_name`): trimmed; Arabic, spaces and dashes allowed; rejected when empty, starting with a dot, containing `/` or `\`, containing control/format characters (newlines, tabs, bidi marks) or longer than 100 characters. The page mirrors the rules live on each pick-list row; the server re-validates.

### Module 3 spec (signed off 2026-10-05)

- **Tab:** one block per step folder present in the job's output, in order `01_ingestion` … `04_ssml`, plus `05_audio` if present. Header = folder name, file count, `[ open folder ]`. Files listed under it grouped by subfolder (`03_segments/ssml/`, `review/`), each with relative path and size. Every block starts collapsed (header row only); clicking the header expands it, and expansion resets whenever the tab is opened or the job changes. Missing step → "<folder> — not produced". Output folder gone → "folder missing" plus the path (LTR styling).
- **Endpoints:** `GET /api/jobs/<name>/files` (listing); `POST /api/jobs/<name>/open` `{"path": rel folder or ""}` opens the system file manager (`xdg-open` / `open` / `os.startfile`; argument list, no shell, not waited on; module-level function so tests monkeypatch it); `GET /view?job=&path=` read-only viewer. All behind the existing host check.
- **Viewer:** UTF-8 HTML with its own strict CSP and no scripts. `.txt`/`.ssml`/`.json`/`.xml` in `<pre dir="auto">`, each line its own `dir="auto"` element; `.csv` as a table (stdlib `csv`, sticky header, `dir="auto"` cells); everything `html.escape`d. Other extensions download (`Content-Disposition: attachment`). 5 MB cap, above it a message instead of content. Same monospace look and light/dark tokens (`prefers-color-scheme`). File links open in a new tab (`target="_blank" rel="noopener"`).
- **Path guard:** paths are relative to the job's recorded `output` (new `_sawt/` and imported jobs alike). Absolute paths and NUL bytes are refused; the rest is `Path.resolve()`d (symlinks followed) and must be `is_relative_to(output.resolve())`. 403 on absolute, `..` escape, symlink out, NUL; 404 unknown job. The listing skips symlinked dirs and files resolving outside. `/open` uses the same guard and only accepts directories.
- **Freshness:** listing reloads when the tab opens, when the job changes while it is open, and when a run finishes. No file watching.
- **Out of scope:** editing, audio preview, search.

### Open questions (non-blocking)

- Accuracy signals for auto-stop: ingest normalization stats, chapters-concatenate-to-source check, dialogue % far outside the 31–45% seen across the five novels.
- Mixed Arabic/English text in a book — how stages and TTS handle embedded Latin script.
- Current SSML voice config cannot produce an FF pairing (Azure only).
- Single-voice SSML for non-fiction.
- Step 5: single-sentence content-block handling (Chirp3-HD fallback and/or flag in CSV).
- Step 5: first full book (rest of *Tharthara Fawq al-Nil* vs *Awlad Haretna*).
- No way to cancel a queued folder run once started. — resolved: [ stop ]
- The UI font loads from the network (Google Fonts); offline it falls back. Decide whether to bundle it or drop it. — resolved: bundled locally

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
