# Insights & Learnings

Capture key learnings, patterns discovered, and knowledge gained.

---

## Technical Insights

### Arabic Phonology

1. **Processor Order Matters**
   - Gemination must happen before sun letter assimilation
   - Sun letter assimilation creates geminates that affect later processing
   - Emphatic spread is always last (modifies vowels based on final consonant context)

2. **Syllable Patterns**
   - 6 patterns cover standard Arabic: CV, CVC, CVV, CVCC, CVVC, V
   - Edge cases exist but are rare (<5%)
   - Resyllabification post-processor handles most edge cases

3. **Diacritization Quality**
   - Mishkal is reliable for MSA but less accurate for dialectal text
   - ~20% processing overhead is acceptable for accuracy gain
   - Manual review recommended for critical content

### Integration Learnings

1. **Amazon Polly**
   - Zeina voice (Arabic) = standard engine ONLY, no neural
   - X-SAMPA input works well via SSML `<phoneme>` tag
   - Fallback to plain text when X-SAMPA fails is robust strategy

2. **eSpeak NG**
   - Good for development/testing, not production quality
   - X-SAMPA input supported but voice is robotic
   - Useful as fallback when Polly unavailable

### Architecture Insights

1. **IPA-First Approach**
   - Validated as correct strategy for Arabic
   - Separates "what to say" (our IP) from "how to say it" (commodity)
   - Enables provider switching without losing value

2. **Universal vs Dialect-Specific**
   - Phonological rules are universal to Arabic
   - Only IPA mappings vary by dialect
   - Clean separation improves maintainability

---

## Process Insights

1. **Test-First Development**
   - 329 tests caught many edge cases early
   - Smoke tests for dependencies prevent environment issues
   - Integration tests validate end-to-end behavior

2. **Documentation Value**
   - CLAUDE.md provides excellent AI assistant context
   - Architecture docs prevent repeated explanations
   - Decision logs preserve rationale for future reference

3. **Incremental Validation**
   - Start with small test set (5 sentences)
   - Validate at each pipeline stage
   - Scale up gradually (25 → 100 → 1000)

---

## What Worked Well

- IPA-first architecture for Arabic TTS
- Comprehensive test coverage (329 tests)
- Separating universal processing from dialect-specific lookup
- AWS Free Tier for POC validation
- Detailed documentation (CLAUDE.md, KNOWLEDGE_BASE.md)

## What Could Be Improved

- Earlier integration of Polly (could have validated voice quality sooner)
- More automated quality metrics (MOS scoring)
- Dialect-specific test sentences (currently EG-heavy)
- Performance profiling at scale

---

## Future Considerations

1. **Voice Options**
   - Monitor AWS for neural Arabic voices
   - Evaluate XTTS/Coqui for self-hosted alternative

2. **Dialect Expansion**
   - Maghrebi dialect needs more entries (159 vs 230 for EG)
   - Consider dialect detection for mixed text

3. **Scale Testing**
   - Full audiobook processing validation needed
   - Cost optimization at volume
