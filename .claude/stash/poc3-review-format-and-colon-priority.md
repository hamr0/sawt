# POC-3: Review Format, Colon Priority & Continuation Bug

**Date**: 2026-02-06
**Status**: Session complete, one known issue documented

## What was done this session

### 1. Dual output format (segments/ssml + segments/review)
- `segment_chapter()` now writes both:
  - `segments/ssml/chapter_*.csv` — machine-readable for SSML generator
  - `segments/review/chapter_*.txt` — human-editable annotated text
- `parse_review_text()` parses edited review text back to segments
- `sync_review(segments_dir)` re-generates ssml/ CSVs from edited review/ text
- Flow: detection → review + csv → human edits review → sync → csv updated → SSML reads csv

### 2. Colon > guillemet priority reversal
- **Problem**: guillemet-first priority treated scare quotes (`«بالتهوُّر»`, `«الموضوع»`) as dialogue, missing all colon-triggered speeches in same paragraph
- **Fix**: reversed to em dash > colon > guillemet > trailing colon > plain
- Guillemets now only activate when NO colons present (inner thoughts, standalone quoted speech)
- Dialogue ratios improved: zuqaq 31.3% → 47.6%, al-liss 37.5% → 44.4%

### 3. Review text markers: `//` and `\\` (not `«»`)
- `«»` collide with guillemets in source text (scare quotes, quoted words)
- Switched to `// dialogue text \\` — never appears in Arabic literature
- `_segments_to_review_text()` wraps dialogue in `// \\`
- `_split_at_review_markers()` parses them back
- Constants: `REVIEW_OPEN = "//"`, `REVIEW_CLOSE = "\\\\"`

### 4. Phase B multi-voice plan updated
- Wikipedia-sourced character registry (extract names upfront, not heuristic)
- Full name capture for complex Arabic names (أم حميدة, الست سنية عفيفي)
- Corner cases: relational refs (أمه, والدته), occupational refs (الطبيب)
- Attribution from narrator segments: parse subject of speech verbs
- Gender disambiguation: قال (masculine) vs قالت (feminine) → carry forward
- Review format: `//name: dialogue text \\` or `//?: unknown \\`
- Voice mapping: character → Azure voice ID, top 3-5 get unique voices

### 5. Dialect-matched voice selection
- Voice dialect must match book's linguistic origin
- Egyptian author → ar-EG voices, Levantine → ar-LB/ar-SY, etc.
- Never mix dialects within a book — text IS the dialect
- Hindawi catalog = all Egyptian → ar-EG-* voices
- Added to plan with Azure voice inventory table

## Known issue: continuation threshold false positive

**Bug**: Short narration paragraphs (< 200 chars) after dialogue get misclassified as dialogue continuation.

**Example** (awlad-haretna chapter 105):
```
...لكنه قال وهو ثابت في مكانه: حضرة الناظر يطلب عم عرفة!  ← dialogue (correct)
ذهبت عواطف لإبلاغ عرفة دون أن تجد للدعوة...                  ← narrator (misclassified as dialogue)
```

**Root cause**: `CONTINUATION_THRESHOLD = 200`. Short paragraph while IN_DIALOGUE → stays dialogue. The paragraph is ~90 chars, so continuation heuristic keeps it as dialogue.

**Possible fixes discussed**:
- Lower threshold (risks breaking actual dialogue continuation)
- Third-person verb + proper noun detection as narrator signal (complex, NER-adjacent)
- Accept as known limitation, fix in review (user's decision pending)

**User was asked for preference** — no answer yet.

## Commits this session
1. `a6434cd` — feat: Add review text output and review→CSV sync
2. `bc54f50` — fix: Reverse marker priority — colons over guillemets
3. `4c2cc2b` — feat: Switch review text markers from «» to // \\
4. `d200307` — docs: Add detailed multi-voice character attribution plan (Phase B)
5. `df06580` — docs: Add dialect-matched voice selection to plan

## Test status
- 242 tests passing (116 dialogue + 90 chapters + 36 ingest)
- All 12 books regenerated across EPUB/DOCX/TXT

## Files changed
- `src/audiobook/dialogue.py` — dual output, colon priority, `// \\` markers, parse/sync
- `tests/audiobook/test_dialogue.py` — updated for all above
- `docs/02-features/azure-audiobooks/PLAN.md` — Phase B + dialect voice selection

## Current book results (colon-first, all regenerated)
| Book | Format | Chapters | Segments | Dialogue % |
|------|--------|----------|----------|-----------|
| al-liss-wal-kilab | EPUB | 18 | 1,211 | 44.4% |
| awlad-haretna | EPUB | 114 | 7,406 | 45.3% |
| bidaya-wa-nihaya | EPUB | 92 | 3,920 | 35.8% |
| tharthara-fawq-al-nil | EPUB | 18 | 2,133 | 49.3% |
| zuqaq-al-midaqq | EPUB | 37 | 2,679 | 47.6% |
| al-tamheed-fi-tajweed | DOCX | 30 | 320 | 65.4% |
| jawahir-al-adab | DOCX | 60 | 1,667 | 24.3% |
| mabahith-ulum-alquran | DOCX | 23 | 953 | 76.4% |
| mawsuat-al-ijaz-al-ilmi | DOCX | 31 | 1,129 | 51.2% |
| رحلة-ابن-فطومة | TXT | 6 | 1,474 | 38.7% |
| صدى-النسيان | TXT | 4 | 694 | 38.1% |
| يوميات-نائب-في-الأرياف | TXT | 7 | 1,076 | 38.7% |
