---
title: Input Formats and the PDF Decision
theme: input-formats-pdf
sources:
  - docs/archive/PLAN.md
description: Input format scope (EPUB/DOCX/TXT), why PDF is out of scope, and why Python is the implementation language.
---

# Input Formats and the PDF Decision

## Input formats

(docs/archive/PLAN.md:36-43)

| Format | Role | Status | Rationale |
|--------|------|--------|-----------|
| EPUB | First-class (content source) | Active | Best extraction quality. Born-digital = clean paragraphs + word boundaries. |
| DOCX | First-class (author input) | Adding | Authors write in Word/Google Docs. python-docx handles Arabic cleanly. |
| TXT | Internal-use (bulk corpus) | Supported | Swedish dataset has 1,745 pre-cleaned books. Not user-facing. |
| PDF | Out of scope | Descoped | Intractable word-spacing problem. |

## Why PDF is out of scope

Extensive testing and research (Feb 2026) confirmed that Arabic PDF text extraction is an unsolved problem in the open-source ecosystem. (docs/archive/PLAN.md:47-48)

### What was tested

- PyMuPDF: best RTL reading order, but fused words (spacing stored as coordinates). (docs/archive/PLAN.md:51)
- pdfplumber: same fused words plus worse reading order. (docs/archive/PLAN.md:52)
- Both were tested on 3 Hindawi PDFs: al-Liss wal-Kilab, Tharthara, Zuqaq al-Midaqq. (docs/archive/PLAN.md:53)

### What was found

- Arabic PDFs store word spacing as positional coordinates, not space characters. (docs/archive/PLAN.md:56)
- Words come out fused: `أﻗﻄﻊُﻫﺬا` instead of `أقطعُ هذا`. (docs/archive/PLAN.md:57)
- PyMuPDF closed the Arabic ligature issue as "wontfix" (it requires HarfBuzz); upstream issue 2199 in the PyMuPDF repo. (docs/archive/PLAN.md:58)
- No open-source tool correctly extracts word-spaced Arabic text from PDFs. (docs/archive/PLAN.md:59)
- Shamela, the largest Arabic digital library (15K+ books), uses human transcription, not OCR. (docs/archive/PLAN.md:60)
- Even Amazon refuses Arabic PDF uploads for Kindle and requires EPUB/DOCX. (docs/archive/PLAN.md:61)
- Most Arabic PDFs in the wild are scanned images, which need OCR rather than text extraction. (docs/archive/PLAN.md:62)
- Calibre's Arabic PDF-to-EPUB conversion is broken (text reversed); Launchpad bug 2032531. (docs/archive/PLAN.md:63)

### Why this does not matter for the pipeline

- Hindawi, the primary content source, offers EPUB alongside PDF: same books, clean extraction. (docs/archive/PLAN.md:66)
- Authors, the primary paying audience, write in DOCX, not PDF. (docs/archive/PLAN.md:67)
- The books that would be processed from PDF are available in better formats. (docs/archive/PLAN.md:68)
- Engineering time is better spent on downstream pipeline stages. (docs/archive/PLAN.md:69)

## If PDF is needed later

Recommended path, in order (docs/archive/PLAN.md:71-74):

1. PyMuPDF `rawdict` character-bbox gap detection: untried, most promising, no dependencies.
2. PaddleOCR v5: 40%+ Arabic improvement, free, best OSS OCR for Arabic.
3. Mistral OCR API: 94.9% accuracy, paid, best-in-class.

Full analysis lives in `docs/logs/02-features/ARABIC_PDF_EXTRACTION.md`. (docs/archive/PLAN.md:76)

PDF test outputs are preserved in `output/pdf/` for reference. (docs/archive/PLAN.md:78)

## Language choice: Python

Python is the right tool for this pipeline (docs/archive/PLAN.md:84-90):

- EPUB extraction: ebooklib + BeautifulSoup, proven clean results.
- DOCX extraction: python-docx, handles Arabic text and paragraph structure cleanly.
- Arabic text handling: good Unicode/regex support, NFKC normalization.
- Azure Speech SDK: official `azure-cognitiveservices-speech` package.
- Existing prototype code: all 7 iterations are Python, patterns are proven.
- CSV handling: built-in `csv` module, pandas if needed.

The bottleneck is Azure API latency (~2-3 sec per minute of audio), not local processing speed. Switching languages would mean rewriting all prototype knowledge for zero meaningful gain. (docs/archive/PLAN.md:92-93)
