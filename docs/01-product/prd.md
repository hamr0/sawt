# Product Requirements Document (PRD)

**Product:** Arabic TTS System
**Version:** 1.0 (MVP Complete)
**Last Updated:** February 2026

---

## Executive Summary

Arabic TTS is a multi-dialect text-to-speech system that converts Arabic text into phonetically accurate speech. The system uses an IPA-first approach where linguistic intelligence is built internally, with voice synthesis delegated to external services (eSpeak NG for development, Amazon Polly for production).

---

## Problem Statement

Current AI-based Arabic TTS systems produce poor-quality audio unsuitable for audiobook production, particularly across different dialects. This creates a barrier to affordable and scalable Arabic audiobook creation.

### Pain Points

1. **Publishers:** High cost of human narration ($200-400/finished hour)
2. **Authors:** Cannot afford professional Arabic narration
3. **Educators:** Need scalable Arabic content for e-learning
4. **Existing TTS:** Generic systems don't handle dialect-specific phonology

---

## Solution

Build an IPA intermediate representation system that accurately handles Arabic phonological rules BEFORE feeding to neural TTS, improving pronunciation accuracy across 5+ dialects.

### Key Differentiator

> "We own the linguistic intelligence. Voice is a commodity."

- **Internal IP:** Phonological rules, syllabification, IPA mappings
- **External Commodity:** Voice synthesis (can switch providers)

---

## Target Users

| Segment | Primary Need | Priority |
|---------|-------------|----------|
| Audiobook Publishers | High-quality, scalable Arabic narration | P1 |
| Self-Publishing Authors | Affordable Arabic audiobook creation | P2 |
| Educational Content Creators | E-learning Arabic content at scale | P2 |
| Linguistic Researchers | Accurate phonetic transcription | P3 |

---

## Requirements

### Functional Requirements

#### FR1: Text Processing
- [x] Accept Arabic text input (UTF-8)
- [x] Auto-diacritization via Mishkal
- [x] Syllabification with pattern classification
- [x] Support undiacritized and diacritized input

#### FR2: Phonological Processing
- [x] Gemination (shadda handling)
- [x] Sun letter assimilation
- [x] Positional allophones
- [x] Emphatic spread (pharyngealization)

#### FR3: Dialect Support
- [x] MSA (Modern Standard Arabic) - Primary
- [x] Egyptian Arabic - Most tested
- [x] Gulf Arabic - Supported
- [x] Levantine Arabic - Supported
- [x] Maghrebi Arabic - Supported

#### FR4: Output Formats
- [x] IPA transcription
- [x] X-SAMPA conversion
- [x] WAV audio (16-bit PCM, 22050 Hz)
- [x] MP3 audio (via Polly)
- [x] JSON pipeline data
- [x] CSV export

#### FR5: Interfaces
- [x] Python SDK (ArabicTTS class)
- [x] REST API (Flask)
- [x] Web demo interface
- [x] CLI scripts

### Non-Functional Requirements

| Requirement | Target | Actual | Status |
|-------------|--------|--------|--------|
| Syllabification Accuracy | >90% | 96.30% | Exceeded |
| IPA Generation Accuracy | >90% | 94.44% | Exceeded |
| Processing Speed | >10 words/sec | 3,059 w/s | 305x target |
| Test Coverage | >95% | 100% (329/329) | Exceeded |
| Documentation | Complete | 2,000+ lines | Complete |

---

## Success Metrics

### Quality Metrics
- **Pronunciation Accuracy:** >95% for MSA, >90% for dialects
- **Naturalness (MOS):** >3.5/5.0 (human baseline: 4.5)
- **Dialect Consistency:** No mixing of dialectal features

### Business Metrics
- **Cost Reduction:** 80% vs human narration
- **Speed:** <1 hour processing per 10 hours audio
- **AWS Free Tier:** Stay within 5M chars/month during POC

---

## Milestones

### Phase 1: MVP (COMPLETE)
- [x] Core phonological pipeline
- [x] 5 dialect support
- [x] eSpeak NG integration
- [x] 329 tests passing
- [x] Web demo interface

### Phase 2: Polly Integration (IN PROGRESS)
- [x] POC validation complete
- [x] X-SAMPA conversion working
- [ ] Long-form content testing
- [ ] Production wrapper
- [ ] Cost monitoring

### Phase 3: Production (PLANNED)
- [ ] Full audiobook processing
- [ ] Quality metrics at scale
- [ ] Multi-dialect optimization

---

## Out of Scope (v1)

- Voice cloning / custom voices
- Real-time streaming synthesis
- Mobile SDKs
- Speech-to-text (STT)
- Non-Arabic languages

---

## Dependencies

| Dependency | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime |
| mishkal | 0.4.1 | Diacritization |
| eSpeak NG | 1.50+ | Dev voice synthesis |
| boto3 | 1.28+ | AWS Polly |
| Flask | 3.0+ | REST API |

---

## Appendix

### Related Documents
- `00-context/vision.md` - Business analysis and market research
- `00-context/system-state.md` - Technical architecture
- `02-features/polly/` - Polly integration documentation
