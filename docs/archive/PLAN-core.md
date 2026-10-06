---
title: Execution Plan
theme: prd
sources:
  - docs/archive/PLAN.md
description: The live execution plan for Sawt - POC-1 to POC-5 specs, status, rules, success criteria, existing work and what is next.
---
# Execution Plan
## Existing work (prototypes that preceded the pipeline)
Seven prototype iterations (docs/archive/PLAN.md:324-334):
01 quotation marks `«»` (5 dialogues, 0% attribution); 02 name-aware extraction (0%, encoding blocked matching); 03 colon `:` discovery (59 dialogues, breakthrough); 04 RTL-aware heuristics (81% attribution, 19% false positives); 05 multiline state machine (better continuation detection); 06 external name list, production (63.5% attribution, 99.7% text preservation); 07 bug fix debug (recovered 331 lost words).
Key findings (docs/archive/PLAN.md:336-342):
- Colon `:` is the primary Arabic dialogue marker, not quotation marks.
- An external character name list (from Wikipedia) beats heuristic extraction.
- A state machine handles multiline dialogue continuation.
- CSV review workflow is essential for quality verification.
- Presentation Forms vs Standard Arabic is a real problem; NFKC handles 100% of it except ornate parentheses U+FD3E/FD3F.
Production assets meant to evolve into `src/audiobook/` (docs/archive/PLAN.md:344-349): `06_simplified_detector.py` (state machine detector), `character_voice_assignment.py` (voice pool, gender matching, SSML), `azure_integration.py` (Azure SDK wrapper, X-SAMPA), the CSV export review workflow, and 14+ Azure Arabic neural voices across 7 dialects.
## Design principles
(docs/archive/PLAN.md:355-362)
- **POC-first:** build small, test with real books, fix, move on.
- **Review between chapters:** every POC produces CSV for human review.
- **Slice and dice:** perfect each step before the next.
- **One book first:** end-to-end on one book, then generalize.
- **No dialect switching:** one dialect per book, because expressions change across dialects, not just accent. Match the dialect to the book's origin (Egyptian author, Egyptian voices; Levantine, Levantine).
- **Minimize LLM usage:** code-first; LLM only where it demonstrably helps (name extraction).
- **POCs isolated by data:** each POC reads the previous POC's file output, not its code, so any POC can be rewritten without breaking the next.
## Status at a glance
POC-1 COMPLETE, POC-2 COMPLETE, POC-3 Phase A COMPLETE, POC-3 Phase B CLOSED, POC-4 DONE, POC-5 NEXT (docs/archive/PLAN.md:368, 415, 611, 668, 713, 947).
## POC-1: Book Ingestion (EPUB/DOCX to clean text)
**Status:** COMPLETE (Feb 2026); results in `docs/logs/03-logs/POC1_RESULTS.md` (docs/archive/PLAN.md:368).
**Problem:** books arrive as EPUB or DOCX with inconsistent encoding, formatting and structure (docs/archive/PLAN.md:370).
**Scope** (docs/archive/PLAN.md:372-379):
- EPUB extraction (HTML-based, cleanest; born-digital Hindawi).
- DOCX extraction (python-docx, author submissions).
- TXT reading with encoding detection (internal use: Swedish corpus).
- Arabic normalization (Presentation Forms to Standard Arabic via NFKC).
- Preserve paragraph boundaries (critical for later splitting).
- Out of scope: PDF extraction.
**Output** (docs/archive/PLAN.md:381-385):
- `output/{format}/{book}/ingestion/clean_text.txt`
- `output/{format}/{book}/ingestion/paragraphs.csv` with columns paragraph_number, char_count, word_count, first_50_chars
- Encoding report: what was normalized, what was stripped
**What was built** (docs/archive/PLAN.md:387-391): `src/audiobook/ingest.py` (extractors, normalization, paragraph splitting); `tests/audiobook/test_ingest.py` with 21 passing tests; tested on 12 books (5 EPUB Hindawi, 4 DOCX Internet Archive/Shamela, 3 TXT Hindawi via HuggingFace); all output clean and human-validated.
**Known issues handed to POC-2** (docs/archive/PLAN.md:393-395):
- Shamela DOCX files carry page markers like `(1/406)` as separate paragraphs; filter during chapter splitting.
- OCR-based archive.org EPUBs have garbled page footers; dropped from the test set, only born-digital EPUBs used.
**Definition of done:** clean text from EPUB and DOCX that a human reads and says "yes, this is the book, nothing missing, nothing garbled" - met (docs/archive/PLAN.md:397).
**POC-1/POC-2 polish, COMPLETE Feb 2026** (docs/archive/PLAN.md:399-409):

| Item | What was done |
|---|---|
| Logging | `print()` replaced by `logging` (INFO reports, DEBUG paths) in both modules |
| Exceptions | `IngestionError(ValueError)` with book/stage context wrapping third-party errors |
| Return types | `NormStats` and `IngestSummary` TypedDicts |
| Magic numbers | 6 named constants (`MIN_ARABIC_CHARS_PER_PAGE`, `PARAGRAPH_FALLBACK_THRESHOLD`, etc.) |
| Docstring | Usage example added to `ingest.py` |

## POC-2: Chapter Detection and Splitting
**Status:** COMPLETE (Feb 2026); results in `docs/logs/03-logs/POC2_RESULTS.md` (docs/archive/PLAN.md:415).
**Problem:** books use different structural delimiters (chapters, parts, sections) or none. Each structural unit becomes an audio file; units exceeding Azure SSML limits need sub-splitting so stitched audio has no weird breaks (docs/archive/PLAN.md:417-419).

### Hard rules (docs/archive/PLAN.md:421-429)
1. **Never cut mid-paragraph.** All splits land on paragraph boundaries; paragraphs are atomic throughout the pipeline.
2. **Delimiter OR size limit, whichever comes first.** A structural delimiter closes the current unit and starts a new one; accumulated text reaching ~25K chars closes at the last complete paragraph before the limit.
3. **All detection runs on POC-1's `clean_text.txt`.** Format-agnostic, no re-parsing of EPUB/DOCX.

### Azure SSML limit (docs/archive/PLAN.md:431-438)
- 64KB per SSML request (WebSocket); Arabic UTF-8 is ~2 bytes per char plus markup overhead, so **~25,000 usable Arabic chars per request**.
- Max 50 **distinct** `<voice>`/`<audio>` tags per SSML (not 50 total; reusing the same 2 voices is fine); 100K billable characters per file (Standard tier).
- Two-voice uses only 2 distinct voices, well under the limit however many switches occur.

### Delimiter hierarchy: detect, do not impose (docs/archive/PLAN.md:440-456)
| Level | Arabic terms | Examples |
|---|---|---|
| Part (highest) | جزء، الجزء، القسم، الباب | الجزء الأول، الباب الثاني |
| Chapter | فصل، الفصل | الفصل الأول |
| Numbered | Lone number paragraph | ١، ٢، ٣ or 1, 2, 3 |
| Section | مبحث، مطلب، فرع | المبحث الأول |
| Front/back matter | مقدمة، تمهيد، خاتمة، إهداء | مقدمة المؤلف، الخاتمة |
Lone number detection: a paragraph that is ONLY a number followed by text paragraphs is a chapter marker (common in Arabic fiction). It must be a standalone paragraph, and both Western and Eastern Arabic digits match (docs/archive/PLAN.md:453-456).

### Splitting logic (docs/archive/PLAN.md:458-476)
Accumulate paragraphs from the start of the book, then for each next paragraph:
1. A structural delimiter closes the current unit at the paragraph before it; the unit is named by its delimiter (CH1, CH2, P1), and the delimiter paragraph becomes the next unit's first line or title.
2. If adding the paragraph would exceed ~25K chars, close at the last complete paragraph before the limit and name the sub-unit `CH1 - 1/2`, `CH1 - 2/2` (or `P1/CH1 - 1/2` if nested).
3. If a delimiter closes an already sub-split unit, the final sub-unit gets the last number (`CH1 - 3/3`).
4. If no delimiter is ever found, use pure size-based chunks: 001, 002, 003.
Naming (docs/archive/PLAN.md:478-487): `CH1`, `CH2`; split chapters `CH1 - 1/2`, `CH1 - 2/2`; hierarchy `P1/CH1`, `P2/CH1`; nested oversized `P1/CH1 - 1/2`; no delimiters `001`, `002`, `003`; front/back matter use the actual title (`مقدمة`, `خاتمة`).

### What is not detected (docs/archive/PLAN.md:489-497)
- Headers/sub-headers within chapters; with no chapter-level delimiters fall back to size-based splitting (optimized for audiobooks, not research papers).
- Decorative dividers (★ ● ※ •••); scene breaks are not split points and pass through to POC-3 as possible context boundaries.
- Date entries, story titles and other book-specific patterns; too varied, they fall through to size-based splitting.

### EPUB spine and survey of the 12 test books (Feb 2026)
EPUB spine is not a reliable chapter signal (docs/archive/PLAN.md:499-512): al-liss-wal-kilab 18 files = 18 chapters (useful); awlad-haretna 5 files vs ~114 chapters (parts); bidaya-wa-nihaya 1 file vs 92, tharthara-fawq-al-nil 1 vs 26, zuqaq-al-midaqq 1 vs 35 (single-file EPUBs). Only 1 of 5 maps cleanly, so text-based regex on `clean_text.txt` is the catch-all.
Survey (docs/archive/PLAN.md:514-543): EPUB al-liss-wal-kilab `الفصل الأول`... (19); awlad-haretna 114, bidaya-wa-nihaya 92, tharthara-fawq-al-nil 18, zuqaq-al-midaqq 35, all lone Eastern numerals. DOCX al-tamheed-fi-tajweed الباب (11) + الفصل (8) + مقدمة (3) = 22, no noise; jawahir-al-adab الباب (31) + الفصل (16) + مقدمة (1) = 48 with 308 page markers; mabahith-ulum-alquran NONE (528 page markers); mawsuat-al-ijaz-al-ilmi NONE (249 page markers). TXT رحلة-ابن-فطومة NONE (size fallback); صدى-النسيان `•••` + story titles (21, short story collection); يوميات-نائب-في-الأرياف date entries `١٢ أكتوبر` (4, diary).
Key findings (docs/archive/PLAN.md:545-550):
1. Lone Eastern Arabic numerals are the most common pattern: 4 of 5 EPUBs, 259 matches.
2. The `الباب`/`الفصل` hierarchy (باب > فصل) exists in 2 DOCX books and 1 EPUB.
3. 5 of 12 books have zero standard delimiters, so size-based fallback works as designed.
4. Page markers `(n/m)` are noise (1,085 across 3 DOCX books): filter, never split on them.
5. Short paragraphs are dialogue, not headers; do not use paragraph length as a signal.

### Regex patterns (docs/archive/PLAN.md:552-560)
| Priority | What | Regex | Covers |
|---|---|---|---|
| 1 | Lone Eastern Arabic numerals | `^[٠-٩]+$` | 4 EPUBs (259 matches) |
| 2 | Arabic heading terms | `^(الفصل\|الباب\|الجزء\|القسم\|المبحث\|مقدمة\|تمهيد\|خاتمة\|إهداء)` | 1 EPUB + 2 DOCX (70 matches) |
| 3 | Page markers (FILTER OUT) | `^\(\d+/\d+\)$` | 3 DOCX (1,085 noise matches) |
Western digits (`^[0-9]+$`) were not found in the survey but are included for robustness.

### Scope, output, review gate (docs/archive/PLAN.md:562-587)
- Scope: detect delimiters by regex on heading terms and lone numbers; support hierarchy Part (باب) > Chapter (فصل) > Numbered > Section (مبحث) > Front/back matter; two split triggers (delimiter or ~25K chars); paragraph-boundary splits only; numbered sub-split naming; size-only fallback; filter Shamela page markers; tag front/back matter with the actual Arabic title; format-agnostic detection on `clean_text.txt` (docs/archive/PLAN.md:564-572).
- Output: `output/{format}/{book}/chapters/chapter_01.txt`, etc., plus `chapters.csv` with columns unit_number, unit_name, level (part/chapter/numbered/section/frontmatter/size), title, char_count, paragraph_count, split_part, total_splits; and a summary of detected delimiter type (or "none - size-based"), total units, total chars, splits needed (docs/archive/PLAN.md:574-579).
- Review gate: verify CSV boundaries match the real structure; confirm hierarchy; check all splits land on paragraph ends; verify no text lost (char counts sum to the total); read the first and last paragraph of each unit (docs/archive/PLAN.md:581-587).

### Test expectations and definition of done
Same 12 books (docs/archive/PLAN.md:589-595): 5 EPUB fiction expect lone numbers (4) or الفصل headings (1); 2 DOCX religious/academic expect الباب/الفصل plus page-marker filtering; 2 DOCX academic expect no delimiters, size fallback, page-marker filtering; 3 TXT fiction expect no standard delimiters, size fallback (book-specific patterns not worth special-casing).
Definition of done: unit files that concatenate to the original text, no partial paragraphs, every unit under ~25K chars, and a CSV that makes every boundary obvious (docs/archive/PLAN.md:597-601).

## POC-3: Dialogue Detection and Voice Output
The core POC, in two phases: two-voice first, multi-voice second (docs/archive/PLAN.md:607).

### Phase A: narration vs dialogue (two-voice) - THE GOAL
**Status:** COMPLETE (Feb 2026). Code `src/audiobook/dialogue.py`, tests `tests/audiobook/test_dialogue.py` (docs/archive/PLAN.md:609-611).
**Problem:** separate narration from dialogue so different voices can be assigned (docs/archive/PLAN.md:613).
**Scope as built** (docs/archive/PLAN.md:615-622):
- Binary classification narration/dialogue, no character attribution.
- State machine with 3 markers: colon, em dash, trailing colon.
- No continuation across paragraphs; each new paragraph resets to narrator.
- Guillemets `«»` are not markers (treated as plain text).
- Dual output: machine CSV plus human review text with `// \\` markers; review-to-CSV sync for corrections.
- Per-chapter segmentation plus a book-level summary CSV.
**Marker priority** (docs/archive/PLAN.md:624-628):
1. Em dash (`–/—/-` plus space at paragraph start): whole paragraph is dialogue.
2. Colon (`:` with speech attribution before it): before = narrator, after = dialogue.
3. Trailing colon (paragraph ends with `:` plus speech verb): narrator, and the next paragraph becomes dialogue (one-shot).
4. Plain: narrator (or dialogue if immediately after a trailing colon, one-shot only).
**Not markers** (docs/archive/PLAN.md:630-632): guillemets `«»` are typographic quotes for short quotes, inner thoughts and scare quotes, and switching voice for 3-word `«phrases»` would be jarring, so they stay text. No continuation: a plain paragraph after dialogue is narrator; multi-paragraph dialogue without markers does not appear in practice (Mahfouz marks every speaker turn).
**Colon filtering** (docs/archive/PLAN.md:634-641):
- Time colons (`١٢:٣٠`) and URL colons (`http:`) skipped.
- Trailing colons with nothing after are heading-style, skipped unless a speech verb is detected.
- Text before colon under 150 chars assumed dialogue attribution; 150 chars or more requires an explicit speech verb in the last 100 chars.
- Passive `قيل` excluded; harakat stripped before verb matching.
**Output** (docs/archive/PLAN.md:643-646):
- `03_segments/ssml/chapter_*.csv`: segment_number, type, char_count, text
- `03_segments/review/chapter_*.txt`: human review with `// dialogue \\` markers
- `03_segments/segments.csv`: per-chapter summary (total_segments, narrator/dialogue counts, chars, ratio)
**Results (5 fiction EPUBs)** (docs/archive/PLAN.md:648-656):

| Book | Chapters | Segments | Dialogue % |
|---|---|---|---|
| al-liss-wal-kilab | 18 | 1,207 | 40.3% |
| awlad-haretna | 114 | 7,399 | 41.8% |
| bidaya-wa-nihaya | 92 | 3,876 | 31.5% |
| tharthara-fawq-al-nil | 18 | 2,125 | 40.5% |
| zuqaq-al-midaqq | 35 | 2,449 | 45.0% |
**Review workflow** (docs/archive/PLAN.md:658-662): open `review/chapter_*.txt` (dialogue wrapped in `// \\`, narrator plain); add or remove markers to fix errors; run `sync_review(segments_dir)` to regenerate `ssml/*.csv`; review chapter by chapter.
**Definition of done:** a complete two-voice audiobook where narration and dialogue are clearly distinguished, voice switches feel natural, and no text is missing (docs/archive/PLAN.md:664).

### Phase B: character attribution and multi-voice - CLOSED (Feb 2026)
Decision: skip entirely; the complexity is not justified (docs/archive/PLAN.md:668-670). Reasons (docs/archive/PLAN.md:672-680):
1. Azure Arabic has only 2 voices per dialect (1M, 1F); characters C through Z would share them, so no character distinction is possible.
2. Attribution overhead is high: 63.5% automated, 36.5% manual review; unnamed characters need catch-all assignment; heavy em-dash exchanges need turn-tracking.
3. Research consensus: a single narrator with tonal shifts beats full-cast for most listeners; rapid voice-switching in dialogue-heavy scenes sounds robotic.
4. Two-voice already captures ~90% of the value; listeners distinguish characters from context, not voice identity.
Preserved for future use if Azure Arabic improves (docs/archive/PLAN.md:682-687): 7 prototype iterations in `archive/` and `docs/02-features/azure-audiobooks/reference/prototypes/`, the Wikipedia-sourced CSV character registry design, attribution logic (carry-forward, gendered verbs, explicit names), and the per-book character-to-voice mapping design.

### Emotion/prosody enhancement - DEFERRED (waiting on platform)
Azure Arabic voices have zero `mstts:express-as` support (no emotions, styles or HD voices; English has 30+ styles); this is a platform gap, not a pipeline task (docs/archive/PLAN.md:691-693). When Azure adds Arabic styles (docs/archive/PLAN.md:695-699):
- Phase A segment CSVs are the right input; each dialogue segment would need an emotion tag.
- Classification from surrounding narrator context is straightforward (LLM or rule-based).
- Wrapping in `<mstts:express-as style="angry">` is trivial once available.
- Higher value than multi-voice: same 2 voices with emotional range.
Doable now in POC-4 SSML (subtle reinforcement, to be tested) (docs/archive/PLAN.md:701-705): `<prosody rate="+10%">` on dialogue, `<prosody pitch="+5%">` on dialogue, and `<break time="300ms"/>` at narrator/dialogue transitions. Monitor Azure Arabic voice updates, HD availability and `express-as` additions (docs/archive/PLAN.md:707).

## POC-4: SSML Generation and Voice Selection - DONE
**Status:** complete; SSML generation production-ready. POC-4a validated 4 TTS providers, and Google Chirp3-HD and ElevenLabs are viable alternatives to Azure; see `docs/logs/03-logs/POC4_RESULTS.md` (docs/archive/PLAN.md:713). **Code:** `src/audiobook/ssml/core.py` (docs/archive/PLAN.md:715).
**Problem:** turn verified POC-3 segment CSVs into Azure-ready SSML with dialect-matched voices. Input `03_segments/ssml/chapter_*.csv`; output `04_ssml/chapter_*.ssml` (docs/archive/PLAN.md:717-720).
**1. Per-book voice config** (JSON/YAML), set once per book, driving all SSML: `book_dialect: ar-EG`, `narrator_voice: ar-EG-ShakirNeural`, `dialogue_voice: ar-EG-SalmaNeural`. Default for the Hindawi catalog is Egyptian (ar-EG); override per book for other dialects (docs/archive/PLAN.md:724-732).
**2. SSML template engine** (docs/archive/PLAN.md:734-741):
- Read segment CSV; wrap narrator segments in the narrator voice tag and dialogue in the dialogue voice tag; structure `<speak>` > `<voice>` > text.
- Respect limits: max 50 distinct voice names (two-voice uses 2), ~25K chars per request.
- Context-aware breaks: 500ms narrator to narrator (paragraph boundary), 300ms narrator/dialogue (voice transition), 200ms dialogue to dialogue (rapid exchange).
**3. Voice sampling script** `scripts/sample_voices.py` to listen to pairs before committing (docs/archive/PLAN.md:743-749):
- Round 1, pick the dialect: 6 files, same text, 3 dialect pairs (ar-EG, ar-SA, ar-SY), male narrates + female dialogue.
- Round 2, pick the direction: 2 files, winning dialect, male-narrates vs female-narrates.
- Round 3, prosody (only if needed): subtle `<prosody rate/pitch>` tweaks on dialogue.
- Total 8-10 files, ~30K chars, within free tier; MP3s with structured filenames.
**Why an M/F voice switch rather than prosody-only** (docs/archive/PLAN.md:751-757): Azure Arabic prosody has only 3 crude dials (rate, pitch, volume); a 10% speed bump does not signal "someone is speaking"; human narrators use dozens of micro-adjustments TTS cannot replicate; M/F switch is blunt but gives unambiguous contrast; voice switching resets listener attention and masks TTS artifacts; prosody polish is optional on top, not a substitute.
**Prosody (optional, test-driven)** (docs/archive/PLAN.md:759-762): `<prosody rate="+10%" pitch="+5%">` on dialogue only if sampling confirms it helps; generate plain two-voice first and tune only what sounds flat; no `express-as` for Arabic.
**Fiction vs non-fiction paths** (docs/archive/PLAN.md:764-772): fiction maps narrator segments to the narrator voice and dialogue segments to the dialogue voice; non-fiction skips POC-3 and sends chapters straight to SSML with all text in the narrator voice.
**Voice inventory for dialect matching** (docs/archive/PLAN.md:774-784):

| Dialect | Locale | Male | Female | Best for |
|---|---|---|---|---|
| Egyptian | ar-EG | ShakirNeural | SalmaNeural | Mahfouz, Hindawi catalog, modern fiction |
| Saudi | ar-SA | HamedNeural | ZariyahNeural | Gulf authors, religious texts |
| Levantine | ar-SY | LaithNeural | AmanyNeural | Levantine authors (Gibran, Darwish) |
| Jordanian | ar-JO | TaimNeural | SanaNeural | Jordanian authors |
| Lebanese | ar-LB | RamiNeural | LaylaNeural | Lebanese authors |
| Iraqi | ar-IQ | BasselNeural | RanaNeural | Iraqi authors |
| Maghreb | ar-MA | JamalNeural | MounaNeural | North African authors |
**Definition of done:** valid SSML accepted by the Azure TTS API, dialect-matched two-voice output for fiction and single-voice for non-fiction, voice pair chosen through sampling, at least one book fully converted (docs/archive/PLAN.md:786).

## POC-5: Audio Generation (Multi-Provider) - NEXT
(docs/archive/PLAN.md:947-951)
- **Goal:** full book/chapter audio generation from the segments CSV (step 3 output).
- The segments CSV is the universal hand-off point for all providers.
- SSML (step 4) is optional: Azure uses it natively, Google/ElevenLabs skip it.
- Non-SSML providers send plain text per segment and concatenate with silence files.
**Provider architecture** (docs/archive/PLAN.md:953-959):

| Provider | Input | Voice switch | Pauses | SSML |
|---|---|---|---|---|
| Azure | Segments CSV to inline SSML | Multi-voice in 1 request | `<break>` tags | Full |
| Google Chirp3-HD | Segments CSV to plain text | 1 API call per segment | Silence WAV concat | Limited (no `<break>`, no `<voice>`) |
| ElevenLabs | Segments CSV to plain text | 1 API call per segment | `<break>` within segment + silence WAV concat | `<break>` only (no `<voice>`) |
**Settled voice pairings** (V Liked, pairing-tested) (docs/archive/PLAN.md:961-969):

| Provider | Combo | Narrator | Dialogue | Notes |
|---|---|---|---|---|
| Google | FF (primary) | Sulafat | Leda | Smoothest, very good narrator |
| Google | MM | Enceladus | Sadaltager | Good narrator, ok dialogue |
| ElevenLabs | FF (primary) | Sara (MSA) | Alice (Egyptian) | Both interesting, good contrast |
| ElevenLabs | MM | Yahya (MSA) | Karim (MSA) | Very good narrator, ok dialogue |
| ElevenLabs | MF | Moncellence (Egyptian) | Alice (Egyptian) | Both good, dialect-matched |
Full inventory: `docs/02-features/research/final_voices.csv` (19 voices, pairing-tested) (docs/archive/PLAN.md:971).
**Scope** (docs/archive/PLAN.md:973-977): a parameterized script (book, chapter range, provider, voice pairing); pause variation randomized within ranges rather than fixed; full-book generation (chapters, concat, final MP3); output `output/{format}/{book}/05_audio/{provider}/chapter_*.mp3`.

## Success criteria
- **POC-1 (production ready):** clean extraction from EPUB, DOCX, TXT; paragraph boundaries human-verified; 12 books (5 EPUB, 4 DOCX, 3 TXT); 21 tests; PDF descoped and removed (docs/archive/PLAN.md:895-900).
- **POC-2 (production ready):** delimiters detected across 3+ books respecting the book's own hierarchy; all units under ~25K chars, sub-split at paragraph boundaries; no mid-sentence splits; units concatenate to the original; 91 tests, validated on all 12 books (docs/archive/PLAN.md:902-909).
- **POC-3 Phase A (production ready)** (docs/archive/PLAN.md:911-920):
  - Dialogue detection on all 12 books, 103 tests passing; ~95% accuracy on narrator/dialogue split (human-reviewed on صدى النسيان).
  - 3 markers: colon, em dash, trailing colon; no continuation heuristic (false positives outweighed benefit).
  - Guillemets stay narrator text: passages mix inner thoughts and spoken words, and splitting would fragment narration with jarring micro voice-switches.
  - Short story titles (مدد, قمر, علي لوز, etc.) stay inside 25K chapters: read aloud they work as narrator pauses; listener navigation is time-based (30s rewind, bookmarks) and a TOC is complementary, not mandatory.
  - Dual output with sync workflow; per-chapter and book-level summary CSVs.
- **POC-3 Phase B (CLOSED):** skipped; only 2 voices per dialect; 36.5% manual review not justified; rapid switching sounds robotic; most listeners prefer a single narrator with tonal shifts; emotion/prosody deferred until Azure adds Arabic `express-as`; Phase A segment CSVs are the foundation for any future enhancement (docs/archive/PLAN.md:922-928).
- **POC-4 (done)** (docs/archive/PLAN.md:930-945):
  - Valid SSML accepted by Azure; all 12 books converted; 30 tests passing; `src/audiobook/ssml/core.py` is 280 lines.
  - Dialect-matched pairs with breaks of 500/300/200ms; voice coalescing reduces tag count (the 50-tag limit is distinct names, not total elements).
  - POC-4a provider comparison: OpenAI not viable (no Arabic voices); Google Chirp3-HD has 30 Arabic voices, natural, same cost as Azure ($1.16/book); ElevenLabs is best quality at 20x cost ($21.74/book) with 10 user-approved Arabic voices; Mishkal diacritization worsens pronunciation, so plain text stays.
  - POC-4b pairing tests (8 combos: 4 gender pairs x 2 providers, on Chapter 1 of Tharthara Fawq al-Nil): FF is the smoothest; female narrator over male dialogue beats the reverse; same-gender pairings (MM, FF) are the most cohesive.
  - Results: `docs/logs/03-logs/POC4_RESULTS.md`.
- **POC-5 (next):** see the POC-5 section above (docs/archive/PLAN.md:947-977).
