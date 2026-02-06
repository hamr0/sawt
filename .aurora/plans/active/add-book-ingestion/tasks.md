# Tasks: POC-1 Book Ingestion

## Phase 1: Normalize + TXT (prove the pattern)

- [x] 1.1 Add ebooklib and beautifulsoup4 to requirements.txt
  <!-- @agent: @code-developer -->
  - tdd: no
  - verify: `pip install -r requirements.txt`
  - Add `pymupdf>=1.23.0`, `ebooklib>=0.18`, `beautifulsoup4>=4.12.0`
  - **Validation**: All packages install without error

- [x] 1.2 Implement Arabic text normalizer
  <!-- @agent: @code-developer -->
  - tdd: yes
  - verify: `pytest tests/audiobook/test_ingest.py -v -k normalize`
  - Function: `normalize_arabic(text: str) -> tuple[str, dict]`
  - Returns cleaned text + stats dict (presentation_forms_converted, tatweel_stripped, etc.)
  - NFKC normalization, tatweel stripping, whitespace collapse
  - Test with real Presentation Forms strings from awalad-7aretna.txt
  - **Validation**: Feed first 200 chars of TXT book, verify 0 presentation forms in output

- [x] 1.3 Implement TXT extractor + ingest entry point
  <!-- @agent: @code-developer -->
  - tdd: yes
  - verify: `pytest tests/audiobook/test_ingest.py -v -k txt`
  - Function: `extract_txt(path: str) -> str` — read with encoding detection (utf-8, cp1256)
  - Function: `ingest(book_path: str, output_dir: str = "output") -> dict` — orchestrator
  - Paragraph splitting: blank line separation
  - Writes `clean_text.txt` and `paragraphs.csv`
  - Test with `data/books/txt/awalad-7aretna.txt`
  - **Validation**: Output file exists, CSV has correct column headers, text is normalized

## Phase 2: PDF + EPUB extraction (the hard parts)

- [x] 2.1 Implement PDF extractor
  <!-- @agent: @code-developer -->
  - tdd: yes
  - verify: `pytest tests/audiobook/test_ingest.py -v -k pdf`
  - Function: `extract_pdf(path: str) -> str`
  - Use PyMuPDF (fitz) for text extraction
  - Skip blank pages (< 50 chars after strip)
  - Strip page headers: if first line of a page matches a previous page's first line, remove it
  - Paragraph detection: join lines within a text block, blank line between blocks
  - Test with `data/books/pdf/al-liss-wal-kilab-hindawi.pdf`
  - **Validation**: Output has readable Arabic text, no "بﻼﻜﻟاو ﺺﻠﻟا" header on every paragraph

- [x] 2.2 Find and download 1 Arabic fiction EPUB
  <!-- @agent: @code-developer -->
  - tdd: no
  - verify: `ls data/books/epub/*.epub`
  - Check Hindawi Foundation (hindawi.org) — they publish EPUB editions
  - Alternative: archive.org Arabic fiction collection, or ManyBooks
  - Must be: Arabic fiction, legally free, has dialogue
  - Save to `data/books/epub/`
  - **Validation**: File exists and can be opened with ebooklib

- [x] 2.3 Implement EPUB extractor
  <!-- @agent: @code-developer -->
  - tdd: yes
  - verify: `pytest tests/audiobook/test_ingest.py -v -k epub`
  - Function: `extract_epub(path: str) -> str`
  - Use ebooklib to read EPUB, iterate spine documents
  - Parse HTML with BeautifulSoup, extract text from `<p>`, `<div>`, heading tags
  - Paragraph boundary = one per block-level element
  - Test with the EPUB from task 2.2
  - **Validation**: Output has readable Arabic, paragraphs are reasonable length

## Phase 3: Integration + validation (wire it together)

- [x] 3.1 Run ingest on all test books, validate CSV output
  <!-- @agent: @code-developer -->
  - tdd: no
  - verify: `pytest tests/audiobook/test_ingest.py -v`
  - Run `ingest()` on all 5+ books (2 TXT, 3 PDF, 1 EPUB)
  - Write integration tests that verify: output files exist, CSV has rows, zero presentation forms
  - Spot-check: open CSVs manually, verify paragraph previews look correct
  - Compare paragraph counts: TXT ~line-based, PDF ~pages × ~3-5 paragraphs/page
  - **Validation**: All books ingest without error, CSV review shows clean text

- [x] 3.2 Handle edge cases found during validation
  <!-- @agent: @code-developer -->
  - tdd: yes
  - verify: `pytest tests/audiobook/test_ingest.py -v`
  - Fix any issues found in 3.1 (garbled text, lost paragraphs, bad headers)
  - Add regression tests for each fix
  - This task may be empty if 3.1 passes clean — that's fine for a POC
  - **Validation**: All tests pass, CSV spot-check is clean
