# Azure Arabic Audiobook Production Plan

**Date:** February 2026
**Goal:** Produce Arabic audiobooks from raw book files (EPUB/DOCX) using Azure TTS
**Target:** Two-voice audiobooks (narrator + dialogue) as primary deliverable
**Stretch:** Multi-voice (per-character) after two-voice is proven solid
**Cost:** ~$8-12 per 150-page book, free tier available (5M chars/month, 12 months)

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

## Voice Approach Refresher

### Single Voice
- One voice reads everything
- Linguistic accuracy ~80%, flaws easily detected — listener has no "reset" point
- Sounds robotic on long content
- No text processing beyond chapter splitting
- **Use case:** Non-fiction, educational, reference material where no dialogue exists
- **Not a product** — anyone with Azure access can do this, zero differentiation

### Two Voice (Narrator + Dialogue) — PRIMARY GOAL
- Narrator voice for narration, different voice for all dialogue
- Voice switching creates a "listener attention reset" that masks TTS pronunciation artifacts
- Only requires binary classification: "Is this narration or dialogue?"
- Existing colon-based detection already achieves 100% dialogue detection rate
- No character attribution needed — just detect that *someone* is speaking
- Manual review effort: 5-15 min per book (verify narration/dialogue boundaries)
- **Use case:** Fiction, stories, any book with dialogue
- **This is the goal.** Good enough for 70-80% of fiction books

### Multi Voice (Per-Character) — STRETCH
- Unique voice per character, gender-matched, dialect-aware
- The "beast" — character attribution is the hard unsolved problem (63.5% automated, 36.5% manual)
- 7 prototype iterations already invested, competitive with English SOTA (53-69%)
- Manual review effort: 15-40 min per book
- Review was painful — developed CSV workflow to make it bearable
- **Use case:** Dialogue-heavy novels, drama adaptations
- **Attempt after two-voice is solid.** Don't expect an easy win

---

## Why Text Processing Is the Product

The actual pipeline difficulty distribution:

```
Raw Book (EPUB/DOCX) ──→ Text Extraction & Cleaning      [DONE - POC-1 complete]
                  ──→ Chapter Detection & Splitting    [DONE - POC-2 complete]
                  ──→ Narration vs Dialogue Detection  [HARD - 7 iterations, mostly solved]
                  ──→ Character Attribution             [BEAST - 63.5% automated]
                  ──→ SSML Generation                   [EASY - just markup templates]
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
ArabicTTS/
├── src/audiobook/          # ACTIVE - audiobook production pipeline
│   ├── ingest.py           #   POC-1: EPUB/DOCX/TXT → clean text
│   ├── chapters.py         #   POC-2: chapter detection & splitting
│   ├── dialogue.py         #   POC-3: dialogue detection
│   ├── azure_client.py     #   Azure SDK wrapper
│   ├── voice_pool.py       #   Voice selection, gender matching
│   ├── ssml.py             #   SSML generation
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
output/{format}/book/ingestion/clean_text.txt + paragraphs.csv    ← REVIEW
    ↓ chapters.py
output/{format}/book/chapters/chapter_*.txt + chapters.csv         ← REVIEW
    ↓ dialogue.py
output/{format}/book/segments/chapter_*.csv                        ← REVIEW (per chapter)
    ↓ ssml.py
output/{format}/book/ssml/chapter_*.ssml
    ↓ azure_client.py
output/{format}/book/audio/chapter_*.mp3
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
- **No dialect switching:** A book is a book. One voice profile per book. Arabic expressions change across dialects, not just accent — swapping dialects changes meaning
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

Additional limits: max 50 `<voice>` tags per SSML, 100K billable characters per file (Standard tier).

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

**Problem:** Separate narration from dialogue so we can assign different voices.

**Scope:**
- Adapt existing `06_simplified_detector.py` to work on chapter-level input from POC-2
- Binary classification only: narration or dialogue (no character attribution yet)
- Handle dialogue markers: colons, em dashes, guillemets, western quotes, hyphens
- Handle multiline dialogue (dialogue that spans paragraphs)
- Quotation mark normalization across book formatting conventions
- Produce segments tagged as NARRATOR or DIALOGUE

**Output per chapter:**
- Segmented CSV → `output/{book}/segments/chapter_01.csv`
  - Columns: segment_number, type [narrator/dialogue], char_count, text
- Statistics: narration/dialogue ratio, segment count, average segment length

**Review gate (per chapter):**
- Review CSV: is every segment correctly tagged?
- Focus on boundary cases: where does narration end and dialogue begin?
- Flag segments that are mislabeled
- Fix and re-run until chapter is clean
- **Review cadence: chapter by chapter.** Don't move to the next chapter until current one is reviewed and correct

**SSML generation:**
- Once segments are verified, SSML is straightforward:
  - NARRATOR segments → narrator voice tag
  - DIALOGUE segments → dialogue voice tag
  - Paragraph breaks → `<break>` tags
- One voice per role, consistent across the entire book
- No dialect switching — pick best-sounding voice pair for the book's style

**Audio output:**
- Generate audio per chapter → `output/{book}/audio/chapter_01.mp3`
- Stitch chapter audio files in order
- Listen to the result

**Definition of done:** A complete two-voice audiobook where narration and dialogue are clearly distinguished, voice switches feel natural, and no text is missing.

---

#### Phase B: Character Attribution & Multi-Voice (The Beast)

**Do not start this until Phase A is solid on at least 3 books.**

**Problem:** Attribute dialogue segments to specific characters for unique voice assignment.

**Why this is hard (honest assessment):**
- Current automated attribution: 63.5% (remaining 36.5% needs manual review)
- "Unknown" speakers: dialogue without explicit "said X:" attribution
- Pronoun resolution: "he said" → which male character?
- Implicit attribution: dialogue that follows narration about a character
- Arabic-specific challenges: verb-first word order, presentation forms encoding
- Review was painful in prototypes — lots of CSV rows to verify
- This is an active research problem globally, not just for Arabic

**Scope:**
- Layer character attribution on TOP of Phase A's narration/dialogue segments
- Use external character name list (from Wikipedia, book info)
- Apply existing detection: colon patterns, verb+name extraction, gender from verb form
- Everything that doesn't match → "Unknown" → manual CSV review
- Voice assignment: gender-matched, unique per character from Azure voice pool

**Output per chapter:**
- Segmented CSV with character column added → `output/{book}/segments/chapter_01.csv`
  - Columns: segment_number, type, character [name or "Unknown"], gender, char_count, text
- Character summary: detected characters, gender, dialogue count, assigned voice

**Review gate (per chapter):**
- Review CSV focusing on "Unknown" rows
- Assign character to each Unknown based on context
- Verify gender detection is correct
- Review cadence: chapter by chapter, same as Phase A
- Expect 15-40 min review per book at current accuracy

**Definition of done:** Multi-voice audiobook with distinct character voices. Listener can tell which character is speaking. Attribution is correct (verified via CSV review).

**Scaling strategy (future):**
- LLM-assisted name extraction: $0.07-0.15 per book
- Cross-book knowledge base: reuse resolved patterns
- Review interface with context display and quick-pick buttons
- Goal: reduce manual review from 15-40 min to 5-10 min

---

### POC-4: Emotion & Prosody Enhancement (Future Layer)

**Not in scope until POC-3 Phase A is proven.**

**Concept:**
- Detect exclamation marks → raise pitch
- Detect question marks → intonation shift
- Detect speech verbs: صرخ (shouted) → louder, همس (whispered) → softer
- Add natural pauses between segments
- Prosody control via SSML `<prosody>` tags

**Applies on top of ANY voice approach** — single, two, or multi.

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
| Voice per book | Single profile, no dialect switching | A book is a book. Dialect changes expressions, not just accent |
| Repo structure | Same repo, IPA archived | Zero code overlap. Archive preserves history without interference |
| Dialogue detection | Code-first (state machine + patterns) | LLM only if code can't solve it |
| Review workflow | CSV export, chapter-by-chapter review | Proven in prototypes, manageable scope |
| Character names source | External list (Wikipedia, book info) | Heuristic extraction had 19% false positive rate |
| POC isolation | Data boundaries between POCs | Each POC reads previous POC's file output, not its code |
| SSML generation | Templates applied to verified segments | Trivial once text processing is correct |
| Audio stitching | Per-chapter files, concatenated | Matches review workflow (review by chapter) |
| PDF handling | Out of scope | No OSS tool extracts Arabic PDF text correctly. See research. |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| EPUB paragraph boundaries inconsistent across publishers | Medium | High | Test on 5+ books from different sources |
| Chapter detection fails on unusual structures | Medium | Medium | Fallback: manual chapter markers or size-based splitting |
| Quotation conventions vary wildly between books | High | Medium | Build normalizer, test on 3+ books with different styles |
| Two-voice doesn't sound good enough | Low | High | Already tested in prototypes — voice switching works |
| Multi-voice review is too painful to scale | High | Medium | Accept it as the cost; improve tooling incrementally |
| Azure free tier runs out during testing | Low | Low | Monitor usage, ~$8-12/book if needed |
| Competitor (Lahajati) builds same pipeline | Medium | High | Ship fast, build content moat with published audiobooks |
| AI narration quality insufficient for fiction | Medium | Medium | Start with non-fiction; two-voice masks artifacts |

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

### POC-1 (Book Ingestion) ✓ COMPLETE
- Clean text extraction from EPUB, DOCX, and TXT
- All paragraph boundaries verified by human review
- Tested on 12 books across 3 formats (5 EPUB, 4 DOCX, 3 TXT)
- 21 tests passing, PDF descoped and removed from pipeline

### POC-2 (Chapter Splitting) ✓ COMPLETE
- Detect natural structural delimiters (parts, chapters, sections) across 3+ books
- Respect book's own hierarchy — don't impose rigid "chapter" concept
- All units under Azure SSML limit (~25K chars), sub-split oversized units at paragraph boundaries
- No mid-sentence splits
- Unit files concatenate back to original text
- 91 tests passing, validated on all 12 books

### POC-3 Phase A (Two-Voice) — THE GOAL
- Complete two-voice audiobook from at least 1 real book
- All narration/dialogue boundaries verified via CSV review
- Voice switching sounds natural on listen-through
- Repeatable on a second book with different formatting

### POC-3 Phase B (Multi-Voice) — STRETCH
- Character attribution on at least 1 real book
- CSV review completed for Unknown segments
- Multi-voice audiobook with distinct character voices
- Honest assessment: is the quality improvement worth the review effort?

---

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
| Azure voice capabilities | `docs/02-features/azure-audiobooks/reference/arabic_voices_capabilities.json` |
| Hindawi CC corpus | [hindawi.org](https://www.hindawi.org/) — 3,271 books, CC BY 4.0 |
| Swedish text corpus | [researchdata.se](https://researchdata.se/en/catalogue/dataset/2024-145) — 1,745 books, plain text |
| hindawi-dl | [github.com/shahwan42/hindawi-dl](https://github.com/shahwan42/hindawi-dl) — bulk downloader |
