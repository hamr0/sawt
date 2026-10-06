---
title: Risks and Go-to-Market
theme: risks-go-to-market
sources:
  - docs/archive/PLAN.md
description: Risk register and go-to-market strategy for Sawt.
---

# Risks and Go-to-Market

This page covers the project risk register and the phased go-to-market plan, with the status of each item as recorded in the plan.

## Risk Register

Each risk is rated by likelihood and impact, with a mitigation and a current status (docs/archive/PLAN.md:848-851).

### Resolved or closed

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| EPUB paragraph boundaries inconsistent across publishers | Medium | High | Test on 5+ books from different sources | Resolved: tested on 12 books |
| Chapter detection fails on unusual structures | Medium | Medium | Fallback: manual chapter markers or size-based splitting | Resolved: size fallback works |
| Quotation conventions vary wildly between books | High | Medium | Build normalizer, test on 3+ books with different styles | Resolved: guillemets kept as narrator |
| Multi-voice review is too painful to scale | High | Medium | ~~Accept it as the cost~~ | Closed: Phase B skipped entirely |

(docs/archive/PLAN.md:852-856)

### Open

| Risk | Likelihood | Impact | Mitigation | Status |
|------|-----------|--------|------------|--------|
| Two-voice doesn't sound good enough | Low | High | Already tested in prototypes: voice switching works | Open: validate with POC-4 sampling |
| Azure Arabic has no emotion/style support | High | Medium | Wait for Azure updates; prosody knobs are all we have | Open: monitor Azure |
| Voice pair sounds wrong for a dialect | Medium | Low | Sampling script tests 3 dialects before committing | Open: POC-4 |
| Azure free tier runs out during testing | Low | Low | Monitor usage, ~$8-12/book if needed | Open |
| Competitor (Lahajati) builds same pipeline | Medium | High | Ship fast, build content moat with published audiobooks | Open |
| AI narration quality insufficient for fiction | Medium | Medium | Two-voice masks artifacts; prosody tuning if needed | Open: validate with POC-4 |

(docs/archive/PLAN.md:855-861)

## Go-to-Market Strategy

Detailed analysis lives in `research/MARKET_RESEARCH.md` (docs/archive/PLAN.md:865-867).

### Phases

- **Phase 1 (Months 1-3):** Produce 20-30 public domain audiobooks from the Hindawi CC catalog. Publish on YouTube and Spotify/Anghami. Build portfolio and audience, and refine the pipeline end-to-end (docs/archive/PLAN.md:869-872).
- **Phase 2 (Months 3-5):** Offer a manual audiobook conversion service to young Arab authors at $20-40/book, marketed via Arabic social media. Success metric: 5+ paying customers (docs/archive/PLAN.md:874-875).
- **Phase 3 (Months 5-8):** If demand validates, build a self-serve web tool at $15-25/book (docs/archive/PLAN.md:877).

### Target audience (prioritized)

1. Young Arab authors and small publishers: they can't afford $1,000+ human narration and write in DOCX.
2. Content consumers: reached through published content, not direct marketing.
3. Institutions: later, when the product is proven.

(docs/archive/PLAN.md:879-882)

### Distribution channels

- YouTube: highest Arabic audiobook search volume, evergreen.
- Spotify / Apple Podcasts: podcast format.
- Anghami: 70M users, Arabic-native.
- Audible: accepts AI narration via its "Virtual Voice" program.
- Arabookverse: Arabic audiobook distributor, 300+ platforms.

(docs/archive/PLAN.md:884-889)
