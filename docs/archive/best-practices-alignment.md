---
title: Best Practices Alignment
theme: best-practices-alignment
sources:
  - docs/archive/PLAN.md
description: How Sawt meets audiobook industry best practices, plus reference links.
---

# Best Practices Alignment

Research behind this page lives in `docs/wiki/audiobook_best_practices.md` (docs/archive/PLAN.md:981-983).

## Status legend

Done items are marked met; items marked as future are not yet built (docs/archive/PLAN.md:985-997).

## Practices Sawt meets

| Best practice | Industry standard | Sawt status |
|---|---|---|
| Pause variation | Vary breaks to avoid the metronome effect (#1 TTS complaint) | Met: context-aware breaks (500/300/200ms by transition type). TODO: add slight randomization |
| Said tags with narrator | "He said" stays with the narrator voice, not dialogue | Met: colon-split puts attribution before the colon as narrator, quoted speech as dialogue |
| Dialect matching | Match voice to the author's region (Storytel/Kitab Sawti standard) | Met: per-book dialect config, Egyptian for Mahfouz, Levantine voices available |
| Two-voice model | MSA narration + dialect dialogue is how Egyptian fiction is produced | Met: core architecture, narrator voice + dialogue voice |
| Same-gender pairings smoothest | Less jarring transitions than M/F switching | Met: FF confirmed as primary pairing in listening tests |
| Voice contrast | Enough to distinguish, not so much it feels spliced | Met: tested 8 pairings, selected voices with complementary warmth/expressiveness |
| Guillemets as narrator | Inner thoughts + speech by the same person = one voice for cohesion | Met: deliberate design decision, avoids jarring micro voice-switches |
| Long-form testing | Test 10+ min continuously, not spot checks | Met: full chapter 1 (70 segments) generated for all 8 pairings |
| Fiction vs non-fiction | Fiction = expressive two-voice; non-fiction = single authoritative voice | Met: genre flag in pipeline design, non-fiction skips dialogue detection |

(docs/archive/PLAN.md:985-997)

## Open gaps (future work)

| Best practice | Industry standard | Planned work |
|---|---|---|
| Proper noun pronunciation | #1 Arabic TTS failure point (no diacritics in print) | Future: per-book pronunciation dictionary via SSML `<phoneme>` |
| Prosody monotony | Vary rhythm to avoid auditory fatigue | Future: `<prosody>` rate/pitch variation between narrative segments |

(docs/archive/PLAN.md:995-996)

## References

### Internal documents

| Resource | Location |
|---|---|
| Market research | `docs/02-features/azure-audiobooks/research/MARKET_RESEARCH.md` |
| PDF extraction research | `docs/02-features/azure-audiobooks/research/ARABIC_PDF_EXTRACTION.md` |
| Production detector | `docs/02-features/azure-audiobooks/reference/prototypes/06_simplified_detector.py` |
| Voice assignment | `docs/02-features/azure-audiobooks/reference/character_voice_assignment.py` |
| Azure integration | `docs/02-features/azure-audiobooks/reference/azure_integration.py` |
| Detection findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SIMPLIFIED_DETECTION_FINAL_STATUS.md` |
| Scalability analysis | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/SCALABILITY_ANALYSIS.md` |
| Bug fix history | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/BUG_FIX_TEXT_LOSS_RESOLVED.md` |
| Research findings | `docs/02-features/azure-audiobooks/reference/prototypes/outputs/QUOTATION_ATTRIBUTION_RESEARCH_FINDINGS.md` |
| Azure voice capabilities | `docs/02-features/azure-audiobooks/reference/arabic_voices_capabilities.json` |

(docs/archive/PLAN.md:1001-1011, docs/archive/PLAN.md:1016-1016)

### POC results

| Resource | Location |
|---|---|
| POC-1 results | `docs/logs/03-logs/POC1_RESULTS.md` |
| POC-2 results | `docs/logs/03-logs/POC2_RESULTS.md` |
| POC-3 results | `docs/logs/03-logs/POC3_RESULTS.md` |
| POC-4 results | `docs/logs/03-logs/POC4_RESULTS.md` |

(docs/archive/PLAN.md:1012-1015)

### External resources

- Hindawi CC corpus: [hindawi.org](https://www.hindawi.org/), 3,271 books, CC BY 4.0 (docs/archive/PLAN.md:1017-1017)
- Swedish text corpus: [researchdata.se](https://researchdata.se/en/catalogue/dataset/2024-145), 1,745 books, plain text (docs/archive/PLAN.md:1018-1018)
- hindawi-dl: [github.com/shahwan42/hindawi-dl](https://github.com/shahwan42/hindawi-dl), bulk downloader (docs/archive/PLAN.md:1019-1019)
