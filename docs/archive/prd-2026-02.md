# Product Requirements: Arabic Audiobook Production

## Goal

Produce Arabic audiobooks from raw book files (PDF/TXT/EPUB) using Azure Neural TTS with two distinct voices: one for narration, one for dialogue.

## Target Users

- Arabic audiobook producers
- Publishers looking to convert backlist titles to audio
- Individual authors wanting audio versions of their work

## Core Requirements

### POC-1: Book Ingestion
- Accept PDF, TXT, and EPUB input formats
- Extract text preserving paragraph structure
- Normalize Arabic encoding (Presentation Forms → Standard Arabic)
- Strip headers, footers, page numbers, publisher noise
- Output: clean text file + paragraph inventory CSV
- Definition of done: human reads output and confirms "this is the book, nothing missing, nothing garbled"

### POC-2: Chapter Detection & Splitting
- Detect chapter boundaries (numbered, named, structural patterns)
- Handle books with no explicit chapters (split by size at paragraph boundaries)
- Split chapters exceeding Azure character limits at paragraph boundaries
- Handle edge cases: prologue, epilogue, author notes, dedications
- Output: individual chapter files + chapter inventory CSV
- Definition of done: chapter files concatenate back to original text, no weird breaks

### POC-3a: Two-Voice (Primary Goal)
- Binary classification: narration or dialogue
- Handle dialogue markers: colons, em dashes, guillemets, western quotes, hyphens
- Handle multiline dialogue (spans paragraphs)
- Generate SSML with narrator voice + dialogue voice
- Produce audio per chapter, stitch in order
- Output: segmented CSV per chapter + SSML + audio
- Definition of done: complete two-voice audiobook, voice switches feel natural, no text missing

### POC-3b: Multi-Voice (Stretch Goal)
- Character attribution on top of Phase A segments
- External character name list (Wikipedia, book info)
- Gender-matched voice assignment from Azure voice pool
- Handle "Unknown" speakers via CSV review
- Definition of done: multi-voice audiobook with distinct character voices

## Review Workflow

Every pipeline stage produces CSV for human review. Review cadence is chapter-by-chapter: don't move to the next chapter until the current one is verified correct.

## Non-Requirements

- Real-time TTS
- Dialect switching within a book
- Phoneme-level pronunciation control
- Web UI or API (CLI pipeline only)
- LLM-based text processing (code-first approach)

## Test Books

| Book | Format | Notes |
|------|--------|-------|
| أولاد حارتنا (Mahfouz) | TXT | Available, tested in prototypes, 11+ characters |
| TBD Book 2 | PDF | Need PDF to test ingestion |
| TBD Book 3 | varied | Different formatting for generalization |
