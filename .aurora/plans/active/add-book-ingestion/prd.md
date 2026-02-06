# PRD: POC-1 Book Ingestion

## Summary
Extract clean Arabic text from book files (PDF, TXT, EPUB), normalize encoding to standard Arabic, detect paragraph boundaries, and produce structured output for human review and downstream pipeline consumption.

## Requirements

### Functional Requirements

#### FR-1: Format Detection
Automatically detect book file format from extension (`.txt`, `.pdf`, `.epub`) and route to the appropriate extractor.

#### FR-2: TXT Extraction
Read plain text files with encoding detection. Support UTF-8 (primary) and CP-1256 (Windows Arabic fallback). Detect paragraphs by blank line separation.

#### FR-3: PDF Extraction
Extract text from text-based PDFs using PyMuPDF. Strip publisher noise: blank/cover pages, title pages, copyright pages, table of contents, and repeated page headers. Detect paragraph boundaries from text block structure.

#### FR-4: EPUB Extraction
Extract text from EPUB files using ebooklib. Parse HTML content from spine documents. Extract text from block-level elements (`<p>`, `<div>`, `<h1>`-`<h6>`). Preserve paragraph boundaries from HTML structure.

#### FR-5: Arabic Encoding Normalization
Normalize all Arabic Presentation Forms (U+FE70-FEFF, U+FB50-FE6F) to standard Arabic (U+0600-06FF) using NFKC Unicode normalization. Strip tatweel/kashida (U+0640) used for typographic stretching. Normalize whitespace (collapse multiple spaces, normalize line endings).

#### FR-6: Clean Text Output
Write a single clean text file per book to `output/{book_slug}/ingestion/clean_text.txt`. Paragraphs separated by blank lines. No publisher noise, no page numbers, no headers/footers.

#### FR-7: Paragraph CSV Output
Write a paragraph inventory CSV to `output/{book_slug}/ingestion/paragraphs.csv` with columns:
- `paragraph_number` (1-indexed)
- `char_count`
- `word_count`
- `first_50_chars` (preview for review)

#### FR-8: Encoding Report
Print/log a summary of what was normalized: count of presentation forms converted, tatweel characters stripped, encoding detected, pages processed (PDF), chapters found (EPUB).

### Non-Functional Requirements

#### NFR-1: Lossless Extraction
No Arabic text content should be lost during extraction. Verify by comparing total character count (post-normalization) against a reasonable expectation for the source (e.g., ~1500 chars/page for PDF).

#### NFR-2: Simple API
Single entry point: `ingest(book_path: str, output_dir: str = "output") -> dict` returning a summary dict. No classes, no configuration objects for POC.

#### NFR-3: Idempotent
Running ingest twice on the same book produces identical output. Output directory is overwritten, not appended.

## Acceptance Criteria

- AC-1: `ingest("data/books/txt/awalad-7aretna.txt")` produces clean_text.txt with 0 Presentation Forms characters
- AC-2: `ingest("data/books/pdf/al-liss-wal-kilab-hindawi.pdf")` produces clean_text.txt with readable Arabic, no page headers, no copyright page
- AC-3: `ingest("data/books/pdf/zuqaq-al-midaqq-hindawi.pdf")` (202 pages) produces clean_text.txt — largest book works
- AC-4: `ingest("data/books/epub/<test-book>.epub")` produces clean_text.txt from at least 1 EPUB book
- AC-5: `paragraphs.csv` for each book has correct paragraph count (manual spot-check)
- AC-6: All tests pass: `pytest tests/audiobook/test_ingest.py -v`
- AC-7: No Arabic Presentation Forms (U+FE70-FEFF, U+FB50-FE6F) in any output file
