# Audiobook Pipeline Guide

End-to-end reference for the Arabic audiobook production pipeline.
Each stage reads the previous stage's output and writes structured artifacts.

## Pipeline Overview

```
Raw Book File (.epub / .docx / .txt)
    │
    ▼
┌──────────────────────────────────────┐
│  POC-1: Ingestion  (ingest.py)       │
│  Extract → Normalize → Paragraphs   │
└──────────────┬───────────────────────┘
               │  01_ingestion/
               │    clean_text.txt
               │    paragraphs.csv
               ▼
┌──────────────────────────────────────┐
│  POC-2: Chapter Splitting            │
│  (chapters.py)                       │
│  Delimiters → Split → Merge         │
└──────────────┬───────────────────────┘
               │  02_chapters/
               │    chapter_01.txt ...
               │    chapters.csv
               ▼
┌──────────────────────────────────────┐
│  POC-3A: Dialogue Detection          │
│  (dialogue.py)                       │
│  Markers → State Machine → Segments  │
└──────────────┬───────────────────────┘
               │  03_segments/
               │    ssml/chapter_01.csv ...
               │    review/chapter_01.txt ...
               │    segments.csv
               ▼
┌──────────────────────────────────────┐
│  POC-4: SSML Generation  (ssml.py)   │
│  (future — not yet implemented)      │
│  Segments → SSML markup              │
└──────────────────────────────────────┘
```

## Directory Layout

All output for a book lives under `output/{format}/{book-slug}/`:

```
output/epub/al-liss-wal-kilab/
├── 01_ingestion/
│   ├── clean_text.txt          # Normalized full text, paragraphs separated by blank lines
│   └── paragraphs.csv          # Paragraph index with char/word counts
├── 02_chapters/
│   ├── chapter_01.txt          # One file per chapter (title + content)
│   ├── chapter_02.txt
│   ├── ...
│   └── chapters.csv            # Chapter index with unit names, levels, char counts
└── 03_segments/
    ├── ssml/
    │   ├── chapter_01.csv      # Machine-readable: segment_number, type, char_count, text
    │   ├── chapter_02.csv
    │   └── ...
    ├── review/
    │   ├── chapter_01.txt      # Human-readable: dialogue wrapped in // ... \\
    │   ├── chapter_02.txt
    │   └── ...
    └── segments.csv            # Per-chapter summary: segment counts, dialogue ratios
```

---

## Stage 1: Ingestion (POC-1)

**Module:** `src/audiobook/ingest.py`
**Entry point:** `ingest(book_path, output_dir="output") → IngestSummary`

### What It Does

Takes a raw book file and produces clean, normalized Arabic text with paragraph boundaries.

### Input

A single file from `data/books/{epub,docx,txt}/`:

| Format | Source | Extractor |
|--------|--------|-----------|
| `.epub` | Hindawi born-digital, archive.org | `extract_epub()` — ebooklib + BeautifulSoup |
| `.docx` | Author manuscripts, Shamela dumps | `extract_docx()` — python-docx |
| `.txt` | HuggingFace/Swedish corpus | `extract_txt()` — UTF-8 with CP-1256 fallback |

### Processing Steps

```
1. EXTRACT raw text from file format
   ├── EPUB: iterate HTML items (sorted by name), prefer <p>/<h> tags
   │         skip pages with <10 Arabic chars (archive.org notices)
   ├── DOCX: iterate doc.paragraphs, skip empty
   └── TXT:  read with encoding detection (UTF-8 → CP-1256)

2. NORMALIZE Arabic encoding
   ├── NFKC normalization (converts ALL Presentation Forms U+FB50-FEFF → standard Arabic)
   ├── Replace ornate parentheses (U+FD3E/FD3F → ASCII parens) — NFKC misses these
   ├── Strip tatweel/kashida (U+0640) — typographic stretching, not semantic
   ├── Strip decorative separator lines (====, ----, ****, etc.) — standalone only
   ├── Collapse runs of whitespace (preserve newlines)
   └── Normalize line endings (CRLF → LF)

3. SPLIT into paragraphs
   ├── Primary: split on blank lines (\n\n)
   ├── Fallback: if ≤3 chunks but >20 lines → split on single newline (hard-wrapped text)
   └── Collapse internal newlines within paragraphs to spaces

4. STRIP back-matter
   ├── Scan last 15 paragraphs for publisher markers (الناشر, ISBN, حقوق النشر, etc.)
   ├── Walk back over short preceding paragraphs (title/author lines <50 chars, max 3 steps)
   └── Remove from cut point to end

5. WRITE output
   ├── clean_text.txt — paragraphs joined by blank lines
   └── paragraphs.csv — index with paragraph_number, char_count, word_count, first_50_chars
```

### Output Artifacts

**`01_ingestion/clean_text.txt`** — The entire book as normalized plain text. Paragraphs are separated by exactly one blank line (`\n\n`). This is the only file the next stage reads.

**`01_ingestion/paragraphs.csv`** — Quality-review index:

```csv
paragraph_number,char_count,word_count,first_50_chars
1,11,2,الفصل الأول
2,3053,508,مرة أخرى يتنفس نسمة الحياة، ولكن في الجو غبار خانق
3,201,32,توقَّفَ عن المسير حتى أدركه الرجل، فتصافحا وهما يُ
```

### Key Design Decisions

- **NFKC eliminates 100% of Presentation Forms** — proven on all 12 test books. No character-level mapping table needed.
- **EPUB prefers `<p>` tags over `<div>`** — prevents duplication when Hindawi EPUBs use `<div>` as containers around `<p>` elements.
- **Paragraph-level granularity from here on** — every downstream stage operates on paragraph boundaries. No mid-paragraph cuts anywhere in the pipeline.

---

## Stage 2: Chapter Splitting (POC-2)

**Module:** `src/audiobook/chapters.py`
**Entry point:** `split_book(ingestion_dir, output_dir=None) → dict`

### What It Does

Reads the clean text and splits it into chapter-sized units, either at structural delimiters (headings, numerals) or by character count (~25K limit for Azure SSML).

### Input

Reads `{book}/01_ingestion/clean_text.txt` — re-splits on blank lines to get paragraphs.

### Processing Steps

```
1. CLASSIFY every paragraph
   ├── Page marker: (1/406) — Shamela noise, filtered out entirely
   ├── Eastern numeral: standalone ١, ٢, ١٠ — chapter number
   ├── Western numeral: standalone 1, 2, 10 — chapter number
   ├── Heading: paragraph starts with structural keyword (الفصل, الباب, المبحث, etc.)
   │   └── Conjunction exclusion: "القسم والشرط" (grammatical) ≠ "القسم الأول" (heading)
   └── Content: regular text paragraph

2. DETECT dominant delimiter
   ├── Count occurrences of each delimiter kind (ignoring page markers)
   ├── Pick the most common kind
   └── Ignore stray noise (<5% of dominant count)

3. SPLIT into raw units
   ├── At each dominant delimiter: close current unit, start new one
   ├── At 25K char overflow: close at paragraph boundary (even mid-chapter)
   └── Content before first delimiter becomes unit "000" (front matter)

4. SUB-SPLIT oversized units
   └── If a unit exceeds 25K chars, split at paragraph boundaries into parts (1/N, 2/N, ...)

5. FOLD empty parents
   ├── A title-only unit (0 content paragraphs) merges into the next unit
   ├── Example: باب (empty) → فصل (with content) becomes "باب / فصل"
   └── Chains accumulate: باب / قسم / فصل

6. MERGE tiny units
   ├── Units below 200 chars merge into the next neighbor
   └── Trailing tiny units merge into the previous unit

7. WRITE output
   ├── chapter_01.txt, chapter_02.txt, ... — title prepended to content
   └── chapters.csv — unit index with metadata
```

### Output Artifacts

**`02_chapters/chapter_01.txt`** (one per unit) — Title on first line (if present), then content paragraphs separated by blank lines. This is what dialogue detection reads.

**`02_chapters/chapters.csv`** — Chapter index for review:

```csv
unit_number,unit_name,level,title,char_count,paragraph_count,split_part,total_splits
1,الفصل الأول,heading,الفصل الأول,11037,82,0,0
2,الفصل العاشر,heading,الفصل العاشر,12055,36,0,0
```

Column meanings:
- `unit_name` — display name (truncated to 60 chars at word boundary)
- `level` — delimiter kind: `heading`, `eastern_numeral`, `western_numeral`, or `size`
- `split_part` / `total_splits` — `0,0` = not split; `1,3` = part 1 of 3 (overflow)

### Key Design Decisions

- **Dominant delimiter** — one pattern per book, not a mix. Prevents false splits from stray numbers in heading-dominated books.
- **Never cut mid-paragraph** — hard rule. Paragraphs are atomic throughout the pipeline.
- **25K char limit** — matches Azure SSML usable payload (~64KB WebSocket limit / ~2.5 bytes per Arabic char, minus SSML markup).
- **5 of 12 test books have no standard delimiters** — pure size-based fallback works fine. Files named `001.txt`, `002.txt`, etc.

---

## Stage 3: Dialogue Detection (POC-3 Phase A)

**Module:** `src/audiobook/dialogue.py`
**Entry point:** `segment_book(chapters_dir, output_dir=None) → dict`

### What It Does

Classifies every paragraph in every chapter as **narrator** or **dialogue**, producing both machine-readable CSVs (for SSML generation) and human-readable review files (for manual correction).

### Input

Reads `{book}/02_chapters/chapter_*.txt` — all chapter files from Stage 2.

### Processing Steps

```
1. DETECT MARKERS per paragraph
   Priority order (first match wins):
   │
   ├── Em dash (– or — at paragraph start + space)
   │   → Whole paragraph = dialogue
   │   → Common in rapid exchanges, modernist Arabic fiction
   │
   ├── Colon (:) — the primary Arabic dialogue marker
   │   ├── Filter out: time colons (digit:digit), URL colons, trailing colons, empty before/after
   │   ├── Find first valid colon position
   │   ├── Check speech attribution:
   │   │   ├── Short text before colon (<150 chars) → always dialogue (short = attribution)
   │   │   └── Long text before colon → requires explicit speech verb in last 100 chars
   │   ├── If speech attribution confirmed:
   │   │   ├── Before colon → narrator (the "said X" part)
   │   │   └── After colon → dialogue (the speech itself)
   │   └── If no speech attribution → entire paragraph = narrator (explanatory colon)
   │
   ├── Trailing colon (paragraph ends with :)
   │   ├── Requires speech verb in the paragraph (not just any trailing colon)
   │   ├── Paragraph itself → narrator
   │   └── Sets state to IN_DIALOGUE for next paragraph only (one-shot)
   │
   └── Plain paragraph (no marker)
       └── Always narrator (no continuation across paragraphs)

2. STATE MACHINE
   Two states: NARRATOR, IN_DIALOGUE
   │
   ├── Start in NARRATOR
   ├── Em dash → emit dialogue, return to NARRATOR
   ├── Colon (with attribution) → emit narrator + dialogue, return to NARRATOR
   ├── Colon (without attribution) → emit narrator, stay NARRATOR
   ├── Trailing colon → emit narrator, enter IN_DIALOGUE
   ├── Plain + IN_DIALOGUE → emit dialogue, return to NARRATOR (one-shot consumed)
   └── Plain + NARRATOR → emit narrator, stay NARRATOR

3. EMIT SEGMENTS
   Each segment: {segment_number, type, char_count, text}
   Empty/whitespace paragraphs are skipped.

4. WRITE DUAL OUTPUT per chapter
   ├── ssml/chapter_01.csv — machine-readable for SSML generator
   └── review/chapter_01.txt — human-readable with // dialogue \\ markers

5. WRITE SUMMARY
   └── segments.csv — per-chapter breakdown of segment counts and dialogue ratios
```

### Output Artifacts

**`03_segments/ssml/chapter_01.csv`** — One CSV per chapter, ready for SSML generation:

```csv
segment_number,type,char_count,text
1,narrator,11,الفصل الأول
2,narrator,3022,مرة أخرى يتنفس نسمة الحياة...
3,dialogue,29,سعيد مهران! .. ألف نهار أبيض!
4,narrator,201,توقَّفَ عن المسير حتى أدركه الرجل...
5,dialogue,22,أشكرك يا معلم بيَّاظة!
```

**`03_segments/review/chapter_01.txt`** — Human-editable annotated text:

```
الفصل الأول

مرة أخرى يتنفس نسمة الحياة...

// سعيد مهران! .. ألف نهار أبيض! \\

توقَّفَ عن المسير حتى أدركه الرجل...

// أشكرك يا معلم بيَّاظة! \\
```

The `//` and `\\` markers delimit dialogue. A reviewer can:
- Add markers around text that should be dialogue
- Remove markers from text that shouldn't be dialogue
- Move marker boundaries within a paragraph

**`03_segments/segments.csv`** — Per-chapter quality dashboard:

```csv
chapter,total_segments,narrator_segments,dialogue_segments,total_chars,narrator_chars,dialogue_chars,dialogue_ratio
chapter_01,140,62,78,10730,7957,2773,0.258
chapter_02,57,25,32,11933,6422,5511,0.462
chapter_03,69,30,39,7813,3239,4574,0.585
```

### Review Workflow

After machine detection, a human reviewer edits the `review/*.txt` files, then syncs corrections back to machine CSVs:

```python
from src.audiobook.dialogue import sync_review

# After editing review files manually:
sync_review("output/epub/al-liss-wal-kilab/03_segments")
# Re-generates ssml/*.csv from review/*.txt
```

`parse_review_text()` reads the annotated format: text inside `// ... \\` becomes dialogue, everything else becomes narrator.

### Speech Attribution Regex

The colon handler uses `COLON_ATTRIBUTION_RE` to verify that text before a colon is genuine speech attribution, not an explanatory/descriptive colon. The pattern matches Arabic speech verbs:

| Category | Verbs |
|----------|-------|
| Basic "said" | قال, قالت, قلت, قلنا, يقول, تقول |
| Response | أجاب, أجابت, سأل, سألت |
| Exclamation | صاح, صاحت, صرخ, صرخت, هتف, هتفت |
| Quiet speech | همس, همست, تمتم, تمتمت, غمغم, غمغمت |
| Questioning | تساءل, تساءلت |
| Continuation | أضاف, أضافت, تابع, أردف |
| Participle | قائلا, قائلة |

**Not included:** `قيل` (passive "it was said") — passive voice indicates reported speech, not direct dialogue.

Diacritics (harakat U+064B-065F, U+0670) are stripped before matching, so `قالَ` matches the same as `قال`.

### Key Design Decisions

- **No continuation across paragraphs** — plain paragraphs always reset to narrator. Searched all 5 novels for real continuation cases; found zero genuine ones, only false positives.
- **Trailing colon is one-shot** — consumes exactly the next paragraph as dialogue, then resets.
- **Guillemets `«»` are NOT dialogue markers** — they appear as scare quotes, inner thoughts, short referenced phrases. Switching TTS voices for a 3-word guillemet phrase mid-sentence would sound jarring. They stay as plain text.
- **Colons override guillemets** — if a paragraph has both a colon and guillemets, the colon is the structural marker. The guillemets inside are typographic.
- **Short attribution shortcut** — text shorter than 150 chars before a colon is almost always speech attribution. Only longer text needs explicit speech verb verification.

---

## Running the Full Pipeline

```python
from src.audiobook.ingest import ingest
from src.audiobook.chapters import split_book
from src.audiobook.dialogue import segment_book

# Stage 1: Ingest
summary = ingest("data/books/epub/al-liss-wal-kilab.epub")
# → output/epub/al-liss-wal-kilab/01_ingestion/

# Stage 2: Split chapters
summary = split_book("output/epub/al-liss-wal-kilab/01_ingestion")
# → output/epub/al-liss-wal-kilab/02_chapters/

# Stage 3: Detect dialogue
summary = segment_book("output/epub/al-liss-wal-kilab/02_chapters")
# → output/epub/al-liss-wal-kilab/03_segments/
```

Each stage is independent — they connect through file output, not code imports. You can re-run any stage without re-running earlier ones (as long as the input directory exists).

## Tests

```bash
pytest tests/audiobook/test_ingest.py -v      # 21 tests
pytest tests/audiobook/test_chapters.py -v     # 90 tests
pytest tests/audiobook/test_dialogue.py -v     # 103 tests
pytest tests/audiobook/ -v                     # All pipeline tests
```

## Test Books (12 total)

| # | Format | Book | Source | Delimiters |
|---|--------|------|--------|------------|
| 1 | EPUB | al-liss-wal-kilab | Hindawi | الفصل headings |
| 2 | EPUB | awlad-haretna | Hindawi | الفصل headings |
| 3 | EPUB | bidaya-wa-nihaya | Hindawi | الفصل headings |
| 4 | EPUB | tharthara-fawq-al-nil-hindawi | Hindawi | الفصل headings |
| 5 | EPUB | zuqaq-al-midaqq | Hindawi | الفصل headings |
| 6 | DOCX | al-tamheed-fi-tajweed | Shamela | الباب/الفصل headings |
| 7 | DOCX | jawahir-al-adab | Shamela | الباب headings |
| 8 | DOCX | mabahith-ulum-alquran | Shamela | المبحث headings |
| 9 | DOCX | mawsuat-al-ijaz-al-ilmi | Internet Archive | None (size-based) |
| 10 | TXT | رحلة-ابن-فطومة | HuggingFace | None (size-based) |
| 11 | TXT | صدى-النسيان | HuggingFace | None (size-based) |
| 12 | TXT | يوميات-نائب-في-الأرياف | HuggingFace | None (size-based) |
