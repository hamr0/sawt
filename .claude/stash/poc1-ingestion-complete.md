# Stash: POC-1 Book Ingestion — Implementation Complete, PDF Spacing Issue Found

**Timestamp:** 2026-02-05
**Branch:** main (uncommitted)
**Plan:** `.aurora/plans/active/add-book-ingestion/` — all tasks [x]

---

## What Was Built

### `src/audiobook/ingest.py` (full implementation)
- `normalize_arabic(text)` → (cleaned_text, stats_dict) — NFKC + ornate parens + tatweel + whitespace
- `extract_txt(path)` → raw text with encoding detection (utf-8, cp1256)
- `extract_pdf(path)` → text via PyMuPDF, skips blank pages, strips repeated headers
- `extract_epub(path)` → text via ebooklib + BeautifulSoup, filters non-Arabic pages
- `ingest(book_path, output_dir)` → orchestrator: extract → normalize → paragraph split → write files + CSV
- `_split_paragraphs(text)` → blank-line split with fallback to single-newline for hard-wrapped TXT

### `tests/audiobook/test_ingest.py` — 20 tests, all passing
- TestNormalizeArabic (6 tests)
- TestExtractTxt (2 tests)
- TestExtractPdf (2 tests)
- TestExtractEpub (2 tests)
- TestIngest (8 tests — TXT, PDF, EPUB, idempotent, error handling)

### Dependencies added to requirements.txt
- pymupdf>=1.23.0, ebooklib>=0.18, beautifulsoup4>=4.12.0

### EPUB test book downloaded
- `data/books/epub/tharthara-fawq-al-nil.epub` — from archive.org (528KB, OCR-based)

---

## Critical Finding: PDF Word Spacing Issue

**User reviewed all 6 output files. Results:**

| Book | Ext | Source | Readability | Issue |
|------|-----|--------|-------------|-------|
| awalad-7aretna | TXT | Hindawi scan | Good words, bad paragraphs | Hard line wraps = each line is a paragraph |
| book2 | TXT | Unknown | Unreadable | Zero spaces, Latin chars — bad source |
| al-liss-wal-kilab | PDF | Hindawi | Words fused | Missing inter-word spaces |
| tharthara | PDF | Hindawi | Words fused | Same |
| zuqaq-al-midaqq | PDF | Hindawi | Words fused | Same |
| tharthara | EPUB | archive.org | Best | Clean. Minor OCR noise page 1 |

### Root Cause Analysis (PDF)
- Hindawi PDFs store word spacing in **positional coordinates**, not as space characters
- PyMuPDF `get_text('dict')` shows spans with fused text: `أﻗﻄﻊُﻫﺬا` instead of `أﻗﻄﻊُ ﻫﺬا`
- Some spaces exist (partial), others don't — it's inconsistent within the same span
- pdfplumber has the SAME problem + reversed reading order (even worse)
- `get_text('words')` splits at letter boundaries, not word boundaries
- **This is a source data problem**, not an extraction bug

### Possible Fixes (not yet implemented)
1. **Character-position gap detection** — read char-level x-coordinates from PyMuPDF, insert space where gap > threshold
2. **Use different PDF source** — Hindawi may offer better-encoded versions, or find same books as EPUB
3. **NLP word segmentation** — post-process with Arabic word tokenizer (camel-tools, farasa)
4. **Accept and move on** — EPUB works great, use that as primary format

### User's question pending
"Want me to tackle the PDF spacing fix, or note it as a known limitation and focus on EPUB?"

---

## Uncommitted Changes

```
M  requirements.txt                     # Added pymupdf, ebooklib, bs4
M  src/audiobook/ingest.py              # Full POC-1 implementation
M  tests/audiobook/test_ingest.py       # 20 tests
?? data/books/epub/                      # Downloaded EPUB
?? output/                               # Ingestion output for all 6 books
M  .aurora/plans/active/add-book-ingestion/tasks.md    # All [x]
M  .aurora/plans/active/add-book-ingestion/agents.json # All completed
```

Plus prior uncommitted changes from last session:
```
M  CLAUDE.md, README.md, docs/* — EPUB references
D  data/books/awalad-7aretna.txt, book2.txt — moved to txt/
?? data/books/pdf/, data/books/txt/
```

---

## Key Technical Insights

1. **NFKC handles 100% of Presentation Forms** — except ornate parentheses U+FD3E/FD3F (replace manually)
2. **PyMuPDF >> pdfplumber** for Arabic reading order, but both fail on word spacing for Hindawi PDFs
3. **EPUB is the cleanest format** for Arabic text extraction — HTML structure preserves paragraphs and word boundaries
4. **Hindawi blocks EPUB downloads (403)** — archive.org is the free EPUB source
5. **TXT hard-wrap detection**: if blank_lines <= 3 and total_lines > 20, treat each line as a paragraph
6. **ebooklib type mismatch**: archive.org EPUBs use item type 0, not ITEM_DOCUMENT (9) — filter by .html/.xhtml extension instead
