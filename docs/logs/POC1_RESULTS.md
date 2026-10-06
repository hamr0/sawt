# POC-1 Results: Book Ingestion

**Date completed:** February 2026
**Code:** `src/audiobook/ingest.py` (single file, functions not classes)
**Tests:** `tests/audiobook/test_ingest.py` — 21 tests, all passing

---

## Summary

POC-1 extracts clean Arabic text from EPUB, DOCX, and TXT book files. Output per book:
- `output/{format}/{book}/ingestion/clean_text.txt` — normalized paragraphs separated by blank lines
- `output/{format}/{book}/ingestion/paragraphs.csv` — paragraph inventory (number, char_count, word_count, first_50_chars)

All 12 test books produce clean output. Human-reviewed and confirmed.

---

## Validation Table

| Book | Fmt | Paras | Chars | Max Para | Pres Forms | Tatweel |
|------|-----|------:|------:|---------:|-----------:|--------:|
| al-liss-wal-kilab | .epub | 781 | 125,053 | 6,885 | 0 | 0 |
| awlad-haretna | .epub | 4,299 | 563,115 | 2,039 | 2 | 0 |
| bidaya-wa-nihaya | .epub | 2,273 | 474,467 | 5,146 | 1 | 0 |
| tharthara-fawq-al-nil-hindawi | .epub | 1,496 | 145,808 | 2,234 | 0 | 0 |
| zuqaq-al-midaqq | .epub | 1,412 | 382,792 | 5,008 | 3 | 0 |
| رحلة-ابن-فطومة | .txt | 856 | 124,529 | 2,172 | 0 | 0 |
| صدى-النسيان | .txt | 425 | 81,136 | 2,083 | 0 | 0 |
| يوميات-نائب-في-الأرياف | .txt | 651 | 146,689 | 5,078 | 0 | 0 |
| al-tamheed-fi-tajweed | .docx | 195 | 121,894 | 1,365 | 0 | 12 |
| jawahir-al-adab | .docx | 2,108 | 772,676 | 5,612 | 0 | 298 |
| mabahith-ulum-alquran | .docx | 1,056 | 563,948 | 2,122 | 0 | 231 |
| mawsuat-al-ijaz-al-ilmi | .docx | 1,190 | 748,164 | 1,798 | 0 | 8 |

**Column definitions:**
- **Max Para** — character count of the longest single paragraph. Sanity check for extraction bugs.
- **Pres Forms** — Arabic Presentation Forms (U+FB50-FEFF) found in raw input, all converted to standard Arabic via NFKC.
- **Tatweel** — kashida/tatweel (U+0640) stretching characters stripped during normalization.

---

## What Was Built

### Extractors
- `extract_epub()` — ebooklib + BeautifulSoup. Prefers `<p>` and heading tags, falls back to leaf `<div>`. Filters non-Arabic pages.
- `extract_docx()` — python-docx. Preserves paragraph structure, skips empty paragraphs.
- `extract_txt()` — encoding detection (UTF-8 → CP-1256 fallback).

### Normalization (`normalize_arabic()`)
- NFKC normalization — converts 100% of Presentation Forms to standard Arabic
- Ornate parentheses (U+FD3E/FD3F) — NFKC doesn't decompose, replaced manually
- Tatweel/kashida stripping (U+0640)
- Whitespace collapsing (preserving newlines for paragraph detection)
- Returns stats dict (forms converted, tatweel stripped)

### Paragraph Splitting (`_split_paragraphs()`)
- Blank-line splitting (primary)
- Single-newline fallback for hard-wrapped text (>20 lines, <=3 blank-line chunks)
- Internal newline collapsing within paragraphs

### Orchestrator (`ingest()`)
- Dispatches to correct extractor by file extension
- Output organized by format: `output/{epub,docx,txt}/{book_slug}/ingestion/`
- Prints encoding report to stdout

---

## Test Book Sources

| Format | Count | Source | Quality |
|--------|------:|--------|---------|
| EPUB | 5 | Hindawi Foundation (born-digital, CC BY 4.0) | Excellent — clean `<p>` tags, proper Unicode |
| DOCX | 4 | Internet Archive / Al-Maktaba Al-Shamilah | Good — real Arabic prose, some page number markers |
| TXT | 3 | HuggingFace (alielfilali01/Hindawi-Books-dataset) | Excellent — pre-cleaned Hindawi books |

**Dropped:**
- archive.org OCR EPUB — garbled page footers from OCR scan, not worth cleaning
- Old manual TXT files (awalad-7aretna.txt, book2.txt) — PDF-extracted, fused words

---

## Known Issues for POC-2

1. **DOCX page markers**: Shamela DOCX files embed page references like `(1/406)` as 6-char paragraphs. Not a bug — these are structural metadata. Filter during chapter splitting.
2. **EPUB chapter structure**: Hindawi EPUBs have chapters as separate HTML files in the EPUB spine. Can use this for chapter detection instead of text-based heuristics.
3. **Max paragraph size**: Some paragraphs reach 5-7K chars. May need sub-splitting if Azure SSML has per-segment limits.

---

## Dependencies

```
ebooklib>=0.18
beautifulsoup4>=4.12.0
python-docx>=1.1.0
```

PDF support (pymupdf) removed — PDF is out of scope.
