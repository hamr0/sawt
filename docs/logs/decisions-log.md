# Decisions Log

Architecture and design decisions with rationale. Record decisions that future-you would want to know about.

## Format

```
### YYYY-MM-DD: [Decision]
**Context:** Why this came up
**Decision:** What was decided
**Rationale:** Why
**Alternatives considered:** What else was on the table
```

---

### 2026-02-05: Azure plain text over IPA phoneme control
**Context:** IPA pipeline produced accurate linguistic processing but unusable audio
**Decision:** Send plain Arabic text to Azure neural voices, no phoneme-level control
**Rationale:** Azure's neural models handle pronunciation better than letter-by-letter SSML phoneme tags. The IPA approach was technically impressive but produced robotic output.
**Alternatives:** Continue refining IPA pipeline, try different TTS engines with phoneme support

### 2026-02-05: Two-voice primary, multi-voice stretch
**Context:** Need to decide voice approach for audiobook production
**Decision:** Binary narration/dialogue classification first, per-character attribution later
**Rationale:** Two-voice is tractable (colon detection already works), covers 70-80% of fiction. Multi-voice attribution sits at 63.5% automated after 7 iterations — hard problem.
**Alternatives:** Jump straight to multi-voice, single-voice only

### 2026-02-05: POC isolation by data boundaries
**Context:** How should pipeline stages connect?
**Decision:** Each POC reads from previous POC's file output, not its code
**Rationale:** Can rewrite any POC without breaking the next one. CSV files at every stage enable review.
**Alternatives:** Direct function calls between stages, shared data models

### 2026-02-05: No dialect switching per book
**Context:** Azure offers 14+ voices across 7 Arabic dialects
**Decision:** One voice profile per book, no mid-book dialect switching
**Rationale:** Arabic dialect changes expressions and meaning, not just accent. Switching dialects mid-book would sound unnatural and change meaning.
**Alternatives:** Detect dialogue dialect per character, match voice dialect
