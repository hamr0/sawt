# Stash: POC-3 Guillemet Removal + Pipeline Guide
**Date:** 2026-02-06
**Branch:** main

## What Was Done This Session

### 1. Removed Continuation Logic (COMPLETE)
- Removed `CONTINUATION_THRESHOLD`, `SPEECH_VERB_RE`, `_is_narrator_paragraph()`
- Plain paragraphs always reset to narrator — no continuation across paragraphs
- Exception: trailing colon consumes ONE next paragraph as dialogue (one-shot)
- Searched all 5 novels for real continuation examples — found zero genuine cases, only false positives
- 112→103 tests (removed `TestIsNarratorParagraph` class, updated 4 tests)

### 2. Numbered Output Folders (COMPLETE)
- `ingestion/` → `01_ingestion/`
- `chapters/` → `02_chapters/`
- `segments/` → `03_segments/`
- Updated: ingest.py, chapters.py, dialogue.py, ssml.py docstring
- Updated: all 3 test files (hardcoded paths)
- Renamed all existing output dirs on disk

### 3. Summary CSV (COMPLETE)
- `03_segments/segments.csv` — per-chapter breakdown
- Columns: chapter, total_segments, narrator_segments, dialogue_segments, total_chars, narrator_chars, dialogue_chars, dialogue_ratio
- Written by `segment_book()`, path in return dict as `csv_path`

### 4. Removed Guillemet Splitting (COMPLETE)
- Removed `_split_at_guillemets()` function
- Removed guillemet detection from `detect_markers()` (was returning "guillemet")
- Removed guillemet branch from state machine in `segment_paragraphs()`
- Guillemet paragraphs now fall through as "plain" → narrator
- Rationale: guillemets are typographic quotation marks (short quotes, inner thoughts, scare quotes), NOT dialogue markers. Switching voices for `«3-word phrase»` mid-sentence would be jarring.
- Removed `TestSplitAtGuillemets` class, updated 5 guillemet-related tests

### 5. Plan Update (PARTIAL)
- Updated data flow diagram with numbered folders
- Updated POC-3 Phase A section with full implementation details
- Updated success criteria section
- Still need to update POC-1/POC-2 output path references (minor, docstring-level)

### 6. Full Pipeline Regen (COMPLETE)
- All 12 books regenerated through ingest → chapters → dialogue
- All output in new numbered folder structure
- 238 total tests passing (21 ingest + 90 chapters + 103 dialogue + 24 other)

## What Remains (IN PROGRESS)

### Pipeline Guide Document
- User requested: `docs/guides/pipeline-guide.md`
- Comprehensive MD doc describing each phase: what it reads, input/output, artifacts, logical flow
- Covers POC-1, POC-2, POC-3 Phase A
- Serves as detailed developer guide for later modifications

### Key Content for the Guide
From the code:

**POC-1 (ingest.py)**:
- Input: `data/books/{epub,docx,txt}/book.*`
- Output: `output/{format}/{book}/01_ingestion/clean_text.txt` + `paragraphs.csv`
- Logic: extract → NFKC normalize → strip tatweel → strip separators → paragraph split → strip back-matter → write
- Extractors: `extract_epub()` (ebooklib+BS4), `extract_docx()` (python-docx), `extract_txt()` (encoding detection)

**POC-2 (chapters.py)**:
- Input: `01_ingestion/clean_text.txt`
- Output: `02_chapters/chapter_*.txt` + `chapters.csv`
- Logic: classify paragraphs → detect dominant delimiter → split at delimiters OR 25K chars → sub-split oversized → fold empty parents → merge tiny units → write
- 2 regex patterns (Eastern numerals, Arabic headings) + 1 filter (page markers)

**POC-3 Phase A (dialogue.py)**:
- Input: `02_chapters/chapter_*.txt`
- Output: `03_segments/ssml/chapter_*.csv` + `review/chapter_*.txt` + `segments.csv`
- Logic: detect_markers per paragraph → state machine (em_dash/colon/trailing_colon/plain) → emit segments → write dual output
- 3 markers: em dash, colon (with speech attribution check), trailing colon
- Review flow: edit review text → sync_review() → regenerate CSVs

## Current State
- All code changes committed? NO — changes are unstaged
- Tests: 238 passing
- Output: all 12 books regenerated in new folder structure

## Files Changed
- `src/audiobook/ingest.py` — folder name `01_ingestion`
- `src/audiobook/chapters.py` — folder name `02_chapters`
- `src/audiobook/dialogue.py` — removed continuation, guillemets, added summary CSV, folder name `03_segments`
- `src/audiobook/ssml.py` — docstring update
- `tests/audiobook/test_ingest.py` — folder name updates
- `tests/audiobook/test_chapters.py` — folder name updates
- `tests/audiobook/test_dialogue.py` — removed continuation/guillemet tests, updated assertions, folder names
- `docs/02-features/azure-audiobooks/PLAN.md` — data flow, POC-3 Phase A, success criteria
