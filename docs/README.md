# Documentation

Arabic Audiobook Production — documentation hub.

## Quick Links

| What | Where |
|------|-------|
| Product requirements (source of truth) | [PRD](product/prd.md) |
| Learnings | [learnings.md](product/learnings.md) |
| Repo structure & data flow | [REPO_STRUCTURE.md](wiki/REPO_STRUCTURE.md) |
| Development workflow | [Dev Workflow](wiki/dev-workflow.md) |
| Definition of done | [DoD](wiki/definition-of-done.md) |

---

## Structure

```
docs/
├── product/                           # WHAT it must do
│   ├── prd.md                         #   Product requirements (single source of truth)
│   └── learnings.md                   #   Lessons, decisions, risks from POCs and research
├── wiki/                              # HOW to work + reference
│   ├── dev-workflow.md, definition-of-done.md, pipeline-guide.md
│   ├── audiobook_best_practices.md
│   └── REPO_STRUCTURE.md, MARKET_RESEARCH.md, AUDIOBOOK_DISTRIBUTION.md
├── logs/                              # MEMORY (what changed)
│   ├── POC{1,2,3,4}_RESULTS.md
│   ├── implementation-log.md, decisions-log.md, bug-log.md, validation-log.md, insights.md
│   └── final_voices.csv, ARABIC_PDF_EXTRACTION.md, VOICE_SELECTION_EMAIL.md
└── archive/                           # Superseded docs (reference only)
```

---

## product/ — Requirements and learnings

| Document | Description |
|----------|-------------|
| [prd.md](product/prd.md) | Product requirements, scope, next build (single source of truth) |
| [learnings.md](product/learnings.md) | Lessons, decisions, risks from POCs and research |

## logs/ — Project Memory

| Document | Description |
|----------|-------------|
| [POC1_RESULTS.md](logs/POC1_RESULTS.md) | POC-1 results: book ingestion (PRODUCTION READY) |
| [POC2_RESULTS.md](logs/POC2_RESULTS.md) | POC-2 results: chapter splitting (PRODUCTION READY) |
| [POC3_RESULTS.md](logs/POC3_RESULTS.md) | POC-3 results: dialogue detection (PRODUCTION READY) |
| [POC4_RESULTS.md](logs/POC4_RESULTS.md) | POC-4 results: SSML and provider listening tests |
| [implementation-log.md](logs/implementation-log.md) | What was built, when |
| [decisions-log.md](logs/decisions-log.md) | Architecture decisions with rationale |
| [bug-log.md](logs/bug-log.md) | Bugs, root causes, fixes |
| [validation-log.md](logs/validation-log.md) | CSV review results per POC |
| [insights.md](logs/insights.md) | Learnings from prototypes and development |

## wiki/ — Workflow and reference

| Document | Description |
|----------|-------------|
| [dev-workflow.md](wiki/dev-workflow.md) | POC development cycle, commands, review gates |
| [definition-of-done.md](wiki/definition-of-done.md) | Completion criteria per POC |
| [REPO_STRUCTURE.md](wiki/REPO_STRUCTURE.md) | Directory layout, data flow between POCs |

---

## Audiobook Best Practices Compliance

Based on research from professional narrators, ACX/Audible standards, and Storytel/Kitab Sawti production practices. Full research: [audiobook_best_practices.md](wiki/audiobook_best_practices.md)

### Met

| Practice | What the industry does | How Sawt does it |
|----------|----------------------|------------------|
| **Said tags with narrator** | "He said/she said" always stays with narrator voice — only quoted speech switches | Colon-split detection puts attribution as narrator, speech after colon as dialogue |
| **Dialect matching** | Voice dialect matches author's region (Storytel standard: Egyptian author → Egyptian voices) | Per-book dialect config. Egyptian for Mahfouz, Levantine/Gulf/Maghreb voices available |
| **Two-voice narrator/dialogue** | MSA narration + dialect dialogue is how modern Egyptian fiction audiobooks are produced | Core architecture — narrator voice for narration, separate voice for all dialogue |
| **Same-gender pairings** | Same-gender voice pairs produce smoother transitions than M/F switching | FF confirmed as primary pairing in 8-combo listening tests |
| **Voice contrast balance** | Voices should differ enough to tell apart, not so much it feels like two audiobooks spliced | 83 voices sampled → 19 shortlisted → 8 pairings tested → 5 production pairs selected |
| **Context-aware pauses** | Different pause lengths for different transitions (voice switch vs paragraph vs rapid exchange) | 500ms narrator→narrator, 300ms narrator↔dialogue, 200ms dialogue→dialogue |
| **Guillemet coherence** | Inner thoughts + outer speech by same person = one voice to avoid fragmenting narration | Guillemets `«»` deliberately kept as narrator — no jarring micro voice-switches |
| **Fiction vs non-fiction** | Fiction needs expressive two-voice; non-fiction needs single authoritative voice | Genre flag: fiction runs full pipeline, non-fiction skips dialogue detection |
| **Full-length testing** | Test 10+ min continuously — uncanny valley compounds over time, spot-checking misses it | Full Chapter 1 (70 segments, ~5 min) generated for all 8 voice pairings |

### Planned

| Practice | What the industry does | Sawt plan |
|----------|----------------------|-----------|
| **Pause variation** | Uniform gaps = metronome effect (#1 TTS listener complaint). Vary break durations | Add slight randomization to break durations (±50-100ms) in audio generation |
| **Proper noun pronunciation** | #1 Arabic TTS failure point — no diacritics in printed Arabic, TTS guesses wrong | Per-book pronunciation dictionary via SSML `<phoneme>` tags for character names |
| **Prosody variation** | Same rhythm repeating = auditory fatigue over hours of listening | `<prosody>` rate/pitch variations between narrative segments (provider-dependent) |

### Not Applicable

| Practice | Why it doesn't apply |
|----------|---------------------|
| **Full-cast production** | Closed — Azure Arabic has only 2 voices/dialect. Two-voice captures 90% of listener value |
| **Emotion/expression styles** | Waiting on Azure — Arabic has zero `mstts:express-as` support. Monitor for updates |
| **Human narrator imperfections** | TTS limitation — "embrace imperfection" applies to human narrators, not synthesized voices |

## Archive

Old documentation (IPA pipeline, Polly, Flask demo) is preserved in [`archive/docs/`](../archive/docs/). The IPA phonological pipeline produced accurate linguistic processing but unusable audio output — the audiobook pipeline takes a fundamentally different approach.
