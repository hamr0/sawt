# POC-2 Results: Chapter Detection & Splitting

**Date completed:** February 2026
**Code:** `src/audiobook/chapters.py` (single file, functions not classes)
**Tests:** `tests/audiobook/test_chapters.py` — 91 tests, all passing (125 total with POC-1)

---

## Summary

POC-2 splits clean text from POC-1 into TTS-ready chapter files. Output per book:
- `output/{format}/{book}/chapters/chapter_01.txt`, `chapter_02.txt`, ... — one file per unit, title prepended for TTS
- `output/{format}/{book}/chapters/chapters.csv` — unit inventory (number, name, level, title, char_count, paragraph_count, split_part, total_splits)

All 12 test books produce clean output. 125 tests passing. Human-reviewed.

---

## Validation Table

| Book | Fmt | Units | Delimiter | Page Markers | Sub-splits | Total Chars |
|------|-----|------:|-----------|-------------:|-----------:|------------:|
| al-liss-wal-kilab | EPUB | 18 | heading | 0 | 0 | 123,542 |
| awlad-haretna | EPUB | 114 | eastern_numeral | 0 | 0 | 557,315 |
| bidaya-wa-nihaya | EPUB | 92 | eastern_numeral | 0 | 0 | 473,224 |
| tharthara-fawq-al-nil | EPUB | 18 | eastern_numeral | 0 | 0 | 144,989 |
| zuqaq-al-midaqq | EPUB | 35 | eastern_numeral | 0 | 0 | 381,820 |
| al-tamheed-fi-tajweed | DOCX | 30 | heading | 0 | 0 | 101,657 |
| jawahir-al-adab | DOCX | 60 | heading | 685 | 26 | 745,252 |
| mabahith-ulum-alquran | DOCX | 23 | size | 528 | 0 | 554,967 |
| mawsuat-al-ijaz-al-ilmi | DOCX | 31 | size | 484 | 0 | 743,964 |
| رحلة-ابن-فطومة | TXT | 6 | size | 0 | 0 | 124,453 |
| صدى-النسيان | TXT | 4 | size | 0 | 0 | 81,019 |
| يوميات-نائب-في-الأرياف | TXT | 7 | size | 0 | 0 | 146,611 |

**Column definitions:**
- **Units** — total output files (chapters + sub-splits)
- **Delimiter** — `heading` (الفصل/الباب etc.), `eastern_numeral` (١/٢/٣), or `size` (no delimiters, 25K fallback)
- **Page Markers** — Shamela `(n/m)` annotations filtered out (not content)
- **Sub-splits** — units where a single chapter exceeded 25K and was split into parts (tracked in CSV as split_part/total_splits)

---

## What Was Built

### Detection (`classify_paragraph`, `detect_delimiters`)
- 2 regex patterns: lone Eastern numerals (`^[٠-٩]+$`), Arabic heading terms (`الفصل|الباب|الجزء|القسم|المبحث|المطلب|الفرع|مقدمة|تمهيد|خاتمة|إهداء`)
- 1 filter: Shamela page markers (`^\(\d+/\d+\)$`) — removed from content, not used as delimiters
- Western numeral support (`^[0-9]+$`) included for robustness, untested in corpus
- **Heading conjunction exclusion**: `القسم والشرط` (grammatical) vs `القسم الأول` (structural) — negative lookahead for و prevents false positives

### Dominant Delimiter (`_find_dominant_delimiter`)
- Picks the most common non-page-marker pattern per book
- Stray noise (< 5% of dominant count) is ignored
- Books with no delimiters get pure size-based splitting

### Splitting (`split_into_units`)
- **Hard rule**: never cut mid-paragraph. Paragraphs are atomic.
- **Delimiter OR 25K char limit**, whichever comes first
- **Pre-delimiter content** becomes unit `000` (e.g., book preamble before first chapter)
- **MAX_UNIT_CHARS = 25,000** — Azure SSML usable limit (~64KB / 2 for Arabic UTF-8, minus markup)

### Post-processing (4 passes after main split)
1. **Sub-split pass**: breaks any remaining oversized units at paragraph boundaries (rare — main loop handles most cases)
2. **Parent folding**: empty parent units (e.g., `الباب` with no content before `الفصل`) fold title into child as prefix (`الباب الأول / فصل في التجويد`)
3. **Tiny unit merge**: units below `MIN_UNIT_CHARS = 200` are absorbed into neighbors (leading → prepend to next, trailing → append to previous)
4. **Overflow grouping**: when a chapter exceeds 25K and creates multiple consecutive units, tracks `split_part`/`total_splits` in CSV. Overflow units get names like `الفصل الثاني عشر (2/17)`.

### File I/O (`split_book`)
- Reads `clean_text.txt` from POC-1 output
- Writes chapter files with title prepended for TTS readout
- Writes `chapters.csv` with full unit metadata
- Clears stale chapter files before writing (prevents orphaned files from previous runs)

---

## Key Findings

1. **2 patterns + 1 filter + size fallback covers 100% of corpus** — no need for book-specific logic
2. **EPUB spine is unreliable**: 4 of 5 Hindawi EPUBs have useless spine (1 HTML file for whole book). Text-based detection is primary.
3. **5 of 12 books have no standard delimiters** — pure size fallback works cleanly
4. **jawahir-al-adab is the stress test**: 60 units, 685 page markers filtered, الفصل الثاني عشر spans 399K chars → 17 sub-split parts. Split tracking now works correctly in CSV.
5. **Heading conjunction exclusion matters**: without the و lookahead, phrases like `القسم والشرط` would false-positive as chapter markers
6. **Parent folding handles nesting**: al-tamheed has `الباب` → `الفصل` hierarchy, correctly folded into combined titles
7. **Title prepend for TTS**: chapter headings are included at the top of each chapter file so they're read aloud in the audiobook

---

## POC-1 Refinements Made During POC-2

These were added to `ingest.py` while validating POC-2 output:

1. **Back-matter stripping** (`strip_back_matter`): removes publisher boilerplate from end of Hindawi EPUBs (الناشر, ISBN, حقوق النشر, etc.) + walkback for title/author lines (max 3 steps, < 50 chars each)
2. **Separator stripping**: standalone decorative lines (`====`, `----`, `****`, `•••`, `____`) removed during normalization. Dots `...` preserved (could be speech ellipsis). Verified zero false positives across all 12 books.

---

## CSV Column Reference

| Column | Description |
|--------|-------------|
| unit_number | Sequential 1-based index |
| unit_name | Display name: delimiter text (truncated to 60 chars) or `001`/`002` for size-based |
| level | How this unit was created: `heading`, `eastern_numeral`, `western_numeral`, or `size` |
| title | Full delimiter paragraph text (empty for overflow/size units) |
| char_count | Character count of content (excluding title) |
| paragraph_count | Number of content paragraphs |
| split_part | 0 if chapter fits in one unit; 1-N if chapter was sub-split |
| total_splits | 0 if not split; N = total parts for this chapter |

---

## Dependencies

No new dependencies beyond POC-1. `chapters.py` uses only stdlib (`csv`, `re`, `pathlib`).
