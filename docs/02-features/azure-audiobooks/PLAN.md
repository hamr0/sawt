# Azure Arabic Audiobook Production Plan

**Date:** February 2026
**Goal:** Produce Arabic audiobooks from raw book files (PDF/TXT) using Azure TTS
**Target:** Two-voice audiobooks (narrator + dialogue) as primary deliverable
**Stretch:** Multi-voice (per-character) after two-voice is proven solid
**Cost:** ~$8-12 per 150-page book, free tier available (5M chars/month, 12 months)

---

## Lesson Learned: Why IPA Pipeline Doesn't Apply Here

The repo originally built a full IPA phonological pipeline:
Arabic text → Diacritization → Syllabification → Gemination → Sun Letters → Allophones →
Emphatic Spread → IPA → X-SAMPA → SSML phoneme tags → TTS engine

**It didn't work for audiobooks.** The letter-by-letter phonological processing through SSML
phoneme tags produced output that was too robotic and unintelligible. The assumption that
controlling pronunciation at the phoneme level would improve quality was never validated
early enough — the processing was beautiful and complex, but the output was unusable.

**The audiobook pipeline takes a fundamentally different approach:**
- Send plain Arabic text to Azure neural voices (let Azure handle pronunciation)
- Our job is TEXT STRUCTURE: chapters, paragraphs, dialogue boundaries, character voices
- We don't touch pronunciation at all — Azure's neural models do that better than phoneme-by-phoneme control
- The IPA pipeline (329 tests, 5 dialects) is archived as a learning artifact

**The IPA pipeline and audiobook pipeline share zero code.** LSP confirms 0 imports connect them.
They solve different problems entirely. The IPA work lives in `archive/` for reference.

---

## Language Choice: Python

Python is the right tool for this pipeline:
- **PDF extraction:** pdfplumber/PyPDF2 are mature and battle-tested for Arabic
- **Arabic text handling:** python-arabic-reshaper, good Unicode/regex support
- **Azure Speech SDK:** official `azure-cognitiveservices-speech` package
- **Existing prototype code:** all 7 iterations are Python, patterns are proven
- **CSV handling:** built-in `csv` module, pandas if needed

The bottleneck is Azure API latency (~2-3 sec per minute of audio), not local processing speed.
Switching languages would mean rewriting all prototype knowledge for zero meaningful gain.

---

## Voice Approach Refresher

### Single Voice
- One voice reads everything
- Linguistic accuracy ~80%, flaws easily detected — listener has no "reset" point
- Sounds robotic on long content
- No text processing beyond chapter splitting
- **Use case:** Non-fiction, educational, reference material where no dialogue exists
- **Not a product** — anyone with Azure access can do this, zero differentiation

### Two Voice (Narrator + Dialogue) — PRIMARY GOAL
- Narrator voice for narration, different voice for all dialogue
- Voice switching creates a "listener attention reset" that masks TTS pronunciation artifacts
- Only requires binary classification: "Is this narration or dialogue?"
- Existing colon-based detection already achieves 100% dialogue detection rate
- No character attribution needed — just detect that *someone* is speaking
- Manual review effort: 5-15 min per book (verify narration/dialogue boundaries)
- **Use case:** Fiction, stories, any book with dialogue
- **This is the goal.** Good enough for 70-80% of fiction books

### Multi Voice (Per-Character) — STRETCH
- Unique voice per character, gender-matched, dialect-aware
- The "beast" — character attribution is the hard unsolved problem (63.5% automated, 36.5% manual)
- 7 prototype iterations already invested, competitive with English SOTA (53-69%)
- Manual review effort: 15-40 min per book
- Review was painful — developed CSV workflow to make it bearable
- **Use case:** Dialogue-heavy novels, drama adaptations
- **Attempt after two-voice is solid.** Don't expect an easy win

---

## Why Text Processing Is the Product

The actual pipeline difficulty distribution:

```
Raw Book (PDF/TXT) ──→ Text Extraction & Cleaning      [HARD - not built]
                   ──→ Chapter Detection & Splitting    [HARD - not built]
                   ──→ Narration vs Dialogue Detection  [HARD - 7 iterations, mostly solved]
                   ──→ Character Attribution             [BEAST - 63.5% automated]
                   ──→ SSML Generation                   [EASY - just markup templates]
                   ──→ Azure TTS API                     [EASY - API call]
                   ──→ Audio Stitching                   [EASY - concatenation]
```

Once text is correctly broken into parts, SSML is just wrapping segments in voice tags.
Text processing IS the product. Everything after it is commodity.

---

## Repo Structure

The IPA pipeline is archived. The audiobook pipeline is the active project.
Full details in [REPO_STRUCTURE.md](REPO_STRUCTURE.md).

```
ArabicTTS/
├── src/audiobook/          # ACTIVE - audiobook production pipeline
│   ├── ingest.py           #   POC-1: PDF/TXT → clean text
│   ├── chapters.py         #   POC-2: chapter detection & splitting
│   ├── dialogue.py         #   POC-3: dialogue detection
│   ├── azure_client.py     #   Azure SDK wrapper
│   ├── voice_pool.py       #   Voice selection, gender matching
│   ├── ssml.py             #   SSML generation
│   └── review.py           #   CSV export at every stage
├── tests/audiobook/        # ACTIVE - audiobook tests
├── data/books/             # ACTIVE - input books (PDF/TXT)
├── output/                 # ACTIVE - per-book working output (gitignored)
├── docs/                   # ACTIVE - documentation
├── archive/                # PAUSED - IPA pipeline preserved intact
│   ├── src/                #   core/, dialects/, integrations/, utils/
│   ├── tests/              #   329 tests
│   ├── data/               #   masterTTS.json, test cases
│   ├── scripts/            #   demo, test scripts
│   ├── tools/              #   all tools including prototype history
│   └── app.py              #   Flask API
└── (configs, .env, etc)
```

### Data flow between POCs (isolated by file output, not code imports)

```
data/books/book.txt
    ↓ ingest.py
output/book/ingestion/clean_text.txt + paragraphs.csv    ← REVIEW
    ↓ chapters.py
output/book/chapters/chapter_*.txt + chapters.csv         ← REVIEW
    ↓ dialogue.py
output/book/segments/chapter_*.csv                        ← REVIEW (per chapter)
    ↓ ssml.py
output/book/ssml/chapter_*.ssml
    ↓ azure_client.py
output/book/audio/chapter_*.mp3
```

---

## Existing Work (What We Built)

### Prototypes (7 iterations in `docs/02-features/azure-audiobooks/reference/prototypes/`)

| Iteration | Approach | Result |
|-----------|----------|--------|
| 01 | Quotation marks `«»` | 5 dialogues, 0% attribution |
| 02 | Name-aware extraction | 0% (encoding blocked matching) |
| 03 | Colon `:` discovery | 59 dialogues found (breakthrough) |
| 04 | RTL-aware heuristics | 81% attribution (19% false positives) |
| 05 | Multiline state machine | Improved continuation detection |
| 06 | External name list (production) | 63.5% attribution, 99.7% text preservation |
| 07 | Bug fix debug | Recovered 331 lost words |

### Key findings
- Colon `:` is the primary dialogue marker in Arabic literature, not quotation marks
- External character name list (from Wikipedia) beats heuristic extraction
- State machine approach handles multiline dialogue continuation
- CSV review workflow is essential for quality verification
- Arabic Presentation Forms encoding vs Standard Arabic is a real problem

### Production assets (to evolve into src/audiobook/)
- `06_simplified_detector.py` — production-ready state machine detector
- `character_voice_assignment.py` — voice pool, gender matching, SSML generation
- `azure_integration.py` — Azure SDK wrapper, X-SAMPA support
- CSV export workflow for review at every stage
- 14+ Azure Arabic neural voices across 7 dialects

---

## Execution Plan

### Design Principles
- **POC-first:** Build small, test with real books, fix, move on
- **Review between chapters:** Every POC produces CSV output for human review
- **Slice and dice:** Perfect each step before moving to the next
- **One book first:** Get one book working end-to-end, then generalize
- **No dialect switching:** A book is a book. One voice profile per book. Arabic expressions change across dialects, not just accent — swapping dialects changes meaning
- **Minimize LLM usage:** Code-first, use LLM only where it demonstrably helps (name extraction)
- **POCs isolated by data:** Each POC reads from previous POC's file output, not its code. Rewrite any POC without breaking the next one

---

### POC-1: Book Ingestion (PDF/TXT to clean text)

**Problem:** Books arrive as PDF or TXT with inconsistent encoding, formatting, and structure.

**Scope:**
- PDF text extraction (preserve paragraph structure)
- TXT file reading with encoding detection
- Arabic encoding normalization (Presentation Forms → Standard Arabic)
- Strip headers/footers, page numbers, publisher noise
- Preserve paragraph boundaries (critical for later splitting)

**Output:**
- Clean plain text file per book → `output/{book}/ingestion/clean_text.txt`
- CSV: paragraph inventory → `output/{book}/ingestion/paragraphs.csv`
  - Columns: paragraph_number, char_count, word_count, first_50_chars
- Encoding report: what was normalized, what was stripped

**Review gate:**
- Open the CSV, spot-check paragraphs
- Verify no text was lost or corrupted
- Verify paragraph boundaries are correct
- Compare paragraph count against page count (sanity check)

**Test with:** 2-3 real books in different formats
- `awalad-7aretna.txt` (Mahfouz — already available, TXT)
- At least 1 PDF book

**Definition of done:** Clean text output that a human reads and says "yes, this is the book, nothing missing, nothing garbled"

---

### POC-2: Chapter Detection & Splitting

**Problem:** Books have chapters. Chapters may exceed Azure SSML character limits. Need to split at safe boundaries (end of paragraph, never mid-sentence) so stitched audio doesn't sound weird.

**Scope:**
- Detect chapter boundaries (numbered: "الفصل الأول", named, structural patterns, page breaks)
- Handle books with no explicit chapters (split by size at paragraph boundaries)
- Character limit management — when a chapter exceeds the limit:
  - Split at paragraph boundary
  - Name as "Chapter X (1 of 2)", "Chapter X (2 of 2)"
  - Track segment numbering for reassembly
- Handle edge cases: prologue, epilogue, author notes, dedications

**Output:**
- Individual chapter text files → `output/{book}/chapters/chapter_01.txt`, etc.
- CSV: chapter inventory → `output/{book}/chapters/chapters.csv`
  - Columns: chapter_number, title, char_count, paragraph_count, split_of, total_splits
- Summary: total chapters, total chars, any chapters that needed splitting

**Review gate:**
- Open the CSV, verify chapter boundaries match the actual book
- Check that split chapters break at paragraph ends
- Verify no text lost between chapters (char count should sum to total)
- Read the first and last paragraph of each chapter — do they make sense?

**Test with:** Same books from POC-1, plus 1 book with very long chapters

**Definition of done:** Chapter files that when concatenated reproduce the original text. No weird breaks. CSV makes it obvious where every chapter starts and ends.

---

### POC-3: Dialogue Detection & Voice Output

**This is the core POC. Two phases: two-voice first, multi-voice second.**

#### Phase A: Narration vs Dialogue Detection (Two-Voice) — THE GOAL

**Problem:** Separate narration from dialogue so we can assign different voices.

**Scope:**
- Adapt existing `06_simplified_detector.py` to work on chapter-level input from POC-2
- Binary classification only: narration or dialogue (no character attribution yet)
- Handle dialogue markers: colons, em dashes, guillemets, western quotes, hyphens
- Handle multiline dialogue (dialogue that spans paragraphs)
- Quotation mark normalization across book formatting conventions
- Produce segments tagged as NARRATOR or DIALOGUE

**Output per chapter:**
- Segmented CSV → `output/{book}/segments/chapter_01.csv`
  - Columns: segment_number, type [narrator/dialogue], char_count, text
- Statistics: narration/dialogue ratio, segment count, average segment length

**Review gate (per chapter):**
- Review CSV: is every segment correctly tagged?
- Focus on boundary cases: where does narration end and dialogue begin?
- Flag segments that are mislabeled
- Fix and re-run until chapter is clean
- **Review cadence: chapter by chapter.** Don't move to the next chapter until current one is reviewed and correct

**SSML generation:**
- Once segments are verified, SSML is straightforward:
  - NARRATOR segments → narrator voice tag
  - DIALOGUE segments → dialogue voice tag
  - Paragraph breaks → `<break>` tags
- One voice per role, consistent across the entire book
- No dialect switching — pick best-sounding voice pair for the book's style

**Audio output:**
- Generate audio per chapter → `output/{book}/audio/chapter_01.mp3`
- Stitch chapter audio files in order
- Listen to the result

**Definition of done:** A complete two-voice audiobook where narration and dialogue are clearly distinguished, voice switches feel natural, and no text is missing.

---

#### Phase B: Character Attribution & Multi-Voice (The Beast)

**Do not start this until Phase A is solid on at least 3 books.**

**Problem:** Attribute dialogue segments to specific characters for unique voice assignment.

**Why this is hard (honest assessment):**
- Current automated attribution: 63.5% (remaining 36.5% needs manual review)
- "Unknown" speakers: dialogue without explicit "said X:" attribution
- Pronoun resolution: "he said" → which male character?
- Implicit attribution: dialogue that follows narration about a character
- Arabic-specific challenges: verb-first word order, presentation forms encoding
- Review was painful in prototypes — lots of CSV rows to verify
- This is an active research problem globally, not just for Arabic

**Scope:**
- Layer character attribution on TOP of Phase A's narration/dialogue segments
- Use external character name list (from Wikipedia, book info)
- Apply existing detection: colon patterns, verb+name extraction, gender from verb form
- Everything that doesn't match → "Unknown" → manual CSV review
- Voice assignment: gender-matched, unique per character from Azure voice pool

**Output per chapter:**
- Segmented CSV with character column added → `output/{book}/segments/chapter_01.csv`
  - Columns: segment_number, type, character [name or "Unknown"], gender, char_count, text
- Character summary: detected characters, gender, dialogue count, assigned voice

**Review gate (per chapter):**
- Review CSV focusing on "Unknown" rows
- Assign character to each Unknown based on context
- Verify gender detection is correct
- Review cadence: chapter by chapter, same as Phase A
- Expect 15-40 min review per book at current accuracy

**Definition of done:** Multi-voice audiobook with distinct character voices. Listener can tell which character is speaking. Attribution is correct (verified via CSV review).

**Scaling strategy (future):**
- LLM-assisted name extraction: $0.07-0.15 per book
- Cross-book knowledge base: reuse resolved patterns
- Review interface with context display and quick-pick buttons
- Goal: reduce manual review from 15-40 min to 5-10 min

---

### POC-4: Emotion & Prosody Enhancement (Future Layer)

**Not in scope until POC-3 Phase A is proven.**

**Concept:**
- Detect exclamation marks → raise pitch
- Detect question marks → intonation shift
- Detect speech verbs: صرخ (shouted) → louder, همس (whispered) → softer
- Add natural pauses between segments
- Prosody control via SSML `<prosody>` tags

**Applies on top of ANY voice approach** — single, two, or multi.

---

## Test Books

| Book | Format | Size | Characters | Notes |
|------|--------|------|------------|-------|
| أولاد حارتنا (Mahfouz) | TXT | 34K, 2,717 words | 11+ characters | Available, heavily tested in prototypes |
| TBD Book 2 | PDF | - | - | Need a PDF to test ingestion |
| TBD Book 3 | TXT or PDF | - | - | Different formatting conventions for generalization |

Priority: Find books with different quotation styles, chapter structures, and dialogue density.

---

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Language | Python | PDF libs, Azure SDK, existing prototypes, Arabic text handling |
| Pronunciation | Let Azure handle it (plain text) | IPA letter-by-letter approach was unusable — validated the hard way |
| Voice per book | Single profile, no dialect switching | A book is a book. Dialect changes expressions, not just accent |
| Repo structure | Same repo, IPA archived | Zero code overlap. Archive preserves history without interference |
| Dialogue detection | Code-first (state machine + patterns) | LLM only if code can't solve it |
| Review workflow | CSV export, chapter-by-chapter review | Proven in prototypes, manageable scope |
| Character names source | External list (Wikipedia, book info) | Heuristic extraction had 19% false positive rate |
| POC isolation | Data boundaries between POCs | Each POC reads previous POC's file output, not its code |
| SSML generation | Templates applied to verified segments | Trivial once text processing is correct |
| Audio stitching | Per-chapter files, concatenated | Matches review workflow (review by chapter) |

---

## Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| PDF extraction loses formatting | High | High | Test multiple PDF libraries, compare output |
| Chapter detection fails on unusual structures | Medium | Medium | Fallback: manual chapter markers or size-based splitting |
| Quotation conventions vary wildly between books | High | Medium | Build normalizer, test on 3+ books with different styles |
| Two-voice doesn't sound good enough | Low | High | Already tested in prototypes — voice switching works |
| Multi-voice review is too painful to scale | High | Medium | Accept it as the cost; improve tooling incrementally |
| Azure free tier runs out during testing | Low | Low | Monitor usage, ~$8-12/book if needed |

---

## Success Criteria

### POC-1 (Book Ingestion)
- Clean text extraction from both PDF and TXT
- Zero text loss (verified by char count comparison)
- Correct paragraph boundary detection

### POC-2 (Chapter Splitting)
- Correct chapter boundary detection on 3+ books
- No mid-sentence splits
- Chapter files concatenate back to original text

### POC-3 Phase A (Two-Voice) — THE GOAL
- Complete two-voice audiobook from at least 1 real book
- All narration/dialogue boundaries verified via CSV review
- Voice switching sounds natural on listen-through
- Repeatable on a second book with different formatting

### POC-3 Phase B (Multi-Voice) — STRETCH
- Character attribution on at least 1 real book
- CSV review completed for Unknown segments
- Multi-voice audiobook with distinct character voices
- Honest assessment: is the quality improvement worth the review effort?

---

## References

| Resource | Location |
|----------|----------|
| Production detector | `docs/02-features/azure-audiobooks/reference/prototypes/06_simplified_detector.py` |
| Voice assignment | `docs/02-features/azure-audiobooks/reference/character_voice_assignment.py` |
| Azure integration | `docs/02-features/azure-audiobooks/reference/azure_integration.py` |
| Detection findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SIMPLIFIED_DETECTION_FINAL_STATUS.md` |
| Scalability analysis | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SCALABILITY_ANALYSIS.md` |
| Bug fix history | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/BUG_FIX_TEXT_LOSS_RESOLVED.md` |
| Research findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/QUOTATION_ATTRIBUTION_RESEARCH_FINDINGS.md` |
| Test book | `data/books/awalad-7aretna.txt` |
| Azure voice capabilities | `docs/02-features/azure-audiobooks/reference/arabic_voices_capabilities.json` |
| Market analysis | MEA audiobook market $237.6M (2024) → $1.24B (2030), 31.5% CAGR |
