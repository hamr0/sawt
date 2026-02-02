# Assumptions, Constraints & Risks

**Project:** Arabic TTS System
**Last Updated:** February 2026

---

## Assumptions

### Technical Assumptions

1. **Arabic Text Input**
   - Input text is valid UTF-8 encoded Arabic
   - Text may or may not include diacritics (tashkeel)
   - Mishkal library can handle diacritization reliably

2. **Phonological Processing**
   - The 4-processor pipeline order is linguistically correct:
     Gemination → Sun Letters → Allophones → Emphatic Spread
   - masterTTS.json lookup must happen AFTER phonological processing
   - 6 syllable patterns cover standard Arabic (CV, CVC, CVV, CVCC, CVVC, V)

3. **Voice Synthesis**
   - eSpeak NG is acceptable for development/testing
   - Amazon Polly provides production-quality voice output
   - X-SAMPA conversion is compatible with Polly SSML input

4. **Dialect Coverage**
   - MSA and Egyptian Arabic are primary targets
   - Other dialects (Gulf, Levantine, Maghrebi) are secondary
   - masterTTS.json has sufficient coverage (1,030 entries)

### Business Assumptions

1. **Target Market**
   - Arabic audiobook market is underserved
   - Quality TTS can reduce production costs by 80%+
   - Users prioritize pronunciation accuracy over voice variety

2. **Cost Model**
   - AWS Free Tier (5M chars/month) covers POC phase
   - Production costs of ~$16/million chars are acceptable
   - IPA-based approach provides competitive advantage

---

## Constraints

### Technical Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Polly Zeina voice: standard engine only | No neural voice for Arabic | Accept standard quality (still better than eSpeak) |
| Mishkal diacritization adds ~20% overhead | Slight performance impact | Acceptable tradeoff for accuracy |
| Single dialect per processing run | Cannot mix dialects in one text | Design constraint, not a bug |

### Resource Constraints

- AWS credentials required for Polly
- eSpeak NG must be installed for fallback/testing
- Python 3.10+ required

### Dependency Constraints

- mishkal v0.4.1 (diacritization)
- boto3 >= 1.28.0 (AWS Polly)
- Flask 3.0+ (web API)

---

## Risks

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Mishkal produces incorrect diacritics | Medium | High | Manual review for critical content |
| X-SAMPA edge cases not handled | Low | Medium | Fallback to plain Arabic text |
| Polly service changes/deprecation | Low | High | Architecture allows provider switching |

### Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| AWS pricing changes | Low | Medium | Monitor costs, budget alerts |
| Competition from end-to-end neural TTS | Medium | Medium | IPA gives control over pronunciation |
| Limited dialect demand | Medium | Low | Focus on MSA first |

---

## Unknowns (To Be Validated)

1. **Long-form Content Quality**
   - How does Polly perform on full chapters/books?
   - Are there prosody issues at paragraph boundaries?

2. **Dialect Accuracy**
   - Is Egyptian Arabic coverage sufficient for native speakers?
   - Do Levantine/Gulf dialects need expansion?

3. **Production Scale**
   - Processing speed at 100K+ word scale
   - AWS cost patterns at volume

---

## Decision Log Reference

See `03-logs/decisions-log.md` for recorded architectural decisions.
