---
title: Content Sources and Test Books
theme: content-sources-test-books
sources:
  - docs/archive/PLAN.md
description: Free Arabic content sources, extraction tooling, and the 12 test books used to develop the Sawt pipeline.
---

# Content Sources and Test Books

## Free content for pipeline development and publishing

Four free sources of Arabic books are listed for developing and publishing (docs/archive/PLAN.md:302-309).

| Resource | What | Format | Size | Access |
|----------|------|--------|------|--------|
| Hindawi Foundation | Arabic literature, philosophy, science | EPUB + PDF | 3,271 books (CC BY 4.0) | https://www.hindawi.org/ |
| Arabic E-Book Corpus | Hindawi books pre-converted to clean text | Plain text + HTML | 1,745 books, 81.5M words | https://researchdata.se/en/catalogue/dataset/2024-145 |
| Hindawi HuggingFace | Hindawi content on HuggingFace | Various | Subset | https://huggingface.co/datasets/alielfilali01/Hindawi-Books-dataset |
| Archive.org Arabic | Mixed: scanned + digital books | PDF, some EPUB | Tens of thousands | https://archive.org/details/booksbylanguage_arabic |

(docs/archive/PLAN.md:304-309)

## Tooling

(docs/archive/PLAN.md:311-318)

| Tool | Purpose |
|------|---------|
| hindawi-dl (https://github.com/shahwan42/hindawi-dl) | Bulk download Hindawi books |
| python-docx | DOCX extraction (Arabic paragraph structure) |
| ebooklib + BeautifulSoup | EPUB extraction (proven in POC-1) |
| Calibre (`ebook-convert`) | EPUB and DOCX conversion (Arabic works for this direction) |

## Test books

The test corpus has 12 books across three formats, plus archived PDFs (docs/archive/PLAN.md:790-823).

### EPUB: 5 Hindawi born-digital books (clean)

All five are by Naguib Mahfouz, sourced from Hindawi (docs/archive/PLAN.md:792-800).

| Book | Paras | Chars |
|------|------:|------:|
| al-liss-wal-kilab | 781 | 125K |
| awlad-haretna | 4,299 | 563K |
| bidaya-wa-nihaya | 2,273 | 474K |
| tharthara-fawq-al-nil-hindawi | 1,496 | 146K |
| zuqaq-al-midaqq | 1,412 | 383K |

(docs/archive/PLAN.md:794-800)

### DOCX: 4 Arabic books from Internet Archive/Shamela

(docs/archive/PLAN.md:802-809)

| Book | Subject | Source | Paras | Chars |
|------|---------|--------|------:|------:|
| al-tamheed-fi-tajweed | Quranic recitation | Shamela | 195 | 122K |
| jawahir-al-adab | Arabic rhetoric | Shamela | 2,108 | 773K |
| mabahith-ulum-alquran | Quranic sciences | Shamela | 1,056 | 564K |
| mawsuat-al-ijaz-al-ilmi | Scientific encyclopedia | Shamela | 1,190 | 748K |

Note: Shamela DOCX files contain page number markers (e.g. `(1/406)`), to be filtered in POC-2 (docs/archive/PLAN.md:811).

### TXT: 3 Hindawi books from HuggingFace (clean)

(docs/archive/PLAN.md:813-819)

| Book | Author | Source | Paras | Chars |
|------|--------|--------|------:|------:|
| رحلة-ابن-فطومة | Naguib Mahfouz | HuggingFace | 856 | 125K |
| صدى-النسيان | Naguib Mahfouz | HuggingFace | 425 | 81K |
| يوميات-نائب-في-الأرياف | Tawfiq al-Hakim | HuggingFace | 651 | 147K |

### Archived: PDF (out of scope)

PDFs are kept in `data/books/pdf/` for reference, with output in `output/pdf/`. They are not processed by the active pipeline (docs/archive/PLAN.md:821-823).
