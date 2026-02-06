# Stash: POC-3 Dialogue Detection Start

**Date:** 2026-02-05
**Branch:** main
**Last commit:** `151d8aa` — refactor: Polish POC-1/POC-2 modules

---

## Current State

- **POC-1 (Ingestion):** COMPLETE, polished (logging, TypedDict, constants, IngestionError)
- **POC-2 (Chapter Splitting):** COMPLETE, polished (logging, stale file cleanup)
- **126 tests passing** (34 POC-1 + 92 POC-2)
- **12 test books** validated across 3 formats
- **PLAN.md** fully up to date, all polish items marked complete

## POC-3 Phase A: Two-Voice Dialogue Detection

### Decision: Start fresh, don't port prototype

The old prototype (`06_simplified_detector.py`, 330 LOC) was built on dirty text (Presentation Forms, line-based processing, character attribution mixed in). POC-1 NFKC normalization eliminates the encoding issue entirely. Phase A only needs binary classification (narrator vs dialogue), not character attribution.

### What to reuse (concepts only, not code)
- Colon `:` as primary Arabic dialogue marker (100% detection proven)
- State machine: READING → IN_DIALOGUE → READING
- Em dash `–/—` as narrator voice marker
- Multiline dialogue continuation until next marker
- Split-at-colon: `[narration]: [dialogue text]`

### What to drop
- Character name lists and attribution parsing (Phase B)
- Stop word lists (not needed for binary classification)
- Presentation Forms duplicate entries (NFKC handles this)
- Line-by-line processing (use paragraphs from clean_text)

### Input/Output
- **Input:** `output/{format}/{book}/chapters/chapter_*.txt` (from POC-2)
- **Output:** `output/{format}/{book}/segments/chapter_*.csv`
- **CSV columns:** segment_number, type (narrator/dialogue), char_count, text

### Key reference files
- Production prototype: `docs/02-features/azure-audiobooks/reference/prototypes/06_simplified_detector.py`
- Detection findings: `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SIMPLIFIED_DETECTION_FINAL_STATUS.md`
- Colon results: `docs/02-features/azure-audiobooks/reference/prototypes/COLON_BASED_DETECTION_RESULTS.md`
- PLAN POC-3 section: `docs/02-features/azure-audiobooks/PLAN.md` (lines 512-553)

### Architecture note
- User wants simple, clean, isolated packages for easy upgrades
- CLI or bash script wrapper later (not now)
- CSV review at every stage, chapter-by-chapter cadence
- No web UI, no database — files on disk

### Dialogue markers to handle
1. Colon `:` — primary (covers ~95% of Arabic dialogue)
2. Em dash `–/—` — narrator voice segments
3. Guillemets `«»` — quotation marks (rare but present)
4. Multiline continuation — dialogue spanning paragraphs

### Estimate
- ~80-100 LOC for the detector (vs 330 in prototype)
- State machine on paragraphs, not lines
- Should work on all 12 test books (5 fiction EPUBs have dialogue, others may not)
