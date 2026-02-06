# Plan: POC-1 Book Ingestion

## Plan ID
`add-book-ingestion`

## Summary
Build the first pipeline stage: extract clean Arabic text from PDF, TXT, and EPUB book files, normalize encoding, detect paragraph boundaries, and produce reviewable CSV output. This is a POC — validate with real books, not perfection.

## Problem Statement
Books arrive as PDF, TXT, or EPUB with inconsistent encoding, formatting, and structure. The Hindawi PDFs use Arabic Presentation Forms encoding (U+FE70-FEFF) instead of standard Arabic (U+0600-06FF). TXT files have the same problem (57% presentation forms in awalad-7aretna.txt). PDFs include publisher noise (cover, copyright, TOC, page headers). No extraction pipeline exists yet — `src/audiobook/ingest.py` is a docstring stub.

### What we learned from research
- **PyMuPDF (fitz)** produces significantly better Arabic text extraction than pdfplumber — correct reading order, cleaner output
- **pdfplumber** extracts text but in reversed/jumbled order for Arabic content
- **`unicodedata.normalize('NFKC')`** eliminates 100% of Presentation Forms characters — proven on the TXT file
- Hindawi PDFs: pages 1-2 are blank/cover, page 3 is title, page 4 is copyright, page 5 is TOC, content starts page 6-7
- Every PDF page starts with the book title as a header — needs stripping
- No EPUB test books yet — need to find one

## Proposed Solution
Three-layer architecture in `src/audiobook/ingest.py`:

1. **Normalizer** — NFKC + Arabic-specific cleanup (tatweel stripping, whitespace normalization)
2. **Format extractors** — TXT reader, PDF reader (PyMuPDF), EPUB reader (ebooklib + BeautifulSoup)
3. **Ingestion orchestrator** — detect format → extract → normalize → paragraph split → write output files + CSV

Single file (`ingest.py`) with clear internal functions. No class hierarchy — this is a POC.

## Benefits
- Unblocks POC-2 (chapter splitting) and the rest of the pipeline
- Validates PDF extraction quality on real Arabic books before committing to the approach
- CSV output enables human review of paragraph boundaries before downstream processing

## Scope

### In Scope
- TXT extraction with encoding detection (utf-8, cp1256)
- PDF extraction via PyMuPDF (primary)
- EPUB extraction via ebooklib + BeautifulSoup (HTML parsing)
- Arabic encoding normalization (NFKC, tatweel, whitespace)
- Publisher noise stripping (cover, copyright, TOC, page headers)
- Paragraph boundary detection (blank lines for TXT, block-level for PDF/EPUB)
- Output: `clean_text.txt` + `paragraphs.csv` per book
- Encoding report: what was normalized
- Finding 1 EPUB Arabic fiction book for testing
- Tests against all 3 formats using real books

### Out of Scope
- OCR for scanned PDFs — text-based only
- Chapter detection (POC-2)
- Dialogue detection (POC-3)
- Perfecting edge cases across 100 books — validate on 4-5 books, fix later
- pdfplumber as fallback (PyMuPDF is clearly better for Arabic)

## Dependencies
- **PyMuPDF** (`pymupdf` package) — already installed, tested
- **ebooklib** — needs `pip install ebooklib`
- **beautifulsoup4** — needs `pip install beautifulsoup4`
- **Test books** — 2 TXT, 3 PDF in `data/books/`, EPUB TBD
- **PLAN.md** — `docs/02-features/azure-audiobooks/PLAN.md` defines output format

## Implementation Strategy
3 phases, ~6 tasks total. Validation-first: get extraction working on real books before polishing.

- **Phase 1**: Normalize + TXT extraction (simplest path, proves the pattern)
- **Phase 2**: PDF + EPUB extraction (the hard parts)
- **Phase 3**: Integration + CSV review output (wire it together, test on all books)

## Risks and Mitigations
| Risk | Impact | Mitigation |
|------|--------|------------|
| PyMuPDF paragraph detection is lossy | Medium | Heuristic: consecutive lines without blank gap = same paragraph. Validate via CSV review |
| EPUB test book has different structure | Low | EPUB is HTML — most consistent format. Parse `<p>` tags |
| Some PDFs have different header patterns | Low | POC scope: handle Hindawi pattern, generalize later |
| NFKC normalization changes meaning | Low | Already tested — zero semantic changes on awalad-7aretna.txt |

## Success Criteria
- [ ] Clean text extraction from TXT, PDF, and EPUB (at least 1 book each)
- [ ] Zero presentation forms in output (all normalized to standard Arabic)
- [ ] Paragraph boundaries match visual inspection of source material
- [ ] `paragraphs.csv` is reviewable — spot-check confirms no garbled or lost text
- [ ] Pipeline runs end-to-end: `ingest("data/books/pdf/al-liss-wal-kilab-hindawi.pdf")` → output files

## Open Questions
1. **EPUB source?** — Need to find 1 Arabic fiction EPUB. **Recommendation**: Check Hindawi Foundation (they publish EPUB), archive.org, or ManyBooks Arabic section.
2. **Strip diacritics?** — Some PDFs have partial diacritics (harakat). **Recommendation**: Keep them. Azure TTS can use them for better pronunciation. Don't strip what might help downstream.
3. **Page header detection** — Hindawi puts book title on every page. **Recommendation**: Simple approach — check if first line of a page matches the book title, strip it. Don't over-engineer.
