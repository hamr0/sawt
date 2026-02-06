# Stash: Docs Rebuild + Test Books Added

**Timestamp:** 2026-02-05
**Branch:** main
**Last commit:** b27f7d5 — docs: Update CLAUDE.md, add KNOWLEDGE_BASE.md topic index
**Uncommitted:** EPUB support added to all docs, books reorganized, 3 Hindawi PDFs downloaded

---

## What Happened This Session

### 1. Documentation Rebuild (committed)
- Archived 49 IPA-era docs to `archive/docs/` (preserving tier structure)
- Rebuilt all 5 doc tiers with audiobook-focused content derived from PLAN.md:
  - `00-context/` — vision, assumptions, system-state (fresh)
  - `01-product/prd.md` — audiobook production requirements (fresh)
  - `03-logs/` — fresh logs seeded with restructure entry + prototype insights
  - `04-process/` — dev-workflow, definition-of-done for POC cycle
- Created `docs/KNOWLEDGE_BASE.md` — Tier 2 progressive disclosure topic index
- Updated CLAUDE.md — table format, compressed, Key Patterns, 3-entry docs table

### 2. Test Books Downloaded (uncommitted)
- Reorganized `data/books/` into `{txt/, pdf/, epub/}` subdirs
- Downloaded 3 text-based PDFs from Hindawi Foundation (legally free):
  - `al-liss-wal-kilab-hindawi.pdf` (102 pages, dialogue-heavy crime)
  - `tharthara-fawq-al-nil-hindawi.pdf` (100 pages, very dialogue-heavy)
  - `zuqaq-al-midaqq-hindawi.pdf` (202 pages, lots of characters)
- Verified all have extractable Arabic text with pdfplumber
- Archive.org PDFs were all scanned images (unusable without OCR) — discarded

### 3. EPUB Support Added (uncommitted)
- Updated PLAN.md, PRD, CLAUDE.md, README.md, system-state, assumptions, vision
- All references now say PDF/TXT/EPUB instead of PDF/TXT
- POC-1 scope expanded to include EPUB extraction
- No OCR — text-based PDFs only, EPUB is HTML-based (cleanest source)

---

## Commits This Session

| Hash | Message |
|------|---------|
| 8621000 | docs: Archive IPA-era docs, rebuild for audiobook production |
| b27f7d5 | docs: Update CLAUDE.md, add KNOWLEDGE_BASE.md topic index |

---

## Uncommitted Changes

```
M  CLAUDE.md                          # EPUB references
M  README.md                          # EPUB references, book dir structure
D  data/books/awalad-7aretna.txt      # Moved to data/books/txt/
D  data/books/book2.txt               # Moved to data/books/txt/
M  docs/00-context/assumptions.md     # EPUB assumption added
M  docs/00-context/system-state.md    # Book dir structure, EPUB
M  docs/00-context/vision.md          # EPUB references
M  docs/01-product/prd.md             # EPUB in POC-1 scope
M  docs/02-features/azure-audiobooks/PLAN.md  # EPUB, test books table, Hindawi source
?? data/books/pdf/                     # 3 Hindawi PDFs (23MB total)
?? data/books/txt/                     # Existing TXT books moved here
?? data/books/epub/                    # Empty, ready for EPUB books
```

---

## Current Book Inventory

| Book | Format | Location | Notes |
|------|--------|----------|-------|
| أولاد حارتنا (Mahfouz) | TXT | txt/awalad-7aretna.txt | Tested in prototypes, 11+ chars |
| book2 | TXT | txt/book2.txt | Second test book |
| اللص والكلاب (Mahfouz) | PDF | pdf/al-liss-wal-kilab-hindawi.pdf | 102pp, dialogue-heavy |
| ثرثرة فوق النيل (Mahfouz) | PDF | pdf/tharthara-fawq-al-nil-hindawi.pdf | 100pp, very dialogue-heavy |
| زقاق المدق (Mahfouz) | PDF | pdf/zuqaq-al-midaqq-hindawi.pdf | 202pp, many characters |

---

## Key Findings

- Archive.org Arabic book PDFs are mostly scanned images (no text layer)
- Hindawi Foundation provides proper text-based PDFs, legally free
- pdfplumber extracts Arabic text fine from Hindawi PDFs
- EPUB would be cleanest source (HTML-based, structured) — no EPUB books yet
- No OCR needed if we stick to text-based PDFs and EPUB

---

## Next Steps

- Commit the EPUB/books changes
- Find an EPUB test book (El-Sebai collection on archive.org has EPUB)
- Start POC-1 implementation: `src/audiobook/ingest.py`
