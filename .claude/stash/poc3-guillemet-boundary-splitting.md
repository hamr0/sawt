# POC-3: Guillemet Boundary Splitting

**Date**: 2026-02-05
**Status**: Complete and tested

## What was done

### Problem
Chapter 92 of bidaya-wa-nihaya uses `«»` guillemets for stream-of-consciousness inner monologue mixed with narration. The old code split at colons (which took priority over guillemets), producing a single 1,628-char "dialogue" segment that was mostly narration with `«inner thoughts»` embedded.

### Solution
Changed guillemet priority to be HIGHER than colons. When `«»` are present in a paragraph, split at guillemet boundaries into alternating N/D segments. Colons are ignored (stay in narrator text). When no guillemets, colon logic unchanged.

### Files changed
- `src/audiobook/dialogue.py`:
  - `detect_markers()`: moved guillemet check above colon check
  - New `_split_at_guillemets()`: splits at `«`/`»` boundaries → list of (type, text) tuples
  - `segment_paragraphs()` guillemet case: replaced old colon-first/dominant-content logic with boundary splitting
- `tests/audiobook/test_dialogue.py`:
  - New `TestSplitAtGuillemets` class (9 tests)
  - Updated `test_guillemet_*` tests for new behavior
  - Changed `test_colon_takes_priority_over_guillemet` → `test_guillemet_takes_priority_over_colon`
  - Added `test_guillemet_multiple_blocks`, `test_guillemet_stream_of_consciousness`

### Test results
- 227 tests passing (101 dialogue + 90 chapters + 36 ingest)
- All 5 EPUB integration tests pass

### Book ratios (after guillemet change)
| Book | Dialogue % |
|------|-----------|
| al-liss-wal-kilab | 37.5% |
| zuqaq-al-midaqq | 31.3% |
| tharthara-fawq-al-nil | 46.7% |
| awlad-haretna | 40.5% |
| bidaya-wa-nihaya | 31.9% |

### Key decisions
- **Guillemets > colons**: When both present, guillemet boundaries used, colons stay in narrator text
- **Marker priority order**: em dash > guillemets > colon > trailing colon > plain
- **Trade-off accepted**: In zuqaq paragraphs where a colon triggers spoken dialogue containing a brief `«inner quote»`, the colon-triggered speech now gets tagged as narrator (because guillemets take priority). The guillemet-quoted portion is correctly tagged as dialogue. This slightly reduces zuqaq's dialogue ratio (47.6% → 31.3%) but correctly handles bidaya-style stream-of-consciousness.

### Other work this session
1. Stripped `//` and `\\` markers from `output/epub/zuqaq-al-midaqq/chapters/chapter_30.txt`
2. Saved annotated copy as `chapter_30-annotated.txt`
3. Regenerated all 5 EPUB segment CSVs
4. Chapter 30 analysis: 56/57 paragraphs match user's markings, 1 edge case (line 53 mid-paragraph D→N→D)

### What's next
- POC-3 Phase A is feature-complete
- User may want to review segment CSVs for bidaya-wa-nihaya and other books
- POC-3 Phase B (character attribution) or POC-4 (SSML generation) would be next pipeline steps
- The `..` dramatic pause pattern noted in earlier session could become SSML `<break>` in POC-4
