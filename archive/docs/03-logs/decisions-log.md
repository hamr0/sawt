# Decisions Log

Track architectural and technical decisions with rationale.

---

## Format

```
## DEC-XXX: Decision Title

**Date:** YYYY-MM-DD
**Status:** Accepted | Superseded | Deprecated
**Context:** Why this decision was needed
**Decision:** What was decided
**Rationale:** Why this choice
**Consequences:** Impact of decision
```

---

## Decisions

### DEC-001: IPA-First Architecture

**Date:** 2025-10-01
**Status:** Accepted
**Context:** Need to build Arabic TTS with high pronunciation accuracy across dialects
**Decision:** Build linguistic intelligence internally (IPA/phonology), use external voice synthesis
**Rationale:**
- Own the IP (phonological rules, syllabification)
- Voice is commodity (can switch providers)
- Better control over dialect-specific pronunciation
- Debug-friendly vs black-box neural TTS
**Consequences:**
- More upfront work on phonological rules
- Can switch voice providers without losing core value
- Pronunciation accuracy depends on our rules, not training data

### DEC-002: Phonological Processor Order

**Date:** 2025-10-15
**Status:** Accepted
**Context:** Multiple phonological rules interact with each other
**Decision:** Fixed processing order: Gemination → Sun Letters → Allophones → Emphatic Spread
**Rationale:**
- Gemination affects consonant doubling (must happen first)
- Sun letter assimilation depends on geminated consonants
- Allophones depend on both above
- Emphatic spread is final vowel modification
**Consequences:**
- Order cannot be changed without breaking accuracy
- Each processor is independent but assumes prior processing
- Testing must respect this order

### DEC-003: masterTTS.json Lookup After Processing

**Date:** 2025-10-20
**Status:** Accepted
**Context:** Dictionary lookup timing affects output
**Decision:** IPA lookup from masterTTS.json happens AFTER all phonological processing
**Rationale:**
- Processing creates context markers (geminated, emphatic, position)
- Dictionary entries include context-specific variants
- Lookup with context = accurate IPA
**Consequences:**
- Dictionary entries must cover all context combinations
- Cannot do early dictionary lookup optimization
- Architecture is validated and working

### DEC-004: Amazon Polly for Production Voice

**Date:** 2025-10-30
**Status:** Accepted
**Context:** eSpeak NG produces robotic voice unsuitable for audiobooks
**Decision:** Use Amazon Polly (Zeina voice) for production audio
**Rationale:**
- Significantly better voice quality
- Accepts X-SAMPA/SSML input (matches our pipeline)
- Cost-effective ($16/million chars, 5M/month free)
- Strategic fit: we own linguistics, they provide voice
**Consequences:**
- AWS credentials required
- Zeina uses standard engine only (not neural)
- Cost monitoring needed at scale

### DEC-005: Universal Processors (No Dialect Parameter)

**Date:** 2025-12-14
**Status:** Accepted
**Context:** Processors were accepting dialect parameter but not using it
**Decision:** Remove dialect parameter from all processors; dialect only affects IPA lookup
**Rationale:**
- Phonological rules (gemination, sun letters, emphatics) are universal to Arabic
- Only IPA mapping varies by dialect
- Cleaner API, reduced confusion
**Consequences:**
- Breaking change for old API (see migration guide)
- AllophoneProcessor deprecated in favor of PositionDetector + IPAMapper
- Dialect is runtime parameter at IPA lookup only

---

## Template for New Decisions

```
### DEC-XXX: Title

**Date:**
**Status:**
**Context:**
**Decision:**
**Rationale:**
**Consequences:**
```
