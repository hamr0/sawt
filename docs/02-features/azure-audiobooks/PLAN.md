# Arabic Audiobook Production Plan

**Date:** February 2026
**Goal:** Produce Arabic audiobooks from raw book files (EPUB/DOCX) using Neural TTS
**Providers:** Google Chirp3-HD (primary, $1.16/book) + ElevenLabs (premium, $21.74/book) + Azure (baseline)
**Target:** Two-voice audiobooks (narrator + dialogue), FF pairing is smoothest
**Stretch:** Multi-voice (per-character) after two-voice is proven solid — CLOSED (not justified)
**Cost:** Google ~$1-2/book, ElevenLabs ~$20-25/book, Azure ~$8-12/book

---

## Lesson Learned: Why IPA Pipeline Doesn't Apply Here

The repo originally built a full IPA phonological pipeline:
Arabic text → Diacritization → Syllabification → Gemination → Sun Letters → Allophones →
Emphatic Spread → IPA → X-SAMPA → SSML phoneme tags → TTS engine

**It didn't work for audiobooks.** The letter-by-letter phonological processing through SSML
phoneme tags produced output that was too robotic and unintelligible. The assumption that
controlling pronunciation at the phoneme level would improve quality was never validated
early enough — the processing was beautiful and complex, but the output was unusable.

**The audiobook pipeline takes a fundamentally different approach:**
- Send plain Arabic text to Azure neural voices (let Azure handle pronunciation)
- Our job is TEXT STRUCTURE: chapters, paragraphs, dialogue boundaries, character voices
- We don't touch pronunciation at all — Azure's neural models do that better than phoneme-by-phoneme control
- The IPA pipeline (329 tests, 5 dialects) is archived as a learning artifact

**The IPA pipeline and audiobook pipeline share zero code.** LSP confirms 0 imports connect them.
They solve different problems entirely. The IPA work lives in `archive/` for reference.

---

## Format Scope & PDF Decision

### Input Formats

| Format | Role | Status | Rationale |
|--------|------|--------|-----------|
| **EPUB** | First-class (content source) | Active | Best extraction quality. Born-digital = clean paragraphs + word boundaries. |
| **DOCX** | First-class (author input) | Adding | Authors write in Word/Google Docs. python-docx handles Arabic cleanly. |
| **TXT** | Internal-use (bulk corpus) | Supported | Swedish dataset has 1,745 pre-cleaned books. Not user-facing. |
| **PDF** | Out of scope | Descoped | Intractable word-spacing problem. See below. |

### Why PDF Is Out of Scope

Extensive testing and research (Feb 2026) confirmed that Arabic PDF text extraction is an
unsolved problem in the open-source ecosystem:

**What we tested:**
- PyMuPDF — best RTL reading order, but fused words (spacing stored as coordinates)
- pdfplumber — same fused words + worse reading order
- Both tested on 3 Hindawi PDFs: al-Liss wal-Kilab, Tharthara, Zuqaq al-Midaqq

**What we found:**
- Arabic PDFs store word spacing as **positional coordinates**, not space characters
- Words come out fused: `أﻗﻄﻊُﻫﺬا` instead of `أقطعُ هذا`
- PyMuPDF closed the Arabic ligature issue as ["wontfix"](https://github.com/pymupdf/PyMuPDF/issues/2199) (requires HarfBuzz)
- No open-source tool correctly extracts word-spaced Arabic text from PDFs
- The largest Arabic digital library (Shamela, 15K+ books) uses **human transcription**, not OCR
- Even Amazon refuses Arabic PDF uploads for Kindle — requires EPUB/DOCX
- Most Arabic PDFs in the wild are scanned images (require OCR, not text extraction)
- Calibre's Arabic PDF-to-EPUB conversion is [broken](https://bugs.launchpad.net/calibre/+bug/2032531) (text reversed)

**Why this doesn't matter for our pipeline:**
- Hindawi (our primary content source) offers EPUB alongside PDF — same books, clean extraction
- Authors (our primary paying audience) write in DOCX, not PDF
- The books we'd process from PDF are available in better formats
- Engineering time is better spent on downstream pipeline stages

**If PDF becomes needed later**, the recommended path is:
1. PyMuPDF `rawdict` character-bbox gap detection (untried, most promising, no dependencies)
2. PaddleOCR v5 (40%+ Arabic improvement, free, best OSS OCR for Arabic)
3. Mistral OCR API (94.9% accuracy, paid, best-in-class)

Full analysis: [research/ARABIC_PDF_EXTRACTION.md](research/ARABIC_PDF_EXTRACTION.md)

PDF test outputs preserved in `output/pdf/` for reference.

---

## Language Choice: Python

Python is the right tool for this pipeline:
- **EPUB extraction:** ebooklib + BeautifulSoup — proven clean results
- **DOCX extraction:** python-docx — handles Arabic text and paragraph structure cleanly
- **Arabic text handling:** good Unicode/regex support, NFKC normalization
- **Azure Speech SDK:** official `azure-cognitiveservices-speech` package
- **Existing prototype code:** all 7 iterations are Python, patterns are proven
- **CSV handling:** built-in `csv` module, pandas if needed

The bottleneck is Azure API latency (~2-3 sec per minute of audio), not local processing speed.
Switching languages would mean rewriting all prototype knowledge for zero meaningful gain.

---

## Product Scope: Fiction Only

**Decision (Feb 2026):** Sawt is optimized for **fiction** (novels, short stories) with dialogue.

### Why Fiction Only?

Testing on non-fiction revealed the dialogue detector creates false positives:
- **Quranic verses** in `{}` — citations, not dialogue
- **Scientific quotations** — "قال العلماء:" triggers colon detection, but it's indirect speech
- **Scholarly citations** — references to historical figures aren't dramatic dialogue
- Example: `mawsuat-al-ijaz-al-ilmi` (smoking health encyclopedia) marked citations as dialogue throughout

Non-fiction (academic, religious, encyclopedias) works better as **single-voice narration**. The text processing pipeline is designed for fiction's dramatic dialogue, not scholarly references.

### Product Positioning

| Content Type | Sawt Approach | Why |
|-------------|---------------|-----|
| **Fiction** | 2+ voices (narrator + dialogue) | Dramatic exchanges, clear speaker turns, voice switching adds life |
| **Non-fiction** | Single voice (skip POC-3) | Citations aren't "performed" dialogue, needs authoritative consistency |
| **Special cases** | Manual quote (contact us) | Quranic recitation with tajweed, custom multi-voice academic content |

**Documentation:** "Sawt produces multi-voice audiobooks for Arabic fiction. For non-fiction, academic texts, or custom projects, contact us."

### Implementation: Fiction/Non-Fiction Flag

Pipeline wrapper script (future):
```bash
# Fiction (default) — runs all 3 POCs
python pipeline.py --book path/to/novel.epub --genre fiction

# Non-fiction — skips POC-3, goes straight to single-voice SSML
python pipeline.py --book path/to/textbook.epub --genre non-fiction
```

**For now:** Process fiction only. Non-fiction support is deferred until demand validates it.

---

## Voice Approach Refresher

### Single Voice (Non-Fiction Use Case)
- One voice reads everything
- No text processing beyond chapter splitting (POC-1 → POC-2 → SSML)
- **Use case:** Non-fiction where citations/quotes are references, not dialogue
- **Not a core product** — deferred until validated

### Two Voice (Narrator + Dialogue) — PRIMARY GOAL (Fiction)
- Narrator voice for narration, different voice for all dialogue
- Voice switching creates a "listener attention reset" that masks TTS pronunciation artifacts
- Only requires binary classification: "Is this narration or dialogue?"
- Existing colon-based detection achieves 100% dialogue detection rate on fiction
- No character attribution needed — just detect that *someone* is speaking
- Manual review effort: 5-15 min per book (verify narration/dialogue boundaries)
- **Use case:** Fiction, stories, novels with dialogue
- **This is the goal.** Good enough for 70-80% of fiction books

### Multi Voice (Per-Character) — CLOSED (Feb 2026)
- **Decision:** Skip. Not justified by current Azure Arabic capabilities or listener value.
- Azure Arabic has only 2 voices per dialect (1M, 1F) — not enough to distinguish characters C through Z
- Character attribution was 63.5% automated in prototypes — remaining 36.5% needs manual review per book
- Unnamed characters (the officer, the neighbor, the mayor) need catch-all assignment for marginal gain
- Heavy dialogue exchanges (10-line em-dash conversations) create rapid voice-switching that sounds robotic in TTS
- Research consensus: most audiobook listeners prefer a single skilled narrator with tonal shifts over full-cast — multi-voice is the exception (drama adaptations, big-budget productions), not the norm
- Two-voice (narrator + dialogue) captures 90% of the listening value with 10% of the complexity
- **If Azure adds more Arabic voices + emotion styles, revisit.** The segment CSVs from Phase A are the right foundation.

### Emotion/Prosody Enhancement — DEFERRED (waiting on Azure Arabic)
- Azure Arabic voices have **zero** `mstts:express-as` support (no emotion styles)
- English has 30+ styles (angry, cheerful, sad, whispering); Arabic has none
- No HD voices for Arabic either
- When Azure adds emotion support for Arabic, the investment is thin: tag dialogue segments with emotion context, apply `mstts:express-as` style — Phase A segment CSVs are ready for this
- **Not a pipeline task today — a platform capability gap.** Monitor Azure updates.

### What We CAN Do Now: Prosody Tuning (POC-4)
- `<prosody rate="+10%">` on dialogue — slightly faster pace signals conversation vs. measured narration
- `<prosody pitch="+5%">` on dialogue — subtle lift separates dialogue from narrator
- `<break time="300ms"/>` at narrator↔dialogue transitions — audible pause signals voice switch
- These are subtle reinforcements on top of the two-voice switch, not character distinction
- Worth experimenting with in POC-4 SSML generation — a few test renders will calibrate values

### Dialect-Matched Voice Selection

**Principle:** The text IS the dialect. Don't change either — match them.

A Mahfouz novel uses Egyptian literary Arabic with Egyptian colloquial in dialogue.
Reading it with a Gulf voice is like dubbing a British film in a Texas accent — technically
intelligible, culturally wrong. The voice dialect must match the book's linguistic origin.

**Matching rules:**
- **Author's nationality/dialect** → primary signal (Mahfouz → Egyptian, Gibran → Levantine)
- **Book's setting** → secondary signal (novel set in Baghdad → Iraqi voices even if author is Egyptian)
- **Publisher origin** → tertiary signal (Hindawi catalog → Egyptian by default)
- **All voices in a book share the same dialect** — narrator, dialogue, all characters
- **Never mix dialects within a book** — no Gulf narrator with Egyptian dialogue characters

**Azure Arabic voice inventory (14+ neural voices, 7 dialects):**

| Dialect | Code | Voices | Best for |
|---------|------|--------|----------|
| Egyptian | ar-EG | ShakirNeural, SalmaNeural | Mahfouz, Hindawi catalog, most modern fiction |
| Saudi | ar-SA | HamedNeural, ZariyahNeural | Gulf authors, religious texts |
| Levantine | ar-SY, ar-JO, ar-LB | Multiple | Levantine authors (Gibran, Darwish) |
| Maghreb | ar-MA, ar-TN, ar-DZ | Multiple | North African authors |
| Iraqi | ar-IQ | Multiple | Iraqi authors |
| MSA | ar-SA (formal) | HamedNeural | Non-fiction, academic, Quranic |

**For the Hindawi catalog (Phase 1: 20-30 books):** All Egyptian → `ar-EG-*` voices.

**Per-book voice config** (in character registry):
```
book_dialect: ar-EG
narrator_voice: ar-EG-ShakirNeural
dialogue_default_voice: ar-EG-SalmaNeural
```

This config is set once per book and applies to all pipeline stages.

---

## Why Text Processing Is the Product

The actual pipeline difficulty distribution:

```
Raw Book (EPUB/DOCX) ──→ Text Extraction & Cleaning      [DONE - POC-1 ✓]
                  ──→ Chapter Detection & Splitting    [DONE - POC-2 ✓]
                  ──→ Narration vs Dialogue Detection  [DONE - POC-3 ✓ ~95% accuracy]
                  ──→ Character Attribution             [CLOSED - not justified, see Phase B]
                  ──→ SSML + Voice Selection            [NEXT - POC-4]
                  ──→ Azure TTS API                     [EASY - API call]
                  ──→ Audio Stitching                   [EASY - concatenation]
```

Once text is correctly broken into parts, SSML is just wrapping segments in voice tags.
Text processing IS the product. Everything after it is commodity.

### Competitive Moat
Nobody else has built a raw-book-to-audiobook pipeline for Arabic. Competitors are either
TTS engines (sell the voice, user handles everything) or audiobook platforms (distribute,
don't produce). Our text processing pipeline bridges the gap.

Full competitive analysis: [research/MARKET_RESEARCH.md](research/MARKET_RESEARCH.md)

---

## Repo Structure

The IPA pipeline is archived. The audiobook pipeline is the active project.
Full details in [REPO_STRUCTURE.md](REPO_STRUCTURE.md).

```
Sawt/
├── src/audiobook/          # ACTIVE - audiobook production pipeline
│   ├── ingest.py           #   POC-1: EPUB/DOCX/TXT → clean text
│   ├── chapters.py         #   POC-2: chapter detection & splitting
│   ├── dialogue.py         #   POC-3: dialogue detection
│   ├── azure_client.py     #   Azure SDK wrapper
│   ├── ssml.py             #   POC-4: SSML generation + voice selection (voice_pool folded in)
│   └── review.py           #   CSV export at every stage
├── tests/audiobook/        # ACTIVE - audiobook tests
├── data/books/             # ACTIVE - input books
│   ├── epub/               #   EPUB books (primary content source)
│   ├── docx/               #   DOCX books (author submissions)
│   ├── txt/                #   TXT files (internal/corpus use)
│   └── pdf/                #   PDF archive (descoped, reference only)
├── output/                 # ACTIVE - per-book working output (gitignored)
│   └── pdf/                #   PDF test outputs (archived, descoped)
├── docs/                   # ACTIVE - documentation
├── archive/                # PAUSED - IPA pipeline preserved intact
│   ├── src/                #   core/, dialects/, integrations/, utils/
│   ├── tests/              #   329 tests
│   ├── data/               #   masterTTS.json, test cases
│   ├── scripts/            #   demo, test scripts
│   ├── tools/              #   all tools including prototype history
│   └── app.py              #   Flask API
└── (configs, .env, etc)
```

### Data flow between POCs (isolated by file output, not code imports)

```
data/books/{epub,docx,txt}/book.*
    ↓ ingest.py
output/{format}/book/01_ingestion/clean_text.txt + paragraphs.csv      ← REVIEW
    ↓ chapters.py
output/{format}/book/02_chapters/chapter_*.txt + chapters.csv           ← REVIEW
    ↓ dialogue.py
output/{format}/book/03_segments/segments.csv                           ← REVIEW (book summary)
output/{format}/book/03_segments/ssml/chapter_*.csv                     ← machine segments
output/{format}/book/03_segments/review/chapter_*.txt                   ← human review text
    ↓ [OPTIONAL] ssml.py (Azure only — voice selection + SSML templates)
output/{format}/book/04_ssml/chapter_*.ssml + voice_config.json
    ↓ audio_gen.py (multi-provider: Google/ElevenLabs/Azure)
output/{format}/book/05_audio/{provider}/chapter_*.mp3

Step 3 segments CSV is the universal hand-off point.
Google/ElevenLabs skip step 4 — plain text per segment + silence concatenation.
Azure can use step 4 SSML or build it inline from step 3.
```

---

## Content Resources

### Free Content for Pipeline Development & Publishing

| Resource | What | Format | Size | Access |
|----------|------|--------|------|--------|
| **Hindawi Foundation** | Arabic literature, philosophy, science | EPUB + PDF | 3,271 books (CC BY 4.0) | [hindawi.org](https://www.hindawi.org/) |
| **Arabic E-Book Corpus** | Hindawi books pre-converted to clean text | Plain text + HTML | 1,745 books, 81.5M words | [researchdata.se](https://researchdata.se/en/catalogue/dataset/2024-145) |
| **Hindawi HuggingFace** | Hindawi content on HuggingFace | Various | Subset | [huggingface.co](https://huggingface.co/datasets/alielfilali01/Hindawi-Books-dataset) |
| **Archive.org Arabic** | Mixed: scanned + digital books | PDF, some EPUB | Tens of thousands | [archive.org](https://archive.org/details/booksbylanguage_arabic) |

### Tooling

| Tool | Purpose |
|------|---------|
| [hindawi-dl](https://github.com/shahwan42/hindawi-dl) | Bulk download Hindawi books |
| python-docx | DOCX extraction (Arabic paragraph structure) |
| ebooklib + BeautifulSoup | EPUB extraction (proven in POC-1) |
| Calibre (ebook-convert) | EPUB ↔ DOCX conversion (Arabic works for this direction) |

---

## Existing Work (What We Built)

### Prototypes (7 iterations in `docs/02-features/azure-audiobooks/reference/prototypes/`)

| Iteration | Approach | Result |
|-----------|----------|--------|
| 01 | Quotation marks `«»` | 5 dialogues, 0% attribution |
| 02 | Name-aware extraction | 0% (encoding blocked matching) |
| 03 | Colon `:` discovery | 59 dialogues found (breakthrough) |
| 04 | RTL-aware heuristics | 81% attribution (19% false positives) |
| 05 | Multiline state machine | Improved continuation detection |
| 06 | External name list (production) | 63.5% attribution, 99.7% text preservation |
| 07 | Bug fix debug | Recovered 331 lost words |

### Key findings
- Colon `:` is the primary dialogue marker in Arabic literature, not quotation marks
- External character name list (from Wikipedia) beats heuristic extraction
- State machine approach handles multiline dialogue continuation
- CSV review workflow is essential for quality verification
- Arabic Presentation Forms encoding vs Standard Arabic is a real problem
- NFKC normalization handles 100% of Presentation Forms (except ornate parentheses U+FD3E/FD3F)

### Production assets (to evolve into src/audiobook/)
- `06_simplified_detector.py` — production-ready state machine detector
- `character_voice_assignment.py` — voice pool, gender matching, SSML generation
- `azure_integration.py` — Azure SDK wrapper, X-SAMPA support
- CSV export workflow for review at every stage
- 14+ Azure Arabic neural voices across 7 dialects

---

## Execution Plan

### Design Principles
- **POC-first:** Build small, test with real books, fix, move on
- **Review between chapters:** Every POC produces CSV output for human review
- **Slice and dice:** Perfect each step before moving to the next
- **One book first:** Get one book working end-to-end, then generalize
- **No dialect switching:** A book is a book. One dialect per book. Arabic expressions change across dialects, not just accent — swapping dialects changes meaning. But **match the dialect to the book's origin** (Egyptian author → Egyptian voices, Levantine → Levantine)
- **Minimize LLM usage:** Code-first, use LLM only where it demonstrably helps (name extraction)
- **POCs isolated by data:** Each POC reads from previous POC's file output, not its code. Rewrite any POC without breaking the next one

---

### POC-1: Book Ingestion (EPUB/DOCX to clean text)

**Status:** COMPLETE (Feb 2026). Results: [docs/03-logs/POC1_RESULTS.md](../../03-logs/POC1_RESULTS.md)

**Problem:** Books arrive as EPUB or DOCX with inconsistent encoding, formatting, and structure.

**Scope:**
- EPUB extraction (HTML-based, cleanest source) — born-digital from Hindawi
- DOCX extraction (python-docx, author submissions)
- TXT file reading with encoding detection (internal use: Swedish corpus)
- Arabic encoding normalization (Presentation Forms → Standard Arabic via NFKC)
- Preserve paragraph boundaries (critical for later splitting)

**Out of scope:** PDF extraction (see [Format Scope & PDF Decision](#format-scope--pdf-decision))

**Output:**
- Clean plain text file per book → `output/{format}/{book}/ingestion/clean_text.txt`
- CSV: paragraph inventory → `output/{format}/{book}/ingestion/paragraphs.csv`
  - Columns: paragraph_number, char_count, word_count, first_50_chars
- Encoding report: what was normalized, what was stripped

**What was built:**
- `src/audiobook/ingest.py` — EPUB, DOCX, TXT extractors + normalization + paragraph splitting
- `tests/audiobook/test_ingest.py` — 21 tests, all passing
- Tested on 12 books: 5 EPUB (Hindawi), 4 DOCX (Internet Archive/Shamela), 3 TXT (Hindawi via HuggingFace)
- All output clean, all formats validated by human review

**Known issues for POC-2:**
- DOCX files from Shamela contain page number markers (e.g. `(1/406)`) as separate paragraphs — filter during chapter splitting
- OCR-based EPUBs (archive.org) have garbled page footers — dropped from test set, only born-digital EPUBs used

**Definition of done:** Clean text output from EPUB and DOCX that a human reads and says "yes, this is the book, nothing missing, nothing garbled" ✓

#### POC-1/POC-2 Polish (COMPLETE — Feb 2026)

Both modules polished with consistent patterns:

| Item | What was done |
|------|---------------|
| Logging | `print()` → `logging` module (INFO for reports, DEBUG for paths) in both modules |
| Exception context | `IngestionError(ValueError)` with book/stage context wrapping third-party errors |
| Return types | `NormStats` and `IngestSummary` TypedDicts for type-safe return values |
| Magic numbers | 6 named constants (`MIN_ARABIC_CHARS_PER_PAGE`, `PARAGRAPH_FALLBACK_THRESHOLD`, etc.) |
| Module docstring | Usage example added to `ingest.py` |

---

### POC-2: Chapter Detection & Splitting

**Status:** COMPLETE (Feb 2026). Results: [docs/03-logs/POC2_RESULTS.md](../../03-logs/POC2_RESULTS.md)

**Problem:** Books use different structural delimiters (chapters, parts, sections, etc.) or none
at all. Each structural unit becomes an audio file. Units that exceed Azure SSML limits need
sub-splitting so stitched audio doesn't have weird breaks.

#### Hard Rules

1. **Never cut mid-paragraph.** All splits — whether by delimiter or size limit — must land on
   a paragraph boundary. Paragraphs are atomic units throughout the pipeline.
2. **Delimiter OR size limit — whichever comes first.** Accumulate paragraphs. Two triggers:
   - Hit a structural delimiter → close the current unit, start a new one
   - Accumulated text reaches ~25K chars → close at the last complete paragraph before the limit
3. **All detection runs on `clean_text.txt` from POC-1.** Format-agnostic. No re-parsing of
   EPUB/DOCX. Works uniformly across all formats.

#### Azure SSML Character Limit

Azure Speech Service limit: **64KB per SSML request** (WebSocket). Arabic UTF-8 characters are
~2 bytes each, plus SSML markup overhead → **~25,000 usable Arabic characters per request**.

Source: [Azure Speech quotas](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits)

Additional limits: max 50 **distinct** `<voice>` and `<audio>` tags per SSML (not 50 total — reusing the same 2 voices is fine), 100K billable characters per file (Standard tier). Two-voice (narrator + dialogue) uses only 2 distinct voices, well under the limit regardless of how many voice switches occur.

#### Delimiter Hierarchy — Detect, Don't Impose

Arabic books use varied structural markers. Don't hardcode "chapter" — detect what the book
actually uses and respect its natural structure:

| Level | Arabic Terms | Examples |
|-------|-------------|----------|
| **Part** (highest) | جزء، الجزء، القسم، الباب | الجزء الأول، الباب الثاني |
| **Chapter** | فصل، الفصل | الفصل الأول، الفصل الثالث عشر |
| **Numbered** | Lone number on its own paragraph | ١، ٢، ٣ or 1, 2, 3 (Western/Eastern Arabic numerals) |
| **Section** | مبحث، مطلب، فرع | المبحث الأول |
| **Front/back matter** | مقدمة، تمهيد، خاتمة، إهداء | مقدمة المؤلف، الخاتمة |

**Lone number detection:** A paragraph that is ONLY a number (e.g. `١` or `3`) followed by
text paragraphs = chapter marker. Common pattern in Arabic fiction. Must be a standalone
paragraph, not a number embedded in text. Both Western digits (1, 2, 3) and Eastern Arabic
digits (١، ٢، ٣) should match.

#### Splitting Logic

```
Accumulate paragraphs from the beginning of the book.

While there are paragraphs remaining:
  1. If the next paragraph is a structural delimiter:
     - Close the current unit at the paragraph BEFORE the delimiter
     - Name it by its delimiter: CH1, CH2, P1, etc.
     - The delimiter paragraph becomes the first line of the next unit (or is stored as title)
  2. If adding the next paragraph would exceed ~25K chars:
     - Close the current unit at the CURRENT paragraph (last complete paragraph before limit)
     - Name the sub-unit: CH1 - 1/2, CH1 - 2/2 (or P1/CH1 - 1/2 if nested)
     - Continue accumulating into the next sub-unit
  3. If a delimiter closes a unit that's already been sub-split:
     - The final sub-unit gets the last number: CH1 - 3/3
  4. If no delimiter is ever found:
     - Pure size-based chunks: 001, 002, 003
```

#### Naming Convention

| Scenario | Unit names |
|----------|-----------|
| Chapter finishes before limit | `CH1`, `CH2`, `CH3` |
| Chapter exceeds limit (split into 2) | `CH1 - 1/2`, `CH1 - 2/2` |
| Part > Chapter hierarchy | `P1/CH1`, `P1/CH2`, `P2/CH1` |
| Nested hierarchy, oversized | `P1/CH1 - 1/2`, `P1/CH1 - 2/2` |
| No delimiters detected (size-only) | `001`, `002`, `003` |
| Front/back matter | `مقدمة`, `خاتمة` (use actual title) |

#### What We Don't Detect

- **Headers/sub-headers** within chapters — not useful for audiobook splitting. If a book has
  no chapter-level delimiters, fall back to size-based splitting. The tool is optimized for
  audiobooks, not research papers.
- **Decorative dividers** (★ ● ※ •••) — scene breaks within chapters are not split points.
  They pass through to POC-3 (dialogue detection may use them as context boundaries).
- **Date entries, story titles, or other book-specific patterns** — too varied to generalize.
  Books with these patterns but no standard delimiters fall through to size-based splitting.

#### EPUB Spine — Bonus, Not Foundation

Tested all 5 Hindawi EPUBs. **Spine is NOT a reliable chapter signal:**

| Book | Spine content items | Actual chapters | Spine useful? |
|------|-------------------|-----------------|---------------|
| al-liss-wal-kilab | 18 files | 18 | YES (1:1 mapping) |
| awlad-haretna | 5 files | ~114 | NO (parts, not chapters) |
| bidaya-wa-nihaya | 1 file | 92 | NO (single-file EPUB) |
| tharthara-fawq-al-nil | 1 file | 26 | NO (single-file EPUB) |
| zuqaq-al-midaqq | 1 file | 35 | NO (single-file EPUB) |

Only 1 of 5 has clean spine-to-chapter mapping. 3 of 5 are single-file EPUBs (entire novel in
one HTML file). Text-based regex on `clean_text.txt` is the catch-all strategy.

#### Survey Findings (12 Test Books)

Surveyed all 12 books' `clean_text.txt` for structural delimiter patterns (Feb 2026).

**EPUB (5 books):**

| Book | Delimiter Found | Count | Pattern |
|------|----------------|-------|---------|
| al-liss-wal-kilab | `الفصل الأول`, `الفصل الثاني`... | 19 | Arabic chapter heading |
| awlad-haretna | `١`, `٢`, `٣`... (standalone paragraphs) | 114 | Lone Eastern Arabic numeral |
| bidaya-wa-nihaya | `١`, `٢`, `٣`... | 92 | Lone Eastern Arabic numeral |
| tharthara-fawq-al-nil | `١`, `٢`, `٣`... | 18 | Lone Eastern Arabic numeral |
| zuqaq-al-midaqq | `١`, `٢`, `٣`... | 35 | Lone Eastern Arabic numeral |

**DOCX (4 books):**

| Book | Delimiter Found | Count | Noise |
|------|----------------|-------|-------|
| al-tamheed-fi-tajweed | `الباب` (11) + `الفصل` (8) + `مقدمة` (3) | 22 | None |
| jawahir-al-adab | `الباب` (31) + `الفصل` (16) + `مقدمة` (1) | 48 | 308 page markers |
| mabahith-ulum-alquran | **NONE** | 0 | 528 page markers |
| mawsuat-al-ijaz-al-ilmi | **NONE** | 0 | 249 page markers |

**TXT (3 books):**

| Book | Delimiter Found | Count | Notes |
|------|----------------|-------|-------|
| رحلة-ابن-فطومة | **NONE** | 0 | Size fallback |
| صدى-النسيان | `•••` + Arabic story titles | 21 | Unique (short story collection) |
| يوميات-نائب-في-الأرياف | Date entries (`١٢ أكتوبر`) | 4 | Unique (diary format) |

**Key findings:**
1. **Lone Eastern Arabic numerals** are the most common pattern — 4 of 5 EPUBs (259 total matches)
2. **`الباب` / `الفصل` hierarchy** exists in 2 DOCX books and 1 EPUB (real hierarchy: باب > فصل)
3. **5 of 12 books have zero standard delimiters** → size-based fallback works as designed
4. **Page markers `(n/m)` are noise** — 1,085 across 3 DOCX books. Must filter, NOT split on
5. **Short paragraphs are dialogue, NOT headers** — don't use paragraph length as a signal

#### Regex Patterns (From Survey)

| Priority | What | Regex | Covers |
|----------|------|-------|--------|
| 1 | Lone Eastern Arabic numerals | `^[٠-٩]+$` | 4 EPUBs (259 matches) |
| 2 | Arabic heading terms | `^(الفصل\|الباب\|الجزء\|القسم\|المبحث\|مقدمة\|تمهيد\|خاتمة\|إهداء)` | 1 EPUB + 2 DOCX (70 matches) |
| 3 | Page markers (**FILTER OUT**) | `^\(\d+/\d+\)$` | 3 DOCX (1,085 noise matches) |

Western digits (`^[0-9]+$`) not found in survey but included for robustness.

#### Scope

- Detect structural delimiters via regex on Arabic heading terms AND lone numbers
- Support hierarchy: Part (باب) > Chapter (فصل) > Numbered (١٢٣) > Section (مبحث) > Front/Back matter
- Two split triggers: delimiter boundary OR size limit (~25K chars), whichever comes first
- **All splits land on paragraph boundaries — never cut mid-paragraph**
- Sub-split oversized units with numbered naming (CH1 - 1/2, CH1 - 2/2)
- Handle books with no delimiters (pure size-based fallback at paragraph boundaries)
- Filter DOCX Shamela page markers `(n/m)` — noise, not structure
- Tag front/back matter distinctly in CSV (use actual Arabic title)
- All detection runs on `clean_text.txt` from POC-1 (format-agnostic)

#### Output

- Individual unit text files → `output/{format}/{book}/chapters/chapter_01.txt`, etc.
- CSV: chapter inventory → `output/{format}/{book}/chapters/chapters.csv`
  - Columns: unit_number, unit_name, level (part/chapter/numbered/section/frontmatter/size), title, char_count, paragraph_count, split_part, total_splits
- Summary: detected delimiter type (or "none — size-based"), total units, total chars, splits needed

#### Review Gate

- Open the CSV, verify boundaries match the actual book structure
- Confirm the detected hierarchy is correct (Parts? Chapters? Numbers? None?)
- Check that ALL splits land on paragraph ends — no partial paragraphs
- Verify no text lost between units (char count should sum to total)
- Read first and last paragraph of each unit — do they make sense?

#### Test Expectations

Same 12 books from POC-1:
- **5 EPUB fiction** → expect lone numbers (4 books) or الفصل headings (1 book)
- **2 DOCX religious/academic** → expect الباب/الفصل hierarchy + page marker filtering
- **2 DOCX academic** → expect NO delimiters, pure size fallback + page marker filtering
- **3 TXT fiction** → expect NO standard delimiters, size fallback (book-specific patterns exist but not worth special-casing)

#### Definition of Done

Unit files that when concatenated reproduce the original text. No partial paragraphs. Every
unit under Azure SSML limit (~25K chars). CSV shows detected hierarchy (or size-based fallback)
and makes every boundary obvious.

---

### POC-3: Dialogue Detection & Voice Output

**This is the core POC. Two phases: two-voice first, multi-voice second.**

#### Phase A: Narration vs Dialogue Detection (Two-Voice) — THE GOAL

**Status:** COMPLETE (Feb 2026). Code: `src/audiobook/dialogue.py`, Tests: `tests/audiobook/test_dialogue.py`

**Problem:** Separate narration from dialogue so we can assign different voices.

**Scope (what was built):**
- Binary classification: narration or dialogue (no character attribution)
- State machine with 3 dialogue markers: colon, em dash, trailing colon
- No continuation across paragraphs — each new paragraph resets to narrator
- Guillemets `«»` are NOT dialogue markers — treated as plain text (typographic quotes, inner thoughts)
- Dual output: machine-readable CSV + human-readable review text with `// \\` markers
- Review→CSV sync flow for human corrections
- Per-chapter segmentation + book-level summary CSV

**Dialogue markers (priority order):**
1. **Em dash** (`–/—/-` + space at paragraph start) → whole paragraph = dialogue
2. **Colon** (`:` with speech attribution before it) → before = narrator, after = dialogue
3. **Trailing colon** (paragraph ends with `:` + speech verb) → narrator, sets up next paragraph as dialogue (one-shot)
4. **Plain** → narrator (or dialogue if immediately after trailing colon, one-shot only)

**What is NOT a dialogue marker:**
- **Guillemets `«»`** — typographic quotation marks for short quotes, inner thoughts, scare quotes. Switching voices for 3-word `«phrases»` embedded in narration would be jarring. Kept as text.
- **No continuation** — a plain paragraph after dialogue is always narrator. Multi-paragraph dialogue without markers doesn't appear in practice (Mahfouz marks every speaker turn).

**Colon filtering:**
- Time colons (`١٢:٣٠`) → skipped
- URL colons (`http:`) → skipped
- Trailing colons (nothing after) → heading-style, skipped (unless speech verb detected)
- Short text before colon (<150 chars) → assumed dialogue attribution
- Long text before colon (≥150 chars) → requires explicit speech verb in last 100 chars
- Passive voice (`قيل`) excluded from speech verb matching
- Arabic diacritics (harakat) stripped before verb matching

**Output:**
- `03_segments/ssml/chapter_*.csv` — machine segments (segment_number, type, char_count, text)
- `03_segments/review/chapter_*.txt` — human review text (`// dialogue \\` markers)
- `03_segments/segments.csv` — per-chapter summary (total_segments, narrator/dialogue counts, chars, ratio)

**Results on 12 books:**

| Book | Chapters | Segments | Dialogue % |
|------|----------|----------|------------|
| al-liss-wal-kilab | 18 | 1,207 | 40.3% |
| awlad-haretna | 114 | 7,399 | 41.8% |
| bidaya-wa-nihaya | 92 | 3,876 | 31.5% |
| tharthara-fawq-al-nil | 18 | 2,125 | 40.5% |
| zuqaq-al-midaqq | 35 | 2,449 | 45.0% |

**Review workflow:**
1. Open `review/chapter_*.txt` — dialogue wrapped in `// \\`, narrator is plain
2. Edit: add/remove `// \\` markers to fix misclassifications
3. Run `sync_review(segments_dir)` → regenerates `ssml/*.csv` from edited review text
4. Review cadence: chapter by chapter

**Definition of done:** A complete two-voice audiobook where narration and dialogue are clearly distinguished, voice switches feel natural, and no text is missing.

---

#### Phase B: Character Attribution & Multi-Voice — CLOSED (Feb 2026)

**Decision: Skip entirely.** The complexity is not justified by current capabilities or listener value.

**Why it was closed:**

1. **Azure Arabic has only 2 voices per dialect (1M, 1F).** Even with perfect attribution, characters C through Z get the same 2 voices. No character distinction possible.

2. **Attribution overhead is high for marginal gain.** 63.5% automated, 36.5% manual review. Unnamed characters (the officer, the mayor, the neighbor) need catch-all assignment. Heavy em-dash exchanges (10 lines between two people) need turn-tracking. All this for a feature most listeners don't prefer.

3. **Research consensus: single narrator with tonal shifts beats full-cast for most listeners.** Multi-voice is the exception (drama adaptations, big-budget productions), not the norm. Rapid TTS voice-switching in dialogue-heavy scenes sounds robotic, not dramatic.

4. **Two-voice already captures 90% of the value.** Narrator↔dialogue voice switch signals "someone is speaking" — that's sufficient. Listeners distinguish characters from context, not voice identity.

**What's preserved for future reference:**
- 7 prototype iterations in `archive/` and `docs/02-features/azure-audiobooks/reference/prototypes/`
- Character registry design (Wikipedia-sourced, CSV-based)
- Attribution logic (carry-forward, gendered verbs, explicit names)
- Voice mapping design (per-book config, character → voice ID)
- All reusable if Azure Arabic capabilities improve significantly

---

#### Emotion/Prosody Enhancement — DEFERRED (waiting on platform)

**Azure Arabic voices have zero `mstts:express-as` support.** No emotions, no speaking styles, no HD voices. English has 30+ styles; Arabic has none. This is a platform capability gap, not a pipeline task.

**When Azure adds emotion styles for Arabic:**
- Phase A segment CSVs are the right input — each dialogue segment would need an emotion tag
- Emotion classification from surrounding narrator context is straightforward (LLM or rule-based)
- SSML wrapping with `<mstts:express-as style="angry">` is trivial once available
- This would be higher-value than multi-voice: same 2 voices, but with emotional range

**What we CAN do now (in POC-4 SSML generation):**
- `<prosody rate="+10%">` on dialogue — slightly faster pace signals conversation
- `<prosody pitch="+5%">` on dialogue — subtle lift separates dialogue from narrator
- `<break time="300ms"/>` at narrator↔dialogue transitions — audible pause for voice switch
- These are subtle reinforcements, not character distinction — worth testing in POC-4

**Monitor:** Azure Arabic voice updates, HD voice availability, `express-as` style additions.

---

### POC-4: SSML Generation + Voice Selection — DONE

**Status:** Complete. SSML generation production-ready. POC-4a validated 4 TTS providers — Google Chirp3-HD and ElevenLabs are viable alternatives to Azure. See `docs/03-logs/POC4_RESULTS.md`.

**Code:** `src/audiobook/ssml/core.py` (stub exists)

**Problem:** Take verified segment CSVs from POC-3 and produce Azure-ready SSML files with dialect-matched voice assignments.

**Input:** `03_segments/ssml/chapter_*.csv` (segment_number, type, char_count, text)
**Output:** `04_ssml/chapter_*.ssml` (valid Azure SSML, ready for TTS API)

#### What POC-4 builds

**1. Per-book voice config** (simple JSON/YAML):
```
book_dialect: ar-EG
narrator_voice: ar-EG-ShakirNeural
dialogue_voice: ar-EG-SalmaNeural
```
- Set once per book, drives all SSML generation
- Default for Hindawi catalog: Egyptian (ar-EG)
- Override per book for other dialects (Levantine, Gulf, etc.)

**2. SSML template engine:**
- Read segment CSV → wrap narrator segments in narrator voice tag, dialogue segments in dialogue voice tag
- Valid SSML structure: `<speak>` → `<voice>` → text
- Respect Azure limits: max 50 **distinct** voice names per SSML (two-voice uses only 2), ~25K chars per request
- Context-aware breaks between segments:
  - `<break time="500ms"/>` — narrator→narrator (paragraph boundary)
  - `<break time="300ms"/>` — narrator↔dialogue (voice transition)
  - `<break time="200ms"/>` — dialogue→dialogue (rapid exchange)

**3. Voice sampling script** (`scripts/sample_voices.py`):
- Purpose: listen to voice pairs before committing to a default config
- **Round 1 — Pick the dialect** (6 audio files): same sample text, 3 dialect pairs (ar-EG, ar-SA, ar-SY), male narrates + female dialogue
- **Round 2 — Pick the direction** (2 audio files): winning dialect, male-narrates vs female-narrates
- **Round 3 — Test prosody** (only if needed): subtle `<prosody rate/pitch>` tweaks on dialogue
- Total: 8-10 audio files, ~30K chars, within free tier
- Output: MP3s with structured filenames, human listens and picks winner

**Why M/F voice switch (not prosody-only):**
- Azure Arabic prosody has only 3 crude dials: rate, pitch, volume
- A 10% speed bump on the same voice doesn't signal "someone is speaking" — listener won't register it
- Real human narrators use dozens of micro-adjustments (breathiness, emphasis, timing) that TTS can't replicate
- M/F switch is a blunt instrument but creates clear, unambiguous contrast for TTS
- Voice switching also resets listener attention, masking TTS pronunciation artifacts
- Prosody polish is optional on top of voice switch, not a substitute for it

**Prosody (optional, test-driven):**
- `<prosody rate="+10%" pitch="+5%">` on dialogue — only if sampling confirms it helps
- Not pre-optimized — generate plain two-voice first, tune only what sounds flat
- Azure Arabic has zero `mstts:express-as` support (no emotions/styles) — prosody knobs are all we have

**Fiction vs non-fiction paths:**
```python
# Fiction — two-voice (narrator + dialogue from POC-3 segments)
narrator segments → narrator_voice tag
dialogue segments → dialogue_voice tag

# Non-fiction — single voice (skip POC-3, chapters go straight to SSML)
all text → narrator_voice tag
```

**Voice inventory for dialect matching:**

| Dialect | Locale | Male | Female | Best for |
|---------|--------|------|--------|----------|
| Egyptian | ar-EG | ShakirNeural | SalmaNeural | Mahfouz, Hindawi catalog, modern fiction |
| Saudi | ar-SA | HamedNeural | ZariyahNeural | Gulf authors, religious texts |
| Levantine | ar-SY | LaithNeural | AmanyNeural | Levantine authors (Gibran, Darwish) |
| Jordanian | ar-JO | TaimNeural | SanaNeural | Jordanian authors |
| Lebanese | ar-LB | RamiNeural | LaylaNeural | Lebanese authors |
| Iraqi | ar-IQ | BasselNeural | RanaNeural | Iraqi authors |
| Maghreb | ar-MA | JamalNeural | MounaNeural | North African authors |

**Definition of done:** Valid SSML files that Azure TTS API accepts, with dialect-matched two-voice output for fiction and single-voice for non-fiction. Voice pair selected through sampling. At least one book fully converted to SSML.

---

## Test Books

### EPUB (5 Hindawi born-digital — clean)

| Book | Author | Source | Paras | Chars |
|------|--------|--------|------:|------:|
| al-liss-wal-kilab | Naguib Mahfouz | Hindawi | 781 | 125K |
| awlad-haretna | Naguib Mahfouz | Hindawi | 4,299 | 563K |
| bidaya-wa-nihaya | Naguib Mahfouz | Hindawi | 2,273 | 474K |
| tharthara-fawq-al-nil-hindawi | Naguib Mahfouz | Hindawi | 1,496 | 146K |
| zuqaq-al-midaqq | Naguib Mahfouz | Hindawi | 1,412 | 383K |

### DOCX (4 Arabic books from Internet Archive/Shamela)

| Book | Subject | Source | Paras | Chars |
|------|---------|--------|------:|------:|
| al-tamheed-fi-tajweed | Quranic recitation | Shamela | 195 | 122K |
| jawahir-al-adab | Arabic rhetoric | Shamela | 2,108 | 773K |
| mabahith-ulum-alquran | Quranic sciences | Shamela | 1,056 | 564K |
| mawsuat-al-ijaz-al-ilmi | Scientific encyclopedia | Shamela | 1,190 | 748K |

Note: Shamela DOCX files contain page number markers (e.g. `(1/406)`) — will filter in POC-2.

### TXT (3 Hindawi books from HuggingFace — clean)

| Book | Author | Source | Paras | Chars |
|------|--------|--------|------:|------:|
| رحلة-ابن-فطومة | Naguib Mahfouz | HuggingFace | 856 | 125K |
| صدى-النسيان | Naguib Mahfouz | HuggingFace | 425 | 81K |
| يوميات-نائب-في-الأرياف | Tawfiq al-Hakim | HuggingFace | 651 | 147K |

### Archived (PDF — Out of Scope)

PDFs kept in `data/books/pdf/` for reference. Output in `output/pdf/`. Not processed by active pipeline.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Input formats** | EPUB + DOCX (first-class), TXT (internal) | EPUB = content source, DOCX = author format. PDF descoped — intractable. |
| Language | Python | EPUB/DOCX libs, Azure SDK, existing prototypes, Arabic text handling |
| Pronunciation | Let Azure handle it (plain text) | IPA letter-by-letter approach was unusable — validated the hard way |
| Voice per book | Single dialect, matched to book origin | A book is a book. Dialect changes meaning, not just accent. Match voice dialect to author/setting |
| Repo structure | Same repo, IPA archived | Zero code overlap. Archive preserves history without interference |
| Dialogue detection | Code-first (state machine + patterns) | LLM only if code can't solve it |
| Review workflow | CSV export, chapter-by-chapter review | Proven in prototypes, manageable scope |
| Character names source | External list (Wikipedia, book info) | Heuristic extraction had 19% false positive rate |
| POC isolation | Data boundaries between POCs | Each POC reads previous POC's file output, not its code |
| SSML generation | Templates + voice selection in one module | voice_pool folded into ssml — two-voice is a 3-field config, not a separate module |
| Voice selection | M/F switch per dialect, not prosody-only | Azure Arabic prosody (rate/pitch/volume) too crude to signal dialogue alone; voice switch creates clear contrast |
| Voice sampling | 8-10 test files across 3 dialects, human picks | Don't pre-optimize — listen first, then commit to defaults |
| Audio stitching | Per-chapter files, concatenated | Matches review workflow (review by chapter) |
| PDF handling | Out of scope | No OSS tool extracts Arabic PDF text correctly. See research. |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| EPUB paragraph boundaries inconsistent across publishers | Medium | High | Test on 5+ books from different sources | ✓ Resolved — tested on 12 books |
| Chapter detection fails on unusual structures | Medium | Medium | Fallback: manual chapter markers or size-based splitting | ✓ Resolved — size fallback works |
| Quotation conventions vary wildly between books | High | Medium | Build normalizer, test on 3+ books with different styles | ✓ Resolved — guillemets kept as narrator |
| Two-voice doesn't sound good enough | Low | High | Already tested in prototypes — voice switching works | Open — validate with POC-4 sampling |
| Multi-voice review is too painful to scale | High | Medium | ~~Accept it as the cost~~ | ✓ Closed — Phase B skipped entirely |
| Azure Arabic has no emotion/style support | High | Medium | Wait for Azure updates; prosody knobs are all we have | Open — monitor Azure |
| Voice pair sounds wrong for a dialect | Medium | Low | Sampling script tests 3 dialects before committing | Open — POC-4 |
| Azure free tier runs out during testing | Low | Low | Monitor usage, ~$8-12/book if needed | Open |
| Competitor (Lahajati) builds same pipeline | Medium | High | Ship fast, build content moat with published audiobooks | Open |
| AI narration quality insufficient for fiction | Medium | Medium | Two-voice masks artifacts; prosody tuning if needed | Open — validate with POC-4 |

---

## Go-to-Market Strategy

Detailed analysis: [research/MARKET_RESEARCH.md](research/MARKET_RESEARCH.md)

### Summary

**Phase 1 (Months 1-3):** Produce 20-30 public domain audiobooks from Hindawi CC catalog.
Publish on YouTube + Spotify/Anghami. Build portfolio and audience. Refine pipeline end-to-end.

**Phase 2 (Months 3-5):** Offer manual audiobook conversion service to young Arab authors.
$20-40/book. Market via Arabic social media. Success metric: 5+ paying customers.

**Phase 3 (Months 5-8):** If demand validates, build self-serve web tool. $15-25/book.

### Target Audience (Prioritized)
1. **Young Arab authors / small publishers** — can't afford $1,000+ human narration, write in DOCX
2. **Content consumers** — reached through published content, not direct marketing
3. **Institutions** — later, when product is proven

### Distribution Channels
- YouTube (highest Arabic audiobook search volume, evergreen)
- Spotify / Apple Podcasts (podcast format)
- Anghami (70M users, Arabic-native)
- Audible (accepts AI narration via "Virtual Voice" program)
- Arabookverse (Arabic audiobook distributor, 300+ platforms)

---

## Success Criteria

### POC-1 (Book Ingestion) ✓ PRODUCTION READY
- Clean text extraction from EPUB, DOCX, and TXT
- All paragraph boundaries verified by human review
- Tested on 12 books across 3 formats (5 EPUB, 4 DOCX, 3 TXT)
- 21 tests passing, PDF descoped and removed from pipeline
- **Results:** `docs/03-logs/POC1_RESULTS.md`

### POC-2 (Chapter Splitting) ✓ PRODUCTION READY
- Detect natural structural delimiters (parts, chapters, sections) across 3+ books
- Respect book's own hierarchy — don't impose rigid "chapter" concept
- All units under Azure SSML limit (~25K chars), sub-split oversized units at paragraph boundaries
- No mid-sentence splits
- Unit files concatenate back to original text
- 91 tests passing, validated on all 12 books
- **Results:** `docs/03-logs/POC2_RESULTS.md`

### POC-3 Phase A (Two-Voice) ✓ PRODUCTION READY
- Dialogue detection on all 12 books, 103 tests passing
- ~95% accuracy on narrator/dialogue split (human-reviewed on صدى النسيان)
- 3 dialogue markers: colon, em dash, trailing colon
- No continuation heuristic (false positives outweighed benefit)
- Guillemets `«»` kept as narrator text — coherent passages mixing inner thoughts and spoken words, splitting would fragment the narration with jarring micro voice-switches
- Short story titles (مدد, قمر, علي لوز, etc.) left within 25K chapters — titles read aloud naturally as narrator pauses, listener navigation is time-based (30s rewind, bookmarks) not chapter-skip, TOC is complementary not mandatory
- Dual output: machine CSV + human review text with sync workflow
- Per-chapter + book-level summary CSV for quality validation
- **Results:** `docs/03-logs/POC3_RESULTS.md`

### POC-3 Phase B (Multi-Voice) — CLOSED
- **Skipped.** Azure Arabic has only 2 voices per dialect (no character distinction possible)
- Character attribution overhead (36.5% manual review) not justified for 2-voice output
- Rapid voice-switching in dialogue-heavy scenes sounds robotic in current TTS
- Most listeners prefer single narrator with tonal shifts over full-cast productions
- Emotion/prosody enhancement deferred — waiting on Azure to add `express-as` styles for Arabic
- Segment CSVs from Phase A are the foundation for any future enhancement

### POC-4 (SSML + Voice Selection) ✓ DONE
- Valid SSML files accepted by Azure TTS API — all 12 books converted
- 30 tests passing, `src/audiobook/ssml/core.py` (280 lines)
- Dialect-matched voice pairs with context-aware breaks (500/300/200ms)
- Voice coalescing reduces voice tag count — 50-tag limit is distinct names, not total elements
- POC-4a: multi-provider comparison (Azure, Google, OpenAI, ElevenLabs)
  - OpenAI not viable (no Arabic voices)
  - Google Chirp3-HD: 30 Arabic voices, natural, same cost as Azure ($1.16/book)
  - ElevenLabs: best quality, 20x cost ($21.74/book), 10 user-approved Arabic voices
  - Mishkal diacritization makes pronunciation worse — plain text stays
- POC-4b: voice pairing tests (8 combos: 4 gender pairs × 2 providers)
  - **FF is the smoothest pairing** — less jarring voice transitions
  - Female narrator over male dialogue better than reverse
  - Same-gender pairings (MM, FF) produce most cohesive audio
  - Tested on Chapter 1 of Tharthara Fawq al-Nil
- **Results:** `docs/03-logs/POC4_RESULTS.md`

### POC-5: Audio Generation (Multi-Provider) — NEXT
- **Goal:** Full book/chapter audio generation from segments CSV (step 3 output)
- Segments CSV is the universal hand-off point for all providers
- SSML (step 4) is optional — Azure uses it natively, Google/ElevenLabs skip it
- Providers send plain text per segment, concatenate with silence files

**Provider architecture:**

| Provider | Input | Voice Switch | Pauses | SSML |
|----------|-------|-------------|--------|------|
| Azure | Segments CSV → SSML inline | Multi-voice in 1 request | `<break>` tags | Full |
| Google Chirp3-HD | Segments CSV → plain text | 1 API call per segment | Silence WAV concat | Limited (no `<break>`, no `<voice>`) |
| ElevenLabs | Segments CSV → plain text | 1 API call per segment | `<break>` within segment + silence WAV concat | `<break>` only (no `<voice>`) |

**Settled voice pairings (V Liked, pairing-tested):**

| Provider | Combo | Narrator | Dialogue | Notes |
|----------|-------|----------|----------|-------|
| Google | FF (primary) | Sulafat | Leda | Smoothest, very good narrator |
| Google | MM | Enceladus | Sadaltager | Good narrator, ok dialogue |
| ElevenLabs | FF (primary) | Sara (MSA) | Alice (Egyptian) | Both interesting, good contrast |
| ElevenLabs | MM | Yahya (MSA) | Karim (MSA) | Very good narrator, ok dialogue |
| ElevenLabs | MF | Moncellence (Egyptian) | Alice (Egyptian) | Both good, dialect-matched |

Full voice inventory: `docs/02-features/research/final_voices.csv` (19 voices, pairing-tested)

**Scope:**
- Parameterized script: book, chapter range, provider, voice pairing
- Pause variation (randomized within ranges, not fixed durations)
- Full book generation (all chapters → concat → final MP3)
- Output: `output/{format}/{book}/05_audio/{provider}/chapter_*.mp3`

---

## Audiobook Best Practices — How Sawt Meets Them

Research: `docs/02-features/research/audiobook_best_practices.md`

| Best Practice | Industry Standard | Sawt Status |
|---------------|-------------------|-------------|
| **Pause variation** | Vary breaks to avoid metronome effect (#1 TTS complaint) | ✅ Context-aware breaks (500/300/200ms by transition type). TODO: add slight randomization |
| **Said tags with narrator** | "He said" stays with narrator voice, not dialogue | ✅ Colon-split puts attribution before colon as narrator, quoted speech as dialogue |
| **Dialect matching** | Match voice to author's region (Storytel/Kitab Sawti standard) | ✅ Per-book dialect config, Egyptian for Mahfouz, Levantine voices available |
| **Two-voice model** | MSA narration + dialect dialogue is how Egyptian fiction is produced | ✅ Core architecture — narrator voice + dialogue voice |
| **Same-gender pairings smoothest** | Less jarring transitions than M/F switching | ✅ FF confirmed as primary pairing in listening tests |
| **Voice contrast** | Enough to distinguish, not so much it feels spliced | ✅ Tested 8 pairings, selected voices with complementary warmth/expressiveness |
| **Guillemets as narrator** | Inner thoughts + speech by same person = one voice for cohesion | ✅ Deliberate design decision — avoids jarring micro voice-switches |
| **Long-form testing** | Test 10+ min continuously, not spot checks | ✅ Full chapter 1 (70 segments) generated for all 8 pairings |
| **Proper noun pronunciation** | #1 Arabic TTS failure point (no diacritics in print) | ⚠️ Future: per-book pronunciation dictionary via SSML `<phoneme>` |
| **Prosody monotony** | Vary rhythm to avoid auditory fatigue | ⚠️ Future: `<prosody>` rate/pitch variation between narrative segments |
| **Fiction vs non-fiction** | Fiction = expressive two-voice; non-fiction = single authoritative voice | ✅ Genre flag in pipeline design, non-fiction skips dialogue detection |

## References

| Resource | Location |
|----------|----------|
| **Market research** | `docs/02-features/azure-audiobooks/research/MARKET_RESEARCH.md` |
| **PDF extraction research** | `docs/02-features/azure-audiobooks/research/ARABIC_PDF_EXTRACTION.md` |
| Production detector | `docs/02-features/azure-audiobooks/reference/prototypes/06_simplified_detector.py` |
| Voice assignment | `docs/02-features/azure-audiobooks/reference/character_voice_assignment.py` |
| Azure integration | `docs/02-features/azure-audiobooks/reference/azure_integration.py` |
| Detection findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SIMPLIFIED_DETECTION_FINAL_STATUS.md` |
| Scalability analysis | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SCALABILITY_ANALYSIS.md` |
| Bug fix history | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/BUG_FIX_TEXT_LOSS_RESOLVED.md` |
| Research findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/QUOTATION_ATTRIBUTION_RESEARCH_FINDINGS.md` |
| POC-1 results | `docs/03-logs/POC1_RESULTS.md` |
| POC-2 results | `docs/03-logs/POC2_RESULTS.md` |
| POC-3 results | `docs/03-logs/POC3_RESULTS.md` |
| POC-4 results | `docs/03-logs/POC4_RESULTS.md` |
| Azure voice capabilities | `docs/02-features/azure-audiobooks/reference/arabic_voices_capabilities.json` |
| Hindawi CC corpus | [hindawi.org](https://www.hindawi.org/) — 3,271 books, CC BY 4.0 |
| Swedish text corpus | [researchdata.se](https://researchdata.se/en/catalogue/dataset/2024-145) — 1,745 books, plain text |
| hindawi-dl | [github.com/shahwan42/hindawi-dl](https://github.com/shahwan42/hindawi-dl) — bulk downloader |
