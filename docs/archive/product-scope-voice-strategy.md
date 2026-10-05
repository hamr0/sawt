---
title: Product Scope and Voice Strategy
theme: product-scope-voice-strategy
sources:
  - docs/archive/PLAN.md
description: Fiction-only scope, single/two/multi-voice reasoning, dialect matching, why text processing is the product, and the IPA-pipeline lesson.
---

# Product Scope and Voice Strategy

## Lesson learned: why the IPA pipeline does not apply

The repo originally built a full IPA phonological pipeline: Arabic text, diacritization, syllabification, gemination, sun letters, allophones, emphatic spread, IPA, X-SAMPA, SSML phoneme tags, TTS engine. (`docs/archive/PLAN.md:14-16`)

It did not work for audiobooks. Letter-by-letter processing through SSML phoneme tags produced output that was too robotic and unintelligible. The assumption that phoneme-level control would improve quality was never validated early enough: the processing was complex, but the output was unusable. (`docs/archive/PLAN.md:18-21`)

The audiobook pipeline takes a different approach (`docs/archive/PLAN.md:23-27`):
- Send plain Arabic text to Azure neural voices and let Azure handle pronunciation.
- Our job is text structure: chapters, paragraphs, dialogue boundaries, character voices.
- We do not touch pronunciation; Azure's neural models do it better than phoneme-by-phoneme control.
- The IPA pipeline (329 tests, 5 dialects) is archived as a learning artifact.

The two pipelines share zero code; LSP confirms 0 imports connect them. The IPA work lives in `archive/` for reference. (`docs/archive/PLAN.md:29-30`)

## Product scope: fiction only

Decision (Feb 2026): Sawt is optimized for fiction (novels, short stories) with dialogue. (`docs/archive/PLAN.md:99`)

### Why fiction only

Testing on non-fiction showed the dialogue detector creates false positives (`docs/archive/PLAN.md:103-107`):
- Quranic verses in `{}` are citations, not dialogue.
- Scientific quotations: "قال العلماء:" triggers colon detection, but it is indirect speech.
- Scholarly citations: references to historical figures are not dramatic dialogue.
- Example: `mawsuat-al-ijaz-al-ilmi` (smoking health encyclopedia) marked citations as dialogue throughout.

Non-fiction (academic, religious, encyclopedias) works better as single-voice narration. The pipeline is designed for fiction's dramatic dialogue, not scholarly references. (`docs/archive/PLAN.md:109`)

### Positioning

| Content type | Sawt approach | Why |
|---|---|---|
| Fiction | 2+ voices (narrator + dialogue) | Dramatic exchanges, clear speaker turns, voice switching adds life |
| Non-fiction | Single voice (skip POC-3) | Citations are not "performed" dialogue; needs authoritative consistency |
| Special cases | Manual quote (contact us) | Quranic recitation with tajweed, custom multi-voice academic content |

(`docs/archive/PLAN.md:113-117`)

Documentation wording: "Sawt produces multi-voice audiobooks for Arabic fiction. For non-fiction, academic texts, or custom projects, contact us." (`docs/archive/PLAN.md:119`)

### Fiction/non-fiction flag (future)

A future pipeline wrapper script takes a `--genre` flag. Fiction (default) runs all 3 POCs; non-fiction skips POC-3 and goes straight to single-voice SSML. (`docs/archive/PLAN.md:123-130`)

```bash
python pipeline.py --book path/to/novel.epub --genre fiction
python pipeline.py --book path/to/textbook.epub --genre non-fiction
```

For now, process fiction only. Non-fiction support is deferred until demand validates it. (`docs/archive/PLAN.md:132`)

## Voice approach

### Single voice (non-fiction use case)

- One voice reads everything, with no text processing beyond chapter splitting (POC-1, POC-2, SSML).
- Use case: non-fiction where citations/quotes are references, not dialogue.
- Not a core product; deferred until validated.

(`docs/archive/PLAN.md:138-142`)

### Two voice (narrator + dialogue): primary goal for fiction

- Narrator voice for narration, a different voice for all dialogue. (`docs/archive/PLAN.md:145`)
- Voice switching creates a "listener attention reset" that masks TTS pronunciation artifacts. (`docs/archive/PLAN.md:146`)
- Only binary classification is needed: narration or dialogue. No character attribution; just detect that someone is speaking. (`docs/archive/PLAN.md:147-149`)
- Existing colon-based detection achieves 100% dialogue detection rate on fiction. (`docs/archive/PLAN.md:148`)
- Manual review effort: 5-15 min per book to verify narration/dialogue boundaries. (`docs/archive/PLAN.md:150`)
- Use case: fiction, stories, novels with dialogue. This is the goal, good enough for 70-80% of fiction books. (`docs/archive/PLAN.md:151-152`)

### Multi voice (per-character): closed (Feb 2026)

Decision: skip. Not justified by current Azure Arabic capabilities or listener value. (`docs/archive/PLAN.md:155`)

Reasons (`docs/archive/PLAN.md:156-161`):
- Azure Arabic has only 2 voices per dialect (1M, 1F), not enough to distinguish characters C through Z.
- Character attribution was 63.5% automated in prototypes; the remaining 36.5% needs manual review per book.
- Unnamed characters (the officer, the neighbor, the mayor) need catch-all assignment for marginal gain.
- Heavy dialogue exchanges (10-line em-dash conversations) create rapid voice-switching that sounds robotic in TTS.
- Research consensus: most listeners prefer a single skilled narrator with tonal shifts over full-cast; multi-voice is the exception (drama adaptations, big-budget productions), not the norm.
- Two-voice captures 90% of the listening value with 10% of the complexity.

Revisit if Azure adds more Arabic voices plus emotion styles; the Phase A segment CSVs are the right foundation. (`docs/archive/PLAN.md:162`)

### Emotion/prosody enhancement: deferred

- Azure Arabic voices have zero `mstts:express-as` support (no emotion styles); there are no HD voices for Arabic either. (`docs/archive/PLAN.md:165,167`)
- English has 30+ styles (angry, cheerful, sad, whispering); Arabic has none. (`docs/archive/PLAN.md:166`)
- When Azure adds support, the investment is thin: tag dialogue segments with emotion context and apply `mstts:express-as`; Phase A segment CSVs are ready. (`docs/archive/PLAN.md:168`)
- This is a platform capability gap, not a pipeline task today. Monitor Azure updates. (`docs/archive/PLAN.md:169`)

### What we can do now: prosody tuning (POC-4)

- `<prosody rate="+10%">` on dialogue: slightly faster pace signals conversation vs. measured narration.
- `<prosody pitch="+5%">` on dialogue: subtle lift separates dialogue from narrator.
- `<break time="300ms"/>` at narrator/dialogue transitions: an audible pause signals the voice switch.
- These are subtle reinforcements on top of the two-voice switch, not character distinction. A few test renders in POC-4 SSML generation will calibrate values.

(`docs/archive/PLAN.md:172-176`)

## Dialect-matched voice selection

Principle: the text is the dialect; do not change either, match them. (`docs/archive/PLAN.md:180`)

A Mahfouz novel uses Egyptian literary Arabic with Egyptian colloquial in dialogue. Reading it with a Gulf voice is like dubbing a British film in a Texas accent: technically intelligible, culturally wrong. The voice dialect must match the book's linguistic origin. (`docs/archive/PLAN.md:182-184`)

Matching rules (`docs/archive/PLAN.md:187-191`):
- Author's nationality/dialect is the primary signal (Mahfouz: Egyptian, Gibran: Levantine).
- Book's setting is secondary (a novel set in Baghdad gets Iraqi voices even if the author is Egyptian).
- Publisher origin is tertiary (Hindawi catalog: Egyptian by default).
- All voices in a book share the same dialect: narrator, dialogue, all characters.
- Never mix dialects within a book (no Gulf narrator with Egyptian dialogue characters).

### Azure Arabic voice inventory (14+ neural voices, 7 dialects)

| Dialect | Code | Voices | Best for |
|---|---|---|---|
| Egyptian | ar-EG | ShakirNeural, SalmaNeural | Mahfouz, Hindawi catalog, most modern fiction |
| Saudi | ar-SA | HamedNeural, ZariyahNeural | Gulf authors, religious texts |
| Levantine | ar-SY, ar-JO, ar-LB | Multiple | Levantine authors (Gibran, Darwish) |
| Maghreb | ar-MA, ar-TN, ar-DZ | Multiple | North African authors |
| Iraqi | ar-IQ | Multiple | Iraqi authors |
| MSA | ar-SA (formal) | HamedNeural | Non-fiction, academic, Quranic |

(`docs/archive/PLAN.md:193-202`)

For the Hindawi catalog (Phase 1: 20-30 books), all books are Egyptian and use `ar-EG-*` voices. (`docs/archive/PLAN.md:204`)

Per-book voice config (in the character registry), set once per book and applied to all pipeline stages (`docs/archive/PLAN.md:206-213`):

```
book_dialect: ar-EG
narrator_voice: ar-EG-ShakirNeural
dialogue_default_voice: ar-EG-SalmaNeural
```

## Why text processing is the product

The pipeline difficulty distribution (`docs/archive/PLAN.md:219-229`):

| Stage | Status |
|---|---|
| Text extraction and cleaning | Done (POC-1) |
| Chapter detection and splitting | Done (POC-2) |
| Narration vs dialogue detection | Done (POC-3, ~95% accuracy) |
| Character attribution | Closed, not justified (see Phase B) |
| SSML + voice selection | Next (POC-4) |
| Azure TTS API | Easy, an API call |
| Audio stitching | Easy, concatenation |

Once text is correctly broken into parts, SSML is just wrapping segments in voice tags. Text processing is the product; everything after it is commodity. (`docs/archive/PLAN.md:231-232`)

### Competitive moat

Nobody else has built a raw-book-to-audiobook pipeline for Arabic. Competitors are either TTS engines (sell the voice, user handles everything) or audiobook platforms (distribute, do not produce). The text processing pipeline bridges the gap. Full competitive analysis is in `docs/product/MARKET_RESEARCH.md`. (`docs/archive/PLAN.md:235-239`)
