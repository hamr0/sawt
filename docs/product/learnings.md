---
title: Learnings
description: Everything Sawt learned through POC-1..4 and research, organized by topic, with links to evidence.
updated: 2026-10-05
---

# Learnings

Single home for what the Sawt pipeline (Arabic audiobooks from EPUB/DOCX/TXT) learned through its POCs and research. Organized by topic, not by POC or date. Product requirements live in [prd.md](prd.md); this file is the "why we know" behind them.

Evidence links: [POC-1](../logs/POC1_RESULTS.md), [POC-2](../logs/POC2_RESULTS.md), [POC-3](../logs/POC3_RESULTS.md), [POC-4](../logs/POC4_RESULTS.md), [insights](../logs/insights.md), [decisions log](../logs/decisions-log.md), [PDF extraction research](../logs/ARABIC_PDF_EXTRACTION.md), [market research](../wiki/MARKET_RESEARCH.md), [repo structure](../wiki/REPO_STRUCTURE.md), [distribution](../wiki/AUDIOBOOK_DISTRIBUTION.md). The "Domain Knowledge" section of the root `CLAUDE.md` is the compact current-truth summary.

Citations of the form `(PLAN:N-M)` refer to the original big plan (formerly `docs/archive/PLAN.md`).

## Contents

1. [Current status](#1-current-status)
2. [Product scope and positioning](#2-product-scope-and-positioning)
3. [Arabic text and encoding](#3-arabic-text-and-encoding)
4. [Input formats and the PDF decision](#4-input-formats-and-the-pdf-decision)
5. [Chapter splitting](#5-chapter-splitting)
6. [Dialogue detection](#6-dialogue-detection)
7. [Voice and dialect strategy](#7-voice-and-dialect-strategy)
8. [TTS providers, SSML and audio generation](#8-tts-providers-ssml-and-audio-generation)
9. [Cost](#9-cost)
10. [Architecture and dev principles](#10-architecture-and-dev-principles)
11. [Content sources and test books](#11-content-sources-and-test-books)
12. [Go-to-market and risks](#12-go-to-market-and-risks)
13. [Best-practices alignment](#13-best-practices-alignment)
14. [Tried and abandoned](#14-tried-and-abandoned)
15. [Success criteria as met](#15-success-criteria-as-met)
16. [Superseded views](#16-superseded-views)
17. [Runner + UI build (2026-10-05)](#17-runner--ui-build-2026-10-05)
18. [Reference index](#18-reference-index)

---

## 1. Current status

| Stage | Status |
|---|---|
| POC-1 ingest (EPUB/DOCX/TXT to clean text) | Done, production ready |
| POC-2 chapter detection and splitting | Done, production ready |
| POC-3 Phase A dialogue detection (two-voice) | Done, ~95% accuracy |
| POC-3 Phase B character attribution / multi-voice | CLOSED (skipped) |
| POC-4 SSML generation + provider/voice selection | Done |
| Stage 5 audio generation (POC-5) | NEXT, not built |

- **Production TTS provider: Gemini 3.8 Flash TTS** (`gemini-3.8-flash-tts`), narrator Sulafat + dialogue Leda (FF), with `speech_metadata.style` direction. Decided 2026-10-05 ([POC-4c](../logs/POC4_RESULTS.md)). Google Chirp3-HD (same voice names) is the content-block fallback.
- Product requirements: [prd.md](prd.md).
- Status summary line from the plan: POC-1 COMPLETE, POC-2 COMPLETE, POC-3 Phase A COMPLETE, POC-3 Phase B CLOSED, POC-4 DONE, POC-5 NEXT (PLAN:368, 415, 611, 668, 713, 947).
- Pipeline difficulty distribution (PLAN:219-229): text extraction/cleaning Done; chapter detection Done; narration vs dialogue Done (~95%); character attribution Closed; SSML + voice selection Done (was "Next"); the TTS API call is easy; audio stitching is easy (concatenation).

---

## 2. Product scope and positioning

### Text processing IS the product
- Once text is correctly broken into parts, SSML is just wrapping segments in voice tags and TTS is a commodity API call. Everything after text processing is commodity (PLAN:231-232).
- Let the TTS engine handle pronunciation; we handle structure: chapters, paragraphs, dialogue boundaries. Evidence: the IPA pipeline failure (see [section 14](#14-tried-and-abandoned)).
- Motivation is commercial and personal: make Arabic audiobooks accessible.

### Fiction only (decision Feb 2026, PLAN:99)
- Sawt is optimized for fiction (novels, short stories) with dialogue. **Fiction = two voices (narrator + dialogue). Non-fiction = single voice, skip dialogue detection entirely.**
- Why: on non-fiction the dialogue detector produces false positives by design (PLAN:103-107):
  - Quranic verses in `{}` are citations, not dialogue.
  - Scientific quotations: `قال العلماء:` triggers colon detection but is indirect speech.
  - Scholarly citations / references to historical figures are not dramatic dialogue.
  - Example: `mawsuat-al-ijaz-al-ilmi` (smoking health encyclopedia) marked citations as dialogue throughout. Validation: academic DOCX books had low dialogue ratios and this one showed false positives ([POC-3](../logs/POC3_RESULTS.md)).
- Non-fiction works better as single-voice narration; the pipeline is built for dramatic dialogue, not scholarly references (PLAN:109). Single voice needs no text processing beyond chapter splitting (POC-1, POC-2, SSML). It is not a core product and is deferred until demand validates it (PLAN:138-142, 132).

| Content type | Sawt approach | Why |
|---|---|---|
| Fiction | 2+ voices (narrator + dialogue) | Dramatic exchanges, clear speaker turns, voice switching adds life |
| Non-fiction | Single voice (skip POC-3) | Citations are not "performed" dialogue; needs authoritative consistency |
| Special cases | Manual quote (contact us) | Quranic recitation with tajweed, custom multi-voice academic content |

- Documentation wording: "Sawt produces multi-voice audiobooks for Arabic fiction. For non-fiction, academic texts, or custom projects, contact us." Do not build genre detection; document it instead.
- Future pipeline wrapper takes a `--genre` flag (earlier name: `--fiction` / `--non-fiction`): fiction (default) runs all stages, non-fiction skips dialogue detection and goes straight to single-voice SSML (PLAN:123-130). Example: `python pipeline.py --book path/to/novel.epub --genre fiction` / `--genre non-fiction`. For now, process fiction only.
- Test book `mawsuat-al-ijaz-al-ilmi` proves non-fiction needs a single voice.

### Competitive moat
- Nobody else has built a raw-book-to-audiobook pipeline for Arabic. Competitors are either TTS engines (sell the voice; user handles everything) or audiobook platforms (distribute, do not produce). The text pipeline bridges the gap (PLAN:235-239). Full analysis: [market research](../wiki/MARKET_RESEARCH.md). Competitor to watch: Lahajati (Arabic TTS, 500+ voices, $9-30/mo).

---

## 3. Arabic text and encoding

- **NFKC normalization eliminates 100% of Arabic Presentation Forms (U+FE70-FEFF)**, proven on all 12 books. Presentation Forms vs Standard Arabic was a real prototype-era problem (encoding blocked name matching in prototype 02). Evidence: [POC-1](../logs/POC1_RESULTS.md).
- **Ornate parentheses (U+FD3E/FD3F) survive NFKC** and are replaced manually.
- **Harakat (diacritics, U+064B-065F, U+0670) must be stripped before any speech-verb regex** (see [dialogue detection](#6-dialogue-detection)).
- NFKC made the old detector's encoding workarounds pointless; this is why the detector was rewritten rather than ported ([section 14](#14-tried-and-abandoned)).
- Arabic punctuation is author/publisher dependent; there is no universal standard. It was only formalized in 1912 (Ahmad Zaki Pasha) and standardized in 1933 by the Cairo Academy. Modern is not cleaner: formatting is author-dependent, not era-dependent. Hindawi EPUBs are the most consistently formatted (born-digital editorial standards). See [Arabic dialogue conventions](#6-dialogue-detection).
- Short paragraphs are dialogue, not headers; never use paragraph length as a heading signal (POC-2).
- Mishkal diacritization makes TTS pronunciation worse; send plain text ([section 8](#8-tts-providers-ssml-and-audio-generation)).

---

## 4. Input formats and the PDF decision

| Format | Role | Status | Rationale |
|---|---|---|---|
| EPUB | First-class (content source) | Active | Best extraction quality. Born-digital = clean paragraphs + word boundaries |
| DOCX | First-class (author input) | Active | Authors write in Word/Google Docs; python-docx handles Arabic cleanly |
| TXT | Internal-use (bulk corpus) | Supported | Swedish dataset of 1,745 pre-cleaned books; not user-facing |
| PDF | **Out of scope, permanently** | Descoped | Intractable word-spacing problem |

(PLAN:36-43)

### Why PDF is out (research Feb 2026, PLAN:47-78)
Evidence: [Arabic PDF extraction research](../logs/ARABIC_PDF_EXTRACTION.md), [POC-1](../logs/POC1_RESULTS.md).
- Tested PyMuPDF (best RTL reading order, but fused words) and pdfplumber (same fused words plus worse reading order) on 3 Hindawi PDFs: al-Liss wal-Kilab, Tharthara, Zuqaq al-Midaqq. The failure reproduced exactly with both: it is a source-data problem, not a tooling problem, and more extraction effort would not help. Recognizing that early stopped a futile detour.
- Arabic PDFs store word spacing as positional coordinates, not space characters. Words extract fused: `أﻗﻄﻊُﻫﺬا` instead of `أقطعُ هذا`.
- PyMuPDF closed the Arabic ligature issue as "wontfix" (requires HarfBuzz); upstream issue 2199.
- No open-source tool correctly extracts word-spaced Arabic text from PDFs.
- Shamela (largest Arabic digital library, 15K+ books) uses human transcription, not OCR.
- Even Amazon refuses Arabic PDF uploads for Kindle and requires EPUB/DOCX.
- Most Arabic PDFs in the wild are scanned images, which need OCR. (Early corpus sourcing from Archive.org hit exactly this: those PDFs were scanned images with no text layer and were discarded. Lesson: text-layer quality varies wildly by source; verify extractability before adopting a book.)
- Calibre Arabic PDF-to-EPUB conversion is broken (text reversed; Launchpad bug 2032531). Do not use. (Calibre `ebook-convert` works for EPUB/DOCX conversion direction.)

### Why it does not matter
- Hindawi (primary content source) offers EPUB alongside PDF: same books, clean extraction.
- Authors (primary paying audience) write in DOCX, not PDF.
- The books that would come from PDF are available in better formats; engineering time is better spent downstream.

### If PDF is ever needed (recommended order, PLAN:71-74)
1. PyMuPDF `rawdict` character-bbox gap detection (untried, most promising, no dependencies).
2. PaddleOCR v5: 40%+ Arabic improvement, free, best OSS Arabic OCR.
3. Mistral OCR API: 94.9% accuracy, paid, best in class.

PDF books stay in `data/books/pdf/` and test outputs in `output/pdf/` for reference only; PDF extraction code and the pymupdf dependency were removed.

### EPUB / DOCX / TXT extraction notes
- EPUB: prefer `<p>` tags over `<div>` (a container-div bug appeared with Hindawi EPUBs). Tooling: ebooklib + BeautifulSoup.
- DOCX: python-docx. Shamela DOCX files carry page markers like `(1/406)` as separate paragraphs; POC-1 leaves them, POC-2 filters them.
- TXT: read with encoding detection.
- Preserve paragraph boundaries; they are critical for later splitting.
- Hindawi blocks direct EPUB downloads (403); needs User-Agent + Referer headers.
- OCR-based archive.org EPUBs have garbled page footers; dropped from the test set, only born-digital EPUBs used.
- POC-1 outputs: `01_ingestion/clean_text.txt`, `paragraphs.csv` (paragraph_number, char_count, word_count, first_50_chars), plus an encoding report (what was normalized/stripped). POC-1 definition of done: a human reads the text and says "yes, this is the book, nothing missing, nothing garbled" (met). Polish done Feb 2026: `logging` replaced `print()`; `IngestionError(ValueError)` with book/stage context; `NormStats`/`IngestSummary` TypedDicts; 6 named constants (`MIN_ARABIC_CHARS_PER_PAGE`, `PARAGRAPH_FALLBACK_THRESHOLD`, etc.); usage-example docstring.

### Language: Python
(PLAN:84-93) EPUB via ebooklib + BeautifulSoup; DOCX via python-docx; good Unicode/regex and NFKC; the Azure Speech SDK (`azure-cognitiveservices-speech`) is official; all 7 prototypes are Python; built-in `csv` (pandas if needed). The bottleneck is TTS API latency (~2-3 sec per minute of audio with Azure), not local processing; switching languages would rewrite all prototype knowledge for zero gain.

---

## 5. Chapter splitting

Evidence: [POC-2](../logs/POC2_RESULTS.md).

### Hard rules (PLAN:421-429)
1. **Never cut mid-paragraph.** All splits land on paragraph boundaries; paragraphs are atomic through the entire pipeline.
2. **Delimiter OR size limit, whichever comes first.** A structural delimiter closes the current unit; accumulated text reaching ~25K chars closes at the last complete paragraph before the limit.
3. **All detection runs on `clean_text.txt`.** Format-agnostic; no re-parsing of EPUB/DOCX.

### Why 25K chars (Azure ceiling)
- 64KB per SSML request (WebSocket); Arabic UTF-8 is ~2 bytes per char plus markup overhead, so **~25,000 usable Arabic chars per request**.
- Azure max 50 **distinct** `<voice>`/`<audio>` tags per SSML (not 50 total; reusing the same 2 voices is fine). Two-voice uses 2 distinct voices, so the limit never binds ([POC-4](../logs/POC4_RESULTS.md)).
- Azure Standard tier: 100K billable characters per file. Azure free tier: 5M chars/month for 12 months, ~$8-12 per 150-page book.
- The 25K ceiling is kept as the unit size even though Gemini (production) has its own limits (requests of ~1,500 chars in the POC-4c test; see [section 8](#8-tts-providers-ssml-and-audio-generation)).

### Delimiter hierarchy: detect, do not impose (PLAN:440-456)
| Level | Arabic terms | Examples |
|---|---|---|
| Part (highest) | جزء، الجزء، القسم، الباب | الجزء الأول، الباب الثاني |
| Chapter | فصل، الفصل | الفصل الأول |
| Numbered | Lone number paragraph | ١، ٢، ٣ or 1, 2, 3 |
| Section | مبحث، مطلب، فرع | المبحث الأول |
| Front/back matter | مقدمة، تمهيد، خاتمة، إهداء | مقدمة المؤلف، الخاتمة |

- Lone number detection: a paragraph that is ONLY a number followed by text paragraphs is a chapter marker (common in Arabic fiction). Must be a standalone paragraph; both Western and Eastern Arabic digits match.
- **Dominant delimiter**: detection picks the most common pattern per book and ignores stray noise.
- **Parent folding**: empty parent units (باب to فصل) fold the title into the child as a prefix.
- **Heading conjunction exclusion**: `القسم والشرط` (grammatical) vs `القسم الأول` (structural), handled with a negative lookahead for و.

### Splitting logic (PLAN:458-476)
Accumulate paragraphs; for each next paragraph:
1. A structural delimiter closes the current unit at the paragraph before it; the unit is named by its delimiter (CH1, CH2, P1) and the delimiter paragraph becomes the next unit's first line/title.
2. If adding the paragraph would exceed ~25K chars, close at the last complete paragraph before the limit; sub-units named `CH1 - 1/2`, `CH1 - 2/2` (or `P1/CH1 - 1/2` if nested).
3. If a delimiter closes an already sub-split unit, the final sub-unit gets the last number (`CH1 - 3/3`).
4. If no delimiter is ever found, pure size-based chunks: 001, 002, 003.

Naming (PLAN:478-487): `CH1`, `CH2`; split `CH1 - 1/2`; hierarchy `P1/CH1`, `P2/CH1`; nested oversized `P1/CH1 - 1/2`; no delimiters `001`...; front/back matter use the actual title (`مقدمة`, `خاتمة`).

### What is not detected (PLAN:489-497)
- Headers/sub-headers within chapters; with no chapter-level delimiters fall back to size-based splitting (optimized for audiobooks, not research papers).
- Decorative dividers (star, bullet, `•••`); scene breaks are not split points and pass through to dialogue detection as possible context boundaries.
- Date entries, story titles and other book-specific patterns; too varied (book-specific patterns are not worth special-casing), they fall through to size-based splitting.
- Short story titles (مدد, قمر, علي لوز, etc.) stay inside 25K chapters: read aloud they work as narrator pauses; listener navigation is time-based (30s rewind, bookmarks) and a table of contents is complementary, not mandatory.

### EPUB spine is unreliable (PLAN:499-512)
al-liss-wal-kilab: 18 files = 18 chapters (useful); awlad-haretna: 5 files vs ~114 chapters (parts); bidaya-wa-nihaya: 1 file vs 92; tharthara-fawq-al-nil: 1 vs 26; zuqaq-al-midaqq: 1 vs 35 (single-file EPUBs). Only 1 of 5 maps cleanly (3 are single-file), so text-based regex on `clean_text.txt` is primary; spine is a bonus.

### Survey of the 12 test books (PLAN:514-550)
- EPUB: al-liss-wal-kilab `الفصل الأول`... (19 matches); awlad-haretna 114, bidaya-wa-nihaya 92, tharthara-fawq-al-nil 18, zuqaq-al-midaqq 35, all lone Eastern numerals.
- DOCX: al-tamheed-fi-tajweed الباب (11) + الفصل (8) + مقدمة (3) = 22, no noise; jawahir-al-adab الباب (31) + الفصل (16) + مقدمة (1) = 48 with 308 page markers; mabahith-ulum-alquran NONE (528 page markers); mawsuat-al-ijaz-al-ilmi NONE (249 page markers).
- TXT: رحلة-ابن-فطومة NONE (size fallback); صدى-النسيان `•••` + story titles (21, short story collection); يوميات-نائب-في-الأرياف date entries `١٢ أكتوبر` (4, diary).

Key findings:
1. Lone Eastern Arabic numerals are the most common pattern: 4 of 5 EPUBs, 259 matches.
2. The `الباب`/`الفصل` hierarchy (باب > فصل) exists in 2 DOCX books and 1 EPUB.
3. 5 of 12 books have zero standard delimiters; size-based fallback is a supported path, not a failure.
4. Page markers `(n/m)` are noise (1,085 across 3 DOCX books): filter, never split on them.
5. Short paragraphs are dialogue, not headers.

### Regex patterns (PLAN:552-560)
| Priority | What | Regex | Covers |
|---|---|---|---|
| 1 | Lone Eastern Arabic numerals | `^[٠-٩]+$` | 4 EPUBs (259 matches) |
| 2 | Arabic heading terms | `^(الفصل\|الباب\|الجزء\|القسم\|المبحث\|مقدمة\|تمهيد\|خاتمة\|إهداء)` | 1 EPUB + 2 DOCX (70 matches) |
| 3 | Page markers (FILTER OUT) | `^\(\d+/\d+\)$` | 3 DOCX (1,085 noise matches) |

Western digits (`^[0-9]+$`) were not found in the survey but are included for robustness.

### Scope, output, review gate (PLAN:562-587)
- Scope: regex on heading terms and lone numbers; hierarchy Part (باب) > Chapter (فصل) > Numbered > Section (مبحث) > Front/back matter; two split triggers; paragraph-boundary splits only; numbered sub-split naming; size-only fallback; filter Shamela page markers; tag front/back matter with the actual Arabic title.
- Output: `02_chapters/chapter_01.txt`, etc., plus `chapters.csv` (unit_number, unit_name, level [part/chapter/numbered/section/frontmatter/size], title, char_count, paragraph_count, split_part, total_splits) and a summary of detected delimiter type (or "none - size-based"), total units, total chars, splits needed.
- Review gate: CSV boundaries match real structure; hierarchy confirmed; all splits land on paragraph ends; no text lost (char counts sum to total); read the first and last paragraph of each unit.
- Test expectations (PLAN:589-595): 5 EPUB fiction expect lone numbers (4) or الفصل headings (1); 2 DOCX religious/academic expect الباب/الفصل plus page-marker filtering; 2 DOCX academic expect no delimiters, size fallback, page-marker filtering; 3 TXT fiction expect no standard delimiters, size fallback.
- Definition of done: unit files concatenate to the original text, no partial paragraphs, every unit under ~25K chars, a CSV that makes every boundary obvious (met; 90-91 tests, validated on all 12 books).

---

## 6. Dialogue detection

Evidence: [POC-3](../logs/POC3_RESULTS.md), [insights](../logs/insights.md). Code: `src/audiobook/dialogue/core.py`.

### Core findings
- **The colon `:` is THE universal Arabic dialogue marker**, not quotation marks. It appears in every book, era and publisher. Prototype 03 (colon discovery) was the breakthrough (59 dialogues, vs 5 with `«»` and 0% attribution).
- **Attribution always comes before the quote** (unlike English before/middle/after).
- Five markers exist in the wild: colon (most common), dash (rapid exchanges), guillemets (quoted speech), quotation marks, none. Nested dialogue: outer layer = colon, inner layer = guillemets or parentheses.
- The paragraph-per-speaker rule is WEAK: Mahfouz puts multiple speakers in one paragraph via `فقال` chains. (Sources for the research: Cogent Arts 2024 paper, Netflix Arabic style guide.)
- Two-voice needs only binary classification (narrator/dialogue); no character attribution. Colon-based detection achieves ~100% dialogue detection on fiction; manual review per book ~5-15 minutes to verify boundaries. Good enough for 70-80% of fiction books.

### Marker priority (final): em dash > colon > trailing colon > plain (narrator)
1. **Em dash** (`–/—/-` plus space at paragraph start): whole paragraph is dialogue, dash stripped from output.
2. **Colon** (`:` with speech attribution before it): text before = narrator, text after = dialogue to end of paragraph. Paragraph = unit: once a colon triggers dialogue, the entire post-colon text is dialogue.
3. **Trailing colon** (paragraph ends with `:` plus speech verb): narrator; the next paragraph becomes dialogue (**one-shot**: consumes exactly one following paragraph, then resets).
4. **Plain**: narrator (or dialogue only if immediately after a trailing colon).
- Because the colon is attribution-then-quote, said-tags stay with the narrator voice automatically.

### Guillemets `«»` are NOT dialogue (deliberate decision; do not "fix")
- They are typographic quotes for short quotes, inner thoughts and scare quotes (example `«بالتهوُّر»`). Switching voice for a 3-word `«phrase»` mid-narration is jarring.
- Passages mix inner thoughts and spoken words; splitting would fragment narration with micro voice-switches. Inner thought + speech by the same person = one voice for cohesion.
- History: guillemets were once promoted above colons (to fix Chapter 92 of bidaya-wa-nihaya, where inner-monologue guillemets were swallowed into one oversized segment). Dialogue ratios shifted book by book (zuqaq fell 47.6% to 31.3%). It misclassified scare quotes and missed colon-triggered speech in the same paragraph; priority was reversed back to colon-first (zuqaq recovered to 47.6%), then guillemet logic was deleted outright. Lesson: a plausible rule that solves one chapter can quietly degrade the rest of the corpus; verify against the whole corpus ([section 14](#14-tried-and-abandoned)). The earlier prototype-era rule "colons override guillemets; guillemets as fallback only when no colons present" is superseded.

### No continuation heuristic
- A plain paragraph after dialogue resets to narrator. A full-corpus search across all 5 novels found zero genuine cross-paragraph continuation cases, only false positives. Arabic authors mark every speaker turn (Mahfouz marks every turn); multi-paragraph unmarked dialogue does not appear in practice.
- Superseded: the earlier design kept plain paragraphs as dialogue until >200 chars AND no speech verbs.

### Colon filtering
- Skip time colons (`١٢:٣٠`, digit:digit), URL colons (`http:`).
- Trailing colons with nothing after are heading-style; skipped unless a speech verb is detected.
- Text <150 chars before a colon assumes dialogue attribution; >=150 chars requires an explicit active speech verb in the last 100 chars.
- Passive `قيل` is excluded from the verb regex. Harakat are stripped before verb matching.

### Review format
- Human review markers are `// dialogue \\`. `«»` was tried first and collided with guillemets already in the source text; `// \\` never occurs naturally in Arabic literature. Lesson: pick review syntax that cannot collide with the data it annotates.
- Workflow: open `review/chapter_*.txt` (dialogue wrapped in `// \\`, narrator plain); add/remove markers; run `sync_review(segments_dir)` (with `parse_review_text()`) to regenerate `ssml/*.csv`; review chapter by chapter.
- Outputs: `03_segments/ssml/chapter_*.csv` (segment_number, type [narrator|dialogue], char_count, text); `03_segments/review/chapter_*.txt`; `03_segments/segments.csv` (per-chapter summary: total_segments, narrator/dialogue counts, chars, ratio). `03_segments/` is the universal hand-off for all TTS providers.
- Definition of done: a complete two-voice audiobook where narration and dialogue are distinguished, voice switches feel natural, no text missing.

### Results
Dialogue ratios, 5 fiction EPUBs (current): al-liss-wal-kilab 18 ch / 1,207 segs / 40.3%; awlad-haretna 114 / 7,399 / 41.8%; bidaya-wa-nihaya 92 / 3,876 / 31.5%; tharthara-fawq-al-nil 18 / 2,125 / 40.5%; zuqaq-al-midaqq 35 / 2,449 / 45.0%. صدى-النسيان: 4 chapters / 619 segs / 28.0%. ~95% accuracy on the narrator/dialogue split, human-reviewed on صدى النسيان. Earlier-iteration numbers (al-liss 44.4%, zuqaq 47.6%, tharthara 49.3%, awlad 45.3%, bidaya 35.8%) predate removal of continuation/guillemets and are superseded. Non-fiction DOCX books: low ratios; mawsuat-al-ijaz-al-ilmi false positives.

### Prototype lineage (7 iterations, `tools/azure_tts/prototypes/`, now reference/archived)
01 quotation marks `«»` (5 dialogues, 0% attribution); 02 name-aware extraction (0%, encoding blocked matching); 03 colon `:` discovery (59 dialogues); 04 RTL-aware heuristics (81% attribution, 19% false positives); 05 multiline state machine; 06 external name list, production (63.5% attribution, 99.7% text preservation); 07 bug-fix debug (recovered 331 lost words) (PLAN:324-334).
Key findings (PLAN:336-342): colon is primary; an external character name list (Wikipedia) beats heuristic extraction; a state machine handles multiline continuation (later deleted for the two-voice product); CSV review is essential; NFKC solves Presentation Forms.
Assets that were meant to evolve into `src/audiobook/` (PLAN:344-349): `06_simplified_detector.py`, `character_voice_assignment.py`, `azure_integration.py`, the CSV review workflow, 14+ Azure Arabic neural voices across 7 dialects.
Rewrite lesson: a 330-line prototype detector existed but was built on dirty text and mixed attribution into the same logic. We kept the concepts (colon marker, state machine, em dash) and dropped stop-word lists, name lists and line-based processing. Once a foundational fix removes the reason for old complexity, a smaller rewrite beats a port.

---

## 7. Voice and dialect strategy

### Single / two / multi voice
- **Two voice (narrator + dialogue) is the product for fiction.** Voice switching creates a "listener attention reset" that masks TTS pronunciation artifacts.
- **Multi-voice per-character is CLOSED (Feb 2026, POC-3 Phase B)** (PLAN:668-687). Reasons:
  1. Azure Arabic has only 2 voices per dialect (1M, 1F); characters C through Z would share them.
  2. Attribution overhead is high: 63.5% automated in prototypes, 36.5% manual review per book; unnamed characters (the officer, the neighbor, the mayor) need catch-all assignment for marginal gain; heavy em-dash exchanges (10-line) need turn tracking and create rapid voice switching that sounds robotic.
  3. Research consensus: a single skilled narrator with tonal shifts beats full-cast for most listeners; multi-voice is the exception (drama adaptations, big-budget productions).
  4. Two-voice captures ~90% of the value with ~10% of the complexity; listeners distinguish characters from context, not voice identity.
- Revisit only if Azure Arabic adds more voices plus emotion styles; Phase A segment CSVs are the right foundation. Preserved for future use: 7 prototypes in `archive/` and `docs/02-features/azure-audiobooks/reference/prototypes/`, the Wikipedia-sourced CSV character registry design, attribution logic (carry-forward, gendered verbs, explicit names), per-book character-to-voice mapping design. The `voice_pool/` and `shared/` packages remain stubs; "voice_pool" was folded into the SSML module (two-voice is a 3-field config, not a separate module).

### Why an M/F (voice) switch rather than prosody-only (PLAN:751-757)
- Azure Arabic prosody has only 3 crude dials (rate, pitch, volume); a 10% speed bump does not signal "someone is speaking".
- Human narrators use dozens of micro-adjustments TTS cannot replicate; a voice switch is blunt but gives unambiguous contrast and resets listener attention, masking TTS artifacts. Prosody polish is optional on top, never a substitute.

### Dialect matching: one dialect per book
- **One dialect per book, matched to the book's origin** ("a book is a book"). Egyptian author gets `ar-EG`, Levantine gets `ar-SY/JO/LB`. Dialect changes meaning, not just accent. Never mix dialects within a book (no Gulf narrator with Egyptian dialogue). The text is the dialect; do not change either, match them. (Analogy: a Mahfouz novel read by a Gulf voice is like dubbing a British film in a Texas accent.)
- Matching signals (PLAN:187-191): author's nationality/dialect primary (Mahfouz Egyptian, Gibran Levantine); the book's setting secondary (a novel set in Baghdad gets Iraqi voices even if the author is Egyptian); publisher origin tertiary (Hindawi catalog: Egyptian by default). All voices in a book share the dialect.
- For the Hindawi catalog (Phase 1: 20-30 books) default is Egyptian `ar-EG`; override per book.
- Per-book voice config set once and applied across stages: `book_dialect: ar-EG`, `narrator_voice: ar-EG-ShakirNeural`, `dialogue_voice` (earlier name `dialogue_default_voice`): `ar-EG-SalmaNeural`.
- Caveat found in POC-4a: Azure "dialect" voices are MSA readers with different speakers, not different pronunciation models. Exception: Syrian voices genuinely carry a Levantine literary feel; Syrian sounded best and Egyptian Azure most robotic even for Mahfouz.

### Azure voice inventory by dialect (14+ neural voices, 7 dialects; historical, now fallback only)
| Dialect | Locale | Male | Female | Best for |
|---|---|---|---|---|
| Egyptian | ar-EG | ShakirNeural | SalmaNeural | Mahfouz, Hindawi catalog, modern fiction |
| Saudi | ar-SA | HamedNeural | ZariyahNeural | Gulf authors, religious texts (HamedNeural also MSA for non-fiction/academic/Quranic) |
| Levantine | ar-SY | LaithNeural | AmanyNeural | Levantine authors (Gibran, Darwish) |
| Jordanian | ar-JO | TaimNeural | SanaNeural | Jordanian authors |
| Lebanese | ar-LB | RamiNeural | LaylaNeural | Lebanese authors |
| Iraqi | ar-IQ | BasselNeural | RanaNeural | Iraqi authors |
| Maghreb | ar-MA (also TN, DZ) | JamalNeural | MounaNeural | North African authors |

### Gender pairing and taste (listening tests, POC-4b)
- 8 combos (4 gender pairs x 2 providers) on Chapter 1 of Tharthara Fawq al-Nil (70 segments, 10+ min continuous): **FF (female narrator + female dialogue) is the smoothest**; female narrator over male dialogue beats the reverse; same-gender pairings (MM, FF) are most cohesive.
- Voice taste: warm, soft, narrative; rejects loud/dramatic/energetic. Egyptian + MSA preferred, Levantine acceptable, no Gulf. Strong female lean (7 of 10 ElevenLabs picks). Distinguishes "formal/narrative" (narrator) vs "soft/warm" (dialogue). The project converged on a voice *profile* rather than a fixed pair.
- Voice contrast: enough to distinguish, not so much it feels spliced; selected voices have complementary warmth/expressiveness.
- Settled pairings (pairing-tested; full inventory: `docs/logs/final_voices.csv`, 19 voices):

| Provider | Combo | Narrator | Dialogue | Notes |
|---|---|---|---|---|
| Gemini (production) | FF | Sulafat | Leda | Winner (POC-4c); with style direction |
| Google | FF (primary) | Sulafat | Leda | Smoothest, very good narrator |
| Google | MM | Enceladus | Sadaltager | Good narrator, ok dialogue |
| ElevenLabs | FF (primary) | Sara (MSA) | Alice (Egyptian) | Both interesting, good contrast |
| ElevenLabs | MM | Yahya (MSA) | Karim (MSA) | Very good narrator, ok dialogue |
| ElevenLabs | MF | Moncellence (Egyptian) | Alice (Egyptian) | Both good, dialect-matched |

### Emotion / prosody
- **Azure Arabic has zero `mstts:express-as` support** (no styles, no HD voices; English has 30+ styles). Only rate/pitch/volume. Emotion work was blocked on the platform, not on us (PLAN:691-707). Plan if it arrives: tag dialogue segments with emotion from surrounding narrator context (LLM or rule-based), wrap in `<mstts:express-as>`; higher value than multi-voice. Monitor Azure Arabic voice updates, HD availability and `express-as`.
- Subtle Azure-era reinforcements to test: `<prosody rate="+10%">` on dialogue, `<prosody pitch="+5%">` on dialogue, `<break time="300ms"/>` at transitions. Prosody is optional and test-driven: generate plain two-voice first, tune only what sounds flat; no `express-as` for Arabic.
- **Superseded by Gemini (2026-10-05):** `speech_metadata.style` per segment gives real style direction in Arabic (about 14% slower, audibly calmer), so the "emotion blocked on platform" constraint no longer applies to the production provider.

---

## 8. TTS providers, SSML and audio generation

Evidence: [POC-4](../logs/POC4_RESULTS.md).

### Production provider: Gemini 3.8 Flash TTS (decided 2026-10-05)
- Model `gemini-3.8-flash-tts` (GA) via the Interactions API (`POST /v1beta/interactions`). Sulafat narrator + Leda dialogue, style-directed. Pronunciation ~90%+; **beat ElevenLabs** in listening tests at about Google cost.
- Test: tharthara-fawq-al-nil Ch1 (70 segments, 41 coalesced groups, 4 requests <=1,500 chars). Same voice names as the Chirp3-HD FF pair so the only variable vs `google_FF.mp3` is the model. Script: `scripts/generate_gemini_sample.py`.
- Variants: `gemini_FF` (no style) 9:03, 17,298 output tokens, Good; `gemini_FF_styled` 10:17, 19,668 tokens, **best overall**. Style strings: narrator "warm, calm, measured audiobook narration; soft and unhurried"; dialogue "natural, soft conversational delivery; gentle, not dramatic".
- **Native two-speaker mode**: narrator and dialogue go in one request (`speech_config.speakers`, max 2), like Azure SSML; no per-segment stitching and Gemini paces turns itself.
- **Style control works and is the differentiator**; Azure Arabic has no equivalent.
- **Content filter risk**: some literary passages are blocked. One 651-char narrator passage (Mamluks using passers-by for target practice, a bereaved mother screaming) is refused deterministically (3/3, `content_blocked`) although each sentence passes alone, so the filter is contextual. Recovery: halve at group, then sentence boundaries (this passage needed 5 splits and leaves 200ms seams). A single sentence blocked on its own has no Gemini workaround. Violent books (e.g. *Awlad Haretna*) will hit this more. **Fallback: Google Chirp3-HD exposes the same voice names (Sulafat, Leda)**, preserving voice identity. Unknown whether blocked requests are billed.
- Plan for stage 5: chapter-by-chapter generation, per-book output to `05_audio/`, content-block splitting + Chirp3-HD fallback, batch pricing for full-book runs.

### Provider comparison (POC-4a, Ch15 al-liss-wal-kilab: 86 segments, 4,026 chars, dialogue-heavy)
| Provider | Verdict |
|---|---|
| Azure (Syrian Neural Laith+Amany) | Baseline: native SSML, correct Arabic; 6.0MB, 3.4s |
| Google WaveNet (ar-XA-Wavenet-B+A) | Correct pronunciation but flat/robotic; 34.7s |
| Google Chirp3-HD | Much better than WaveNet; 30 Arabic voices (vs 4 WaveNet); natural; low cost |
| OpenAI tts-1-hd (onyx+nova) | NOT VIABLE: all 9 voices (alloy, echo, fable, onyx, nova, shimmer, ash, ballad, coral) are English-primary multilingual; short Arabic segments produce English or gibberish |
| ElevenLabs multilingual_v2 | Best quality of the earlier set; 5.3MB, 156s |
| Gemini 3.8 Flash TTS (POC-4c) | Winner overall, see above |

Azure voice combos tested: M/F Egyptian Shakir+Salma "most robotic"; F/M Syrian Amany+Laith "most natural, best Levantine feel"; F/F Saudi+Lebanese Zariyah+Layla "nice, distinguishable"; M/M Jordanian+Iraqi Taim+Bassel "nice male voices, hard to distinguish".

ElevenLabs: 31 voices tested; default voices (Adam/Sarah) produce gibberish on Arabic, so Arabic voices come from the shared community library. User-approved 10: Sara (MSA F, soft/expressive/warm, top pick), Alice (Egyptian F), Razan (MSA F, academic/formal), Mona (MSA F), Ghizlane (MSA F, smooth/calm), Salma (Levantine F), Suhair (MSA F), Hanafi (Egyptian M, good narrator), Moncellence (Egyptian M), Yahya (MSA M, deep/warm). Recommended pairings: F/F Razan+Sara; F/F Ghizlane+Alice; F/F Mona+Salma; M/F Hanafi+Sara.
Google Chirp3-HD (12 tested) approved: Sadachbia, Puck, Fenrir (M); Laomedeia, Achernar (F) (`ar-XA-Chirp3-HD-*`). Samples live under `output/epub/al-liss-wal-kilab/05_audio/poc4a/`.

### Cross-cutting TTS findings
- **Mishkal diacritization makes pronunciation worse** (conflicts with Azure's internal Arabic model, Dec 2024, 78% error reduction); send plain text.
- **Segment coalescing** (merge consecutive same-type segments) is required for non-SSML providers: 86 segments to 49 groups; 31 of 86 were under 20 chars and cause language-detection failures without SSML language hints.
- Non-SSML providers: per-group generation + context-aware silence insertion + ffmpeg concatenation (silence matches 500/300/200ms). Azure: native `<voice>` tags in one request. Pause variation should be randomized within ranges, not fixed.
- Credentials via `pass` (amr/azure_tts, amr/google_api, amr/elevenlabs_api, amr/openai_api), parsed on the fly, never stored in code or env files. `.env.example` is stale (lists AWS Polly keys); code uses `AZURE_SPEECH_KEY`/`AZURE_SPEECH_REGION`. TTS credentials are needed only for audio generation; everything through SSML runs offline.
- Azure SSML facts: X-SAMPA works on Azure (unlike Polly) but with a simplified phoneme set (relevant only to the abandoned IPA work).

### SSML generation (POC-4, `src/audiobook/ssml/core.py`, 280 lines, 30 tests)
- `build_ssml()` pure function (segments to valid SSML); `VoiceConfig` TypedDict (`book_dialect`, `narrator_voice`, `dialogue_voice`); `make_voice_config(dialect, narrator_gender)` factory covering 7 dialects. Structure `<speak>` > `<voice>` > text. Consecutive same-voice segments coalesce under one `<voice>` tag.
- Context-aware breaks: 500ms narrator to narrator (paragraph), 300ms narrator/dialogue (voice transition), 200ms dialogue to dialogue (rapid exchange). Open item: add slight randomization.
- Input `03_segments/ssml/chapter_*.csv`; output `04_ssml/chapter_*.ssml` + `voice_config.json` + `ssml_summary.csv`. All 12 books converted.
- Non-fiction path: skip dialogue detection, all text in the narrator voice. Fiction path: narrator segments to narrator voice, dialogue to dialogue voice.
- **The Azure 50-tag limit counts 50 distinct voice names, not elements**; two-voice never approaches it and needs no chapter splitting for that reason.
- Voice sampling script plan (`scripts/sample_voices.py`, PLAN:743-749): Round 1 pick the dialect (6 files, same text, 3 dialect pairs ar-EG/ar-SA/ar-SY, male narrates + female dialogue); Round 2 pick direction (2 files, winning dialect, male-narrates vs female-narrates); Round 3 prosody only if needed. 8-10 files, ~30K chars, within free tier. Principle: do not pre-optimize; listen first, then commit to defaults. Lesson: provider and voice choice could not be settled from spec sheets or cost; only side-by-side listening surfaced the real disqualifiers.

### POC-5 provider architecture (PLAN:953-977)
Goal: full book/chapter audio from the segments CSV (stage 3 output), the universal hand-off for all providers; SSML (stage 4) is optional.

| Provider | Input | Voice switch | Pauses | SSML |
|---|---|---|---|---|
| Azure | Segments CSV to inline SSML | Multi-voice in 1 request | `<break>` tags | Full |
| Google Chirp3-HD | Segments CSV to plain text | 1 API call per segment | Silence WAV concat | Limited (no `<break>`, no `<voice>`) |
| ElevenLabs | Segments CSV to plain text | 1 API call per segment | `<break>` within segment + silence WAV concat | `<break>` only (no `<voice>`) |
| Gemini (production) | Segments CSV to plain text + style | Native 2-speaker request | Model-paced; ~200ms seams on split | None (style direction instead) |

Scope: parameterized script (book, chapter range, provider, voice pairing); randomized pause variation; full-book generation (chapters, concat, final MP3); output `output/{format}/{book}/05_audio/{provider}/chapter_*.mp3`. Per-chapter files match the chapter-by-chapter review workflow.

---

## 9. Cost

- Azure free tier: 5M chars/month for 12 months; ~$8-12 per 150-page book at list.
- Prices per 1M chars (POC-4): Google Standard $4; Google WaveNet/Neural2 $16; Google **Chirp3-HD $30**; Azure Neural $16; ElevenLabs Multilingual v2 API $99; ElevenLabs overage Creator $300 / Pro $240 / Scale $180; OpenAI tts-1-hd $30 (not viable).
- Per book, al-liss-wal-kilab (121K chars): Azure $1.93; WaveNet $1.93; Chirp3-HD $3.63; ElevenLabs Creator marginal $6.30 (+$22/mo base); ElevenLabs API $11.98. Ch15 alone: Azure $0.06, WaveNet $0.06, Chirp3-HD $0.12, OpenAI $0.12, ElevenLabs $0.40.
- ElevenLabs plans (1 credit = 1 char): Creator $22/mo (100K chars), Pro $99/mo (500K), Scale $330/mo (2M, best if batched).
- 5 Mahfouz novels (1.69M chars): Chirp3-HD $50.61; ElevenLabs API $167.02 (al-liss 121K $3.63/$11.98; tharthara 146K $4.38/$14.45; zuqaq 383K $11.49/$37.92; bidaya 474K $14.22/$46.93; awlad 563K $16.89/$55.74). ElevenLabs plans for the same: Creator ~$730 (17 months + overage), Pro $396 (4 months), Scale $330 (1 month).
- **Gemini 3.8 Flash TTS (production)**: ~3.6 output tokens per char (measured). Standard through 2026-12-31 ($9/M audio tokens) ~$32/1M chars, al-liss ~$3.90, 5 novels ~$54; Standard from 2027-01-01 ($18/M) ~$64/1M, ~$7.80, ~$109; **Batch from 2027-01-01 ($9/M) ~$32/1M, ~$3.90, ~$54**. Input text tokens ($0.50-1.00/M) negligible. Use batch for full-book runs. Gemini is at Google Chirp3-HD cost and about a third of ElevenLabs.
- Gap correction: Chirp3-HD vs ElevenLabs is ~3x, not the ~20x originally estimated (earlier numbers $1.16 vs $21.74 per book were based on a lower Chirp3 rate and were superseded). Competitor pricing context: Lahajati $9-30/mo.

---

## 10. Architecture and dev principles

### Design principles (PLAN:355-362)
- **POC first:** validate with a ~15-minute proof of concept (happy path + common edges) before building; then design properly, build with tests; never ship the POC. Test with real books, fix, move on.
- **Build incrementally:** small independent modules; each works on its own before integrating. One book end to end first, then generalize.
- **Slice and dice:** perfect each step before the next.
- **Review between chapters:** every stage emits a CSV for human review, chapter by chapter; do not advance until the current chapter's output is verified.
- **Minimize LLM usage:** code-first (state machine + patterns); reach for an LLM only where it demonstrably beats code (originally: name extraction).
- **Dependency hierarchy:** vanilla language, then stdlib, then external only when stdlib cannot do it in <100 lines; external deps must be maintained, lightweight, widely adopted; always use vetted libraries for security-critical code.
- **Lightweight over complex:** fewer moving parts, fewer deps, less config; simple > clever; readable > elegant. Open-source only, no vendor lock-in; every line must have a purpose (no speculative code, no premature abstractions). File-based, no DB, no web UI.
- Archive superseded work instead of deleting it.

### POCs isolated by DATA boundaries, not code imports
Each stage reads the previous stage's file output, never its Python, so any stage can be rewritten without breaking the next. Do not add cross-stage imports. Evidence: [decisions log](../logs/decisions-log.md).

```
data/books/{epub,docx,txt}/book.*
  | ingest
output/{format}/book/01_ingestion/clean_text.txt + paragraphs.csv       <- REVIEW
  | chapters
output/{format}/book/02_chapters/chapter_*.txt + chapters.csv            <- REVIEW
  | dialogue
output/{format}/book/03_segments/segments.csv                            <- REVIEW (book summary)
                              /ssml/chapter_*.csv                        <- machine segments
                              /review/chapter_*.txt                      <- human review text
  | [OPTIONAL] ssml (Azure only: voice selection + SSML templates)
output/{format}/book/04_ssml/chapter_*.ssml + voice_config.json
  | audio generation (multi-provider: Gemini/Google/ElevenLabs/Azure)
output/{format}/book/05_audio/{provider}/chapter_*.mp3
```
Hand-off rules: the stage-3 segments CSV is the universal hand-off; Gemini/Google/ElevenLabs skip stage 4 (plain text per segment); Azure can use stage-4 SSML or build inline from stage 3. Output folders carry numeric phase prefixes so order is self-evident. `output/` is gitignored working state; regenerate freely.

### Repo structure
- Same repo, IPA archived: zero code overlap; the archive preserves history without interference. Active: `src/audiobook/`, `tests/audiobook/`, `data/books/`, `output/`, `docs/`; paused: `archive/` (src core/dialects/integrations/utils, 329 tests, data masterTTS.json, scripts, tools, Flask `app.py`). Details: [repo structure](../wiki/REPO_STRUCTURE.md).
- Plan-era module layout was flat (`ingest.py`, `chapters.py`, `dialogue.py`, `azure_client.py`, `ssml.py` with voice_pool folded in, `review.py`); **current layout is a package per stage** under `src/audiobook/<stage>/core.py` with tests mirroring at `tests/audiobook/<module>/test_core.py` (ingest, chapters, dialogue, ssml; `voice_pool/` and `shared/` are stubs).
- Input folders: `data/books/epub/` (primary), `docx/` (author submissions), `txt/` (internal), `pdf/` (reference only); `output/pdf/` archived.
- Module conventions: `__init__.py` re-exports `from .core import *` and explicitly imports underscore helpers tests need; named constants (`MAX_UNIT_CHARS = 25_000`, `SPEECH_ATTRIBUTION_LEN = 150`); errors carry pipeline context (`IngestionError(ValueError)`); TypedDict return types (`NormStats`, `IngestSummary`, `VoiceConfig`); `logging`, not `print()`.
- Test counts as built: POC-1 21; POC-2 90-91; POC-3 103 (116 in a later count, 242 total with POC-1+2); POC-4 30; full suite 259.

### Architecture decision table
| Decision | Choice | Rationale |
|---|---|---|
| Input formats | EPUB + DOCX first-class, TXT internal | EPUB = content source, DOCX = author format; PDF descoped |
| Language | Python | EPUB/DOCX libs, SDKs, prototypes, Arabic handling |
| Pronunciation | Let the TTS engine handle it (plain text) | IPA letter-by-letter was unusable, validated the hard way |
| Voice per book | Single dialect matched to origin | A book is a book; dialect changes meaning |
| Repo structure | Same repo, IPA archived | Zero code overlap |
| Dialogue detection | Code-first (state machine + patterns) | LLM only if code cannot solve it |
| Review workflow | CSV export, chapter by chapter | Proven in prototypes; manageable scope |
| Character names source | External list (Wikipedia, book info) | Heuristic extraction had 19% false-positive rate (moot after Phase B closed) |
| POC isolation | Data boundaries | Each stage reads file output, not code |
| SSML generation | Templates + voice selection in one module | Two-voice is a 3-field config |
| Voice selection | M/F switch per dialect, not prosody-only | Azure prosody too crude to signal dialogue alone |
| Voice sampling | 8-10 files across 3 dialects, human picks | Listen first, then commit |
| Audio stitching | Per-chapter files, concatenated | Matches review workflow |
| PDF handling | Out of scope | No OSS tool extracts Arabic PDF correctly |

### Process lessons
- When a design is broken, say so and redesign; do not patch over it. Validate with tests/regression/smoke after a correction before reporting. Edits to canonical docs must be additive (no silent omission). Follow the literal scoped ask and do not create unrequested files. Pushing to main is acceptable; do not open a PR per change. Dev workflow and definition of done live in [dev-workflow](../wiki/dev-workflow.md) and [definition-of-done](../wiki/definition-of-done.md).
- Reference index: see [section 18](#18-reference-index).

---

## 11. Content sources and test books

### Free content (PLAN:302-309)
| Resource | What | Format | Size | Access |
|---|---|---|---|---|
| Hindawi Foundation | Arabic literature, philosophy, science | EPUB + PDF | 3,271 books (CC BY 4.0) | hindawi.org |
| Arabic E-Book Corpus (Swedish) | Hindawi books as clean text | Plain text + HTML | 1,745 books, 81.5M words | researchdata.se/en/catalogue/dataset/2024-145 |
| Hindawi HuggingFace | Hindawi content | Various | Subset | huggingface.co/datasets/alielfilali01/Hindawi-Books-dataset |
| Archive.org Arabic | Mixed scanned + digital | PDF, some EPUB | Tens of thousands | archive.org/details/booksbylanguage_arabic |

Sourcing lesson: Archive.org Arabic PDFs were scanned images with no text layer and were discarded; the Hindawi Foundation (legally free, born-digital) was adopted and extraction verified before committing books to the corpus. Hindawi EPUB download needs User-Agent + Referer headers (403 otherwise).

### Tooling
hindawi-dl (github.com/shahwan42/hindawi-dl; bulk download; broken on Python 3.14, use direct download); python-docx; ebooklib + BeautifulSoup; Calibre `ebook-convert` (EPUB/DOCX direction only). OCR note from PDF research: PaddleOCR v5 best free; Mistral OCR best paid (94.9%).

### The 12 test books
EPUB (5 Hindawi born-digital, all Naguib Mahfouz, clean): al-liss-wal-kilab 781 paras / 125K chars; awlad-haretna 4,299 / 563K; bidaya-wa-nihaya 2,273 / 474K; tharthara-fawq-al-nil-hindawi 1,496 / 146K; zuqaq-al-midaqq 1,412 / 383K. (Later cost work uses 121K for al-liss, a measured post-processing figure.)

DOCX (4, Internet Archive/Shamela, with `(n/m)` page markers): al-tamheed-fi-tajweed (Quranic recitation) 195 / 122K; jawahir-al-adab (Arabic rhetoric) 2,108 / 773K; mabahith-ulum-alquran (Quranic sciences) 1,056 / 564K; mawsuat-al-ijaz-al-ilmi (scientific encyclopedia) 1,190 / 748K.

TXT (3, Hindawi via HuggingFace, clean): رحلة-ابن-فطومة (Mahfouz) 856 / 125K; صدى-النسيان (Mahfouz) 425 / 81K; يوميات-نائب-في-الأرياف (Tawfiq al-Hakim) 651 / 147K.

PDF: archived in `data/books/pdf/` and `output/pdf/`, not processed. All 12 books ingested clean.

---

## 12. Go-to-market and risks

### Go-to-market (hybrid: content-first, manual service, self-serve tool)
- **Phase 1 (months 1-3):** 20-30 public-domain audiobooks from the Hindawi CC catalog; publish on YouTube and Spotify/Anghami; build portfolio and audience; refine the pipeline end to end.
- **Phase 2 (months 3-5):** manual conversion service for young Arab authors at $20-40/book via Arabic social media; success metric 5+ paying customers.
- **Phase 3 (months 5-8):** if demand validates, self-serve web tool at $15-25/book.
- Target audience in priority: (1) young Arab authors and small publishers who cannot afford $1,000+ human narration and write in DOCX; (2) content consumers, reached through published content; (3) institutions, later.
- Channels: YouTube (highest Arabic audiobook search volume, evergreen); Spotify / Apple Podcasts (podcast format); Anghami (70M users, Arabic-native); Audible (accepts AI narration via "Virtual Voice"); Arabookverse (Arabic distributor, 300+ platforms). Details: [market research](../wiki/MARKET_RESEARCH.md), [distribution](../wiki/AUDIOBOOK_DISTRIBUTION.md).

### Risk register (as recorded in the plan)
Resolved/closed:
| Risk | L / I | Mitigation | Status |
|---|---|---|---|
| EPUB paragraph boundaries inconsistent across publishers | Med / High | Test on 5+ books from different sources | Resolved: tested on 12 books |
| Chapter detection fails on unusual structures | Med / Med | Manual markers or size-based splitting | Resolved: size fallback works |
| Quotation conventions vary wildly | High / Med | Build normalizer, test on 3+ books | Resolved: guillemets kept as narrator |
| Multi-voice review too painful to scale | High / Med | (accept as cost) | Closed: Phase B skipped |

Open:
| Risk | L / I | Mitigation | Status |
|---|---|---|---|
| Two-voice does not sound good enough | Low / High | Prototypes showed switching works | Validated by POC-4 listening tests (FF pairing, Gemini styled) |
| Azure Arabic has no emotion/style support | High / Med | Wait for Azure; prosody knobs only | Mitigated by choosing Gemini (style direction) |
| Voice pair sounds wrong for a dialect | Med / Low | Sampling tests 3 dialects first | Largely resolved by POC-4 sampling |
| Azure free tier runs out during testing | Low / Low | Monitor usage, ~$8-12/book | Open; reduced relevance after Gemini |
| Competitor (Lahajati) builds same pipeline | Med / High | Ship fast, build content moat with published audiobooks | Open |
| AI narration quality insufficient for fiction | Med / Med | Two-voice masks artifacts; prosody tuning | Largely validated by POC-4; Gemini ~90%+ pronunciation |
| (new) Gemini content filter blocks violent passages | Med / Med | Split and retry, Chirp3-HD fallback (same voice names) | Open; see [section 8](#8-tts-providers-ssml-and-audio-generation) |
| (new) Proper-noun pronunciation | High / Med | Per-book pronunciation dictionary (future) | Open ([section 13](#13-best-practices-alignment)) |

---

## 13. Best-practices alignment

Research: [audiobook best practices](../wiki/audiobook_best_practices.md).

Met:
| Practice | Standard | Sawt |
|---|---|---|
| Pause variation | Vary breaks to avoid the metronome effect (#1 TTS complaint) | Context-aware breaks 500/300/200ms; TODO slight randomization |
| Said tags with narrator | "He said" stays with narrator | Colon split puts attribution before the colon as narrator |
| Dialect matching | Match voice to author's region (Storytel/Kitab Sawti standard) | Per-book dialect config; Egyptian for Mahfouz, Levantine available |
| Two-voice model | MSA narration + dialect dialogue is how Egyptian fiction is produced | Core architecture |
| Same-gender pairings smoothest | Less jarring than M/F | FF confirmed primary |
| Voice contrast | Distinguishable, not spliced | Tested 8 pairings; complementary warmth/expressiveness |
| Guillemets as narrator | One voice for cohesion | Deliberate decision |
| Long-form testing | 10+ min continuous, not spot checks | Full chapter 1 (70 segments) for all 8 pairings |
| Fiction vs non-fiction | Expressive two-voice vs single authoritative voice | Genre flag in pipeline design |

Open gaps: proper-noun pronunciation (#1 Arabic TTS failure point since print has no diacritics; future per-book pronunciation dictionary via SSML `<phoneme>`; note this is a targeted dictionary, not a return to letter-by-letter IPA); prosody monotony (future `<prosody>` rate/pitch variation between narrative segments; Gemini style direction is the new lever).

---

## 14. Tried and abandoned

| Idea | Outcome | Lesson | Evidence |
|---|---|---|---|
| **IPA / phoneme pipeline** (Arabic text, diacritization, syllabification, gemination, sun letters, allophones, emphatic spread, IPA, X-SAMPA, SSML phoneme tags, TTS; Polly-based, 329 tests, 5 dialects) | Letter-by-letter output was robotic and unintelligible; audio judged unusable | Assumption that phoneme control would improve quality was never validated early; complex processing, unusable output. Validate with listening early. Archived in `archive/` (~360-file restructure Feb 2026), shares zero code (LSP confirms 0 imports) | [insights](../logs/insights.md), CLAUDE.md |
| PDF ingestion (PyMuPDF, pdfplumber) | Fused words | Source-data problem; see [section 4](#4-input-formats-and-the-pdf-decision) | [POC-1](../logs/POC1_RESULTS.md) |
| Guillemets as dialogue markers (prototype 01, then promoted above colons, then guillemet splitter) | Reversed twice, then deleted | Misclassifies scare quotes; degrades corpus; verify heuristics against the whole corpus | [POC-3](../logs/POC3_RESULTS.md) |
| Continuation heuristic (plain paragraphs stay dialogue until >200 chars and no speech verb) | Deleted | Zero genuine cases in 5 novels, only false positives | [POC-3](../logs/POC3_RESULTS.md) |
| Review markers `«»` | Replaced by `// \\` | Collided with source guillemets | [POC-3](../logs/POC3_RESULTS.md) |
| Porting the 330-line prototype detector | Rewritten smaller | NFKC removed the need for its workarounds | [insights](../logs/insights.md) |
| Multi-voice per-character / character attribution | CLOSED | See [section 7](#7-voice-and-dialect-strategy); 63.5% automated attribution, 36.5% manual | [decisions log](../logs/decisions-log.md) |
| Heuristic character-name extraction | 19% false positives; replaced in prototypes by external name list, then moot | | [insights](../logs/insights.md) |
| Prosody-only dialogue contrast on Azure | Too crude (3 dials) | Voice switch needed | [POC-4](../logs/POC4_RESULTS.md) |
| Mishkal diacritization | Made Azure pronunciation worse | Plain text | [POC-4](../logs/POC4_RESULTS.md) |
| OpenAI TTS | No Arabic voices | Not viable | [POC-4](../logs/POC4_RESULTS.md) |
| Azure as production TTS | Robotic Egyptian voices, no `express-as` for Arabic | Superseded by Gemini 2026-10-05 | [POC-4](../logs/POC4_RESULTS.md) |
| ElevenLabs as quality pick | Beaten by Gemini at ~1/3 cost; plan choice moot | Reserved at most for premium work | [POC-4](../logs/POC4_RESULTS.md) |
| Genre-detection feature | Not built | Document "fiction only; contact us" instead | PLAN |
| Splitting on EPUB spine | Unreliable | Text regex primary | [POC-2](../logs/POC2_RESULTS.md) |
| Splitting on page markers / paragraph length as header signal | Noise / dialogue is short | Filter markers; do not use length | [POC-2](../logs/POC2_RESULTS.md) |
| Archive.org scanned-PDF corpus | No text layer | Verify extractability before adopting a source | [insights](../logs/insights.md) |
| Calibre PDF to EPUB | Reversed text | Do not use | [PDF research](../logs/ARABIC_PDF_EXTRACTION.md) |

---

## 15. Success criteria as met

- **POC-1 (production ready):** clean extraction from EPUB, DOCX, TXT; paragraph boundaries human-verified; 12 books (5 EPUB, 4 DOCX, 3 TXT); 21 tests; PDF descoped and removed.
- **POC-2 (production ready):** delimiters detected across 3+ books respecting each book's own hierarchy; all units under ~25K chars, sub-split at paragraph boundaries; no mid-sentence splits; units concatenate to original; 91 tests; validated on all 12 books.
- **POC-3 Phase A (production ready):** dialogue detection on all 12 books, 103 tests passing; ~95% accuracy; 3 markers (colon, em dash, trailing colon); no continuation heuristic; guillemets stay narrator; short story titles stay inside chapters; dual output with sync workflow; per-chapter and book-level summary CSVs.
- **POC-3 Phase B (CLOSED):** skipped (only 2 voices per dialect; 36.5% manual review not justified; rapid switching robotic; listeners prefer a single narrator with tonal shifts; emotion/prosody deferred until a platform supports Arabic styles).
- **POC-4 (done):** valid SSML accepted by Azure; all 12 books converted; 30 tests; `ssml/core.py` 280 lines; dialect-matched pairs with 500/300/200ms breaks; voice coalescing. POC-4a provider comparison (OpenAI not viable; Google Chirp3-HD 30 voices; ElevenLabs best of that set; Mishkal worsens). POC-4b pairing tests (8 combos): FF smoothest. POC-4c Gemini winner. (Original numbers "$1.16/book Chirp3, $21.74/book ElevenLabs, 20x" are superseded by [section 9](#9-cost).)
- **POC-5 (next):** see [section 8](#8-tts-providers-ssml-and-audio-generation).

---

## 16. Superseded views

One-liners so the history is not lost:
- Earlier plan assumed Azure as the production TTS; superseded by Gemini 3.8 Flash TTS (2026-10-05). Azure remains the baseline and SSML target.
- "Emotion is blocked on the platform" is true of Azure Arabic only; Gemini style direction removes the block.
- "Google Chirp3-HD is the preferred low-cost provider (~20x cheaper than ElevenLabs)" is superseded: gap is ~3x, and Gemini beats both on quality.
- Plan listed `--fiction`/`--non-fiction` flags; later `--genre`.
- Original vision/KB text described "PDF/TXT via Azure Neural TTS" and "none started"; current inputs are EPUB/DOCX/TXT and POC-1..4 are done.
- Prototype-era detector rules (colons override guillemets, guillemet fallback, continuation heuristic with >200-char threshold, 5-marker priority including guillemets) are superseded by the 3-marker final priority.
- Earlier dialogue-ratio numbers (al-liss 44.4%, etc.) are superseded by the table in [section 6](#6-dialogue-detection).
- Plan-era flat module names (`ingest.py`, `ssml.py`, `review.py`, `audio_gen.py`, `azure_client.py`) are superseded by per-stage packages.
- Old doc paths (`docs/02-features/azure-audiobooks/...`, `docs/logs/03-logs/...`) have moved to `docs/product/`, `docs/wiki/`, `docs/logs/`.
- Gulf voices for religious texts (Saudi HamedNeural) were a plan-era suggestion; user taste later ruled out Gulf voices for fiction.

---

## 17. Runner + UI build (2026-10-05)

### Process: spec before build
- Spec first through the AGENT_RULES Operating Flow (interview rounds, explicit owner sign-off), then build. A UI built without approval was deleted. Opus orchestrates and reviews; Sonnet agents write the code.

### Testing
- Server/API tests passed while the page itself was broken. A real-browser check found defects across four fix rounds after the first build. That is why a page-level test now exists: a Node fake-DOM harness in `tests/audiobook/ui/test_core.py` that runs the real page JS (e.g. `TestStartButtonSync`).

### Arabic display
- Arabic paths need LTR direction with segments that break only at `/`.
- Arabic names embedded in LTR messages need bidi isolation (`<bdi>` / `unicode-bidi: isolate`), or the sentence reorders around them.

### Runner design
- The go/no-go passed: a forced step-3 failure, then retry, left steps 1-2 output byte-identical (the retry resumes from disk).
- `ingest()` hard-coded its output location (`output/{format}/{book}/`). It got an optional `ingestion_dir` argument so the runner can write to `<book dir>/<name>_sawt/01_ingestion`; this was the one stage change.

### Shared state and tests
- `jobs.json` has more than one writer (a UI run, a CLI run, the owner deleting a job). Whole-file overwrite lost runs and resurrected deleted jobs; the fix is a locked read-merge-write keyed on stable job and run ids, never a snapshot of the file taken at run start. Date-sorting merged runs is still by local-time ISO strings (a clock step back can misorder them).
- Tests must never touch the real history: `tests/conftest.py` sets a session-wide `SAWT_HOME` and asserts the real `jobs.json` is unchanged at session end; the UI client fixture drains the worker before shutdown.
- A path stored unresolved is a path matched wrongly: store and compare book sources resolved, or a symlinked spelling creates a phantom "name already taken".
- Bundle the font instead of loading it from the network: it lets the CSP drop external hosts (`font-src 'self'`) and the page works offline.

### Look
- Bareloop style (DESIGN_PLAN.md); light-theme colours contrast-tuned to the AA checklist in DESIGN_PLAN.md.

---

## 18. Reference index

Internal (paths as in the original plan; some now relocated):
- Market research [wiki/MARKET_RESEARCH.md](../wiki/MARKET_RESEARCH.md); PDF research [logs/ARABIC_PDF_EXTRACTION.md](../logs/ARABIC_PDF_EXTRACTION.md); production detector prototype `reference/prototypes/06_simplified_detector.py`; `reference/character_voice_assignment.py`; `reference/azure_integration.py`; prototype outputs `SIMPLIFIED_DETECTION_FINAL_STATUS.md`, `SCALABILITY_ANALYSIS.md`, `BUG_FIX_TEXT_LOSS_RESOLVED.md`, `QUOTATION_ATTRIBUTION_RESEARCH_FINDINGS.md`; `arabic_voices_capabilities.json`.
- POC results: [POC-1](../logs/POC1_RESULTS.md), [POC-2](../logs/POC2_RESULTS.md), [POC-3](../logs/POC3_RESULTS.md), [POC-4](../logs/POC4_RESULTS.md).
- Process/other: [implementation log](../logs/implementation-log.md), [decisions log](../logs/decisions-log.md), [bug log](../logs/bug-log.md), [validation log](../logs/validation-log.md), [insights](../logs/insights.md), [dev workflow](../wiki/dev-workflow.md), [definition of done](../wiki/definition-of-done.md), [pipeline guide](../wiki/pipeline-guide.md), [audiobook best practices](../wiki/audiobook_best_practices.md), [prd](prd.md), [REPO_STRUCTURE](../wiki/REPO_STRUCTURE.md), [AUDIOBOOK_DISTRIBUTION](../wiki/AUDIOBOOK_DISTRIBUTION.md).
- Vision one-liner: two-voice Arabic audiobooks; text processing is the product. Brand: Sawt (صوت), "voice"; tagline كل كتاب له صوت ("every book has a voice").

External: Hindawi (hindawi.org, 3,271 books, CC BY 4.0); Swedish text corpus (researchdata.se/en/catalogue/dataset/2024-145, 1,745 books); hindawi-dl (github.com/shahwan42/hindawi-dl); HuggingFace Hindawi-Books-dataset; Azure pricing (azure.microsoft.com/pricing/details/cognitive-services/speech-services); Google TTS pricing (cloud.google.com/text-to-speech/pricing); ElevenLabs pricing (elevenlabs.io/pricing).
