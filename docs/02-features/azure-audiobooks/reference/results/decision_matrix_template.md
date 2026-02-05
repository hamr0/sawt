# Azure TTS Decision Matrix

**Date:** _____________
**Decision:** [ ] Azure X-SAMPA  [ ] Azure Plain Text  [ ] Other: _________

---

## Evaluation Summary

### X-SAMPA Value Assessment

| Criterion | Result | Weight | Notes |
|-----------|--------|--------|-------|
| **Pronunciation Accuracy Improvement** | Plain: ___ / X-SAMPA: ___ | HIGH | Difference: ___ points |
| **Multi-Voice Consistency** | Plain: ___ / X-SAMPA: ___ | HIGH | Critical for dialogue |
| **Rare Word Handling** | Plain: ___ / X-SAMPA: ___ | MEDIUM | Edge cases matter |
| **Voice Quality** | Plain: ___ / X-SAMPA: ___ | MEDIUM | Both neural voices |
| **Dialect Consistency** | Plain: ___ / X-SAMPA: ___ | MEDIUM | Cross-dialect support |

### Success Criteria Check

**X-SAMPA is worth keeping if:**
- [ ] Azure X-SAMPA scores ≥ 0.5 points higher in pronunciation accuracy
- [ ] Multi-voice consistency noticeably better with X-SAMPA
- [ ] Rare words pronounced more accurately with X-SAMPA

**Result:** ___/3 criteria met

---

## Cost-Benefit Analysis

### Benefits of Keeping X-SAMPA Pipeline

**Pros:**
- [ ] Pronunciation control
- [ ] Multi-dialect support
- [ ] Rare word handling
- [ ] Character consistency in dialogue
- [ ] Future TTS flexibility
- [ ] Linguistic IP ownership

**Measured Value (from tests):**
- Pronunciation improvement: ___ points (1-5 scale)
- Worth the complexity? [ ] Yes  [ ] No

### Costs of Keeping X-SAMPA Pipeline

**Development/Maintenance:**
- Annual maintenance: ~40 hours/year
- Bug fixes: ~10 hours/year
- masterTTS.json updates: ~20 hours/year
- Documentation updates: ~10 hours/year
- **Total:** ~80 hours/year

**Complexity:**
- 4 phonological processors
- 1,030-entry masterTTS.json
- X-SAMPA conversion logic
- Testing overhead

**Is the cost justified?** [ ] Yes  [ ] No

---

## Alternative Scenarios

### Scenario A: Keep X-SAMPA, Use Azure
**When to choose:**
- X-SAMPA shows clear advantage (≥0.5 points)
- Multi-voice audiobooks are priority
- Dialect support needed
- Willing to maintain pipeline

**Implementation:**
- Move azure_integration.py to src/integrations/
- Update app.py with Azure option
- Document Azure setup
- Set as default TTS

### Scenario B: Drop X-SAMPA, Use Azure Plain Text
**When to choose:**
- X-SAMPA shows no advantage (<0.3 points)
- Single-voice audiobooks sufficient
- MSA only needed
- Want to simplify

**Implementation:**
- Remove X-SAMPA generation code
- Keep phonological processors (lightweight)
- Use Azure with plain text
- Simplify pipeline

### Scenario C: Keep X-SAMPA, Use eSpeak/Festival
**When to choose:**
- X-SAMPA shows value
- Cost is major concern
- Local processing required
- Willing to accept robotic voice

**Implementation:**
- Keep current eSpeak setup
- Add Festival as alternative
- Document voice quality trade-off

### Scenario D: Long-term Investment in XTTS
**When to choose:**
- X-SAMPA shows value
- Want both quality AND control
- Willing to invest 3-6 months
- Research/experimentation OK

**Implementation:**
- Keep X-SAMPA pipeline
- Research XTTS Arabic adaptation
- Parallel development with Azure
- Evaluate in 6 months

---

## Decision

### Selected Scenario: _____________

**Reasoning:**

**Key factors in decision:**
1.
2.
3.

**What we're optimizing for:**
- [ ] Voice quality
- [ ] Pronunciation accuracy
- [ ] Cost efficiency
- [ ] Development simplicity
- [ ] Future flexibility
- [ ] Dialect support

---

## Implementation Plan

### Immediate Next Steps (This Week)

1. [ ] Task 1
2. [ ] Task 2
3. [ ] Task 3

### Short-term (2-4 Weeks)

1. [ ] Task 1
2. [ ] Task 2
3. [ ] Task 3

### Long-term (1-3 Months)

1. [ ] Task 1
2. [ ] Task 2
3. [ ] Task 3

---

## Success Metrics

**How we'll measure success:**
1. Metric 1: ___________
2. Metric 2: ___________
3. Metric 3: ___________

**Timeline for evaluation:** _____________

---

## Learnings & Reflections

**What we learned from testing:**

**What surprised us:**

**What we'd do differently:**

**Advice for future TTS decisions:**
