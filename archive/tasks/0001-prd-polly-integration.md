# PRD: Amazon Polly TTS Integration - Proof of Concept

**Date:** November 3, 2025  
**Status:** Draft  
**Owner:** Development Team  
**Timeline:** This week (POC phase)

---

## 1. Introduction / Overview

This PRD defines the requirements for integrating Amazon Polly neural TTS engine into the ArabicTTS system as a proof-of-concept. The current system uses eSpeak for audio generation, which produces robotic-sounding output suitable for development verification but not production audiobooks.

**Problem Statement:**
- eSpeak audio quality is insufficient for customer-facing audiobooks
- Need to validate whether Polly can produce natural-sounding Arabic speech using our existing IPA/X-SAMPA phonetic pipeline
- Must test before committing to larger architectural changes or budget allocation

**High-Level Goal:**
Test Polly integration with minimal code changes (≤50 lines) to determine if it produces acceptable audio quality for MSA (Modern Standard Arabic) audiobooks, while staying within budget constraints ($0-50/month or AWS free tier).

---

## 2. Goals

1. **Validate Audio Quality** - Determine if Polly neural voices produce significantly better audio than eSpeak for Arabic text
2. **Preserve Architecture** - Integrate Polly without modifying the existing IPA/X-SAMPA phonetic pipeline
3. **Control Costs** - Stay within AWS free tier (5M characters/month) or minimal budget during POC
4. **Quick Turnaround** - Complete POC testing within one week
5. **Gather Validation Data** - Collect feedback from native Arabic speakers on pronunciation accuracy
6. **Document Decision Path** - Create clear criteria for proceeding to production integration or exploring alternatives

---

## 3. User Stories

**As a development team member**, I want to test Polly integration quickly so that I can assess audio quality without major code changes.

**As an audiobook listener**, I want natural-sounding Arabic speech so that the listening experience is pleasant and professional.

**As a native Arabic speaker**, I want accurate pronunciation of MSA text so that I can validate the system produces correct speech.

**As a project stakeholder**, I want to understand costs and quality trade-offs so that I can make informed decisions about production implementation.

**As a developer**, I want the integration to preserve our existing phonetic pipeline so that we don't lose the 96.30% syllabification and 94.44% IPA accuracy we've achieved.

---

## 4. Functional Requirements

### 4.1 AWS Integration

**FR-001:** The system must install and configure boto3 (AWS SDK for Python) as a dependency.

**FR-002:** The system must support AWS credential configuration via environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION).

**FR-003:** The system must support AWS credential configuration via config file (~/.aws/credentials or project-level config).

**FR-004:** The system must default to us-east-1 region if no region is specified.

### 4.2 Polly Wrapper Implementation

**FR-005:** The system must implement a PollyTTS class that wraps Amazon Polly API calls.

**FR-006:** The PollyTTS class must accept X-SAMPA phonetic representations as input (from existing pipeline).

**FR-007:** The PollyTTS class must convert X-SAMPA to SSML format required by Polly.

**FR-008:** The system must support both 'Zeina' (MSA) and 'Hala' (Gulf Arabic) voice options.

**FR-009:** The system must support both 'neural' and 'standard' Polly engine options, defaulting to 'neural'.

**FR-010:** The system must generate MP3 audio files as output.

**FR-011:** The system must handle Polly API errors gracefully and return meaningful error messages.

### 4.3 Testing Requirements

**FR-012:** The system must include a test script that processes 5 representative Arabic sentences.

**FR-013:** The test sentences must cover various phonetic patterns: short vowels, long vowels, consonant clusters, shadda, and tanween.

**FR-014:** The system must generate audio files with clear naming (e.g., test_polly_001.mp3, test_polly_002.mp3).

**FR-015:** The system must provide a comparison mechanism to generate both eSpeak and Polly audio for the same input text.

### 4.4 Pipeline Integration

**FR-016:** The Polly integration must use the existing ArabicTTS.process_text() method without modification.

**FR-017:** The system must accept IPA or X-SAMPA output from the existing pipeline without requiring pipeline changes.

**FR-018:** The integration must not modify masterTTS.json phonetic mappings.

**FR-019:** The system must maintain compatibility with existing eSpeak output (dual engine support).

### 4.5 Documentation

**FR-020:** The system must document AWS setup steps (account creation, credential generation, configuration).

**FR-021:** The system must document the test execution procedure.

**FR-022:** The system must provide examples of how to run tests with different voices and engines.

---

## 5. Non-Goals (Out of Scope)

The following are explicitly **NOT** included in this POC phase:

**NG-001:** Removing eSpeak dependency - Both engines should coexist during POC

**NG-002:** Library cleanup - Removing unused dependencies (tqdm, PyYAML, python-Levenshtein) is deferred

**NG-003:** Adding missing kasratan character (ٍ) to masterTTS.json - Current 99% coverage is acceptable for POC

**NG-004:** Production deployment - No production release or customer-facing deployment in this phase

**NG-005:** Cost optimization features - Caching, phrase optimization, or character usage optimization

**NG-006:** Voice customization - Custom lexicons, speaking rate adjustment, pitch modification

**NG-007:** Batch processing - Processing multiple audiobooks or large-scale generation

**NG-008:** Alternative TTS engines - XTTS, Coqui, or other TTS solutions are not evaluated in this phase

**NG-009:** Mobile or web integration - Focus is on command-line/script usage only

**NG-010:** Multi-dialect support expansion - Focus on MSA (Zeina voice) with optional Gulf (Hala) testing

---

## 6. Design Considerations

### 6.1 Architecture

The integration follows a wrapper pattern:

```
User Input (Arabic Text)
    ↓
ArabicTTS.process_text() [EXISTING - NO CHANGES]
    ↓
IPA/X-SAMPA Output [EXISTING]
    ↓
PollyTTS.generate_audio() [NEW - 50 lines]
    ↓
MP3 Audio Output
```

### 6.2 Dual Engine Support

During POC, both engines remain available:

- **eSpeak:** Quick verification, offline development, debugging
- **Polly:** Quality assessment, native speaker validation, production evaluation

### 6.3 Test Sentences Selection

The 5 test sentences should represent:
1. Simple sentence with common words
2. Sentence with consonant clusters
3. Sentence with tanween and diacritics
4. Longer sentence (10-15 words)
5. Sentence with proper nouns or challenging phonemes

---

## 7. Technical Considerations

### 7.1 Dependencies

**New dependency:**
- boto3>=1.28.0 (AWS SDK)

**Existing dependencies preserved:**
- mishkal>=0.4.1 (diacritization)
- All other current dependencies remain unchanged

### 7.2 API Constraints

- **Free tier limit:** 5 million characters/month (neural voices) for first 12 months
- **Character estimate:** 5 test sentences ≈ 200-500 characters (negligible usage)
- **Network requirement:** Internet connection required for Polly API calls (unlike eSpeak)
- **Latency:** Network round-trip adds ~500ms-2s per request (acceptable for POC)

### 7.3 Error Handling

The system must handle:
- Missing AWS credentials → Clear error message with setup instructions
- Network failures → Timeout with retry suggestion
- Invalid X-SAMPA → Fallback to plain text with warning
- API rate limits → Graceful error with wait time indication
- Insufficient permissions → IAM policy requirements message

### 7.4 File Structure

```
src/
  integrations/
    polly.py          [NEW] - PollyTTS wrapper class
  main.py             [UNCHANGED] - Existing ArabicTTS class

scripts/
  test_polly_integration.py  [NEW] - POC test script

demo_output/
  polly_test/         [NEW] - Test audio output directory
```

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

**SM-001:** POC completion time ≤ 5 working days

**SM-002:** Code changes ≤ 100 lines (target: ~50 lines)

**SM-003:** Test execution time ≤ 5 minutes for 5 sentences

**SM-004:** Cost during POC: $0 (within free tier)

**SM-005:** Zero breaking changes to existing tests (329 tests remain passing)

### 8.2 Qualitative Metrics

**SM-006:** Audio quality subjectively rated "much better than eSpeak" by development team

**SM-007:** Native Arabic speaker validation: ≥90% pronunciation accuracy

**SM-008:** Native speaker feedback: Audio is "acceptable for audiobooks" (yes/no)

**SM-009:** X-SAMPA to SSML conversion preserves phonetic accuracy (verified by listening)

### 8.3 Decision Criteria

**Proceed to Production Integration if:**
- SM-006: Quality is significantly better (⭐⭐⭐ or higher vs eSpeak's ⭐⭐)
- SM-007: Native speaker validation ≥90%
- SM-008: Native speaker confirms acceptability
- SM-004: Costs are within budget

**Iterate/Tune if:**
- Audio quality is good but has specific pronunciation issues
- Cost is acceptable but needs optimization
- Minor X-SAMPA mapping adjustments needed

**Consider Alternatives if:**
- Audio quality is not significantly better than eSpeak
- Cost projections exceed budget ($50+/month for expected volume)
- Major architectural changes would be required

---

## 9. Open Questions

**OQ-001:** Which specific 5 test sentences should be used? (Need input from native speaker or linguistics expert)

**OQ-002:** Should we test both Zeina (MSA) and Hala (Gulf) voices in POC, or focus on Zeina only?

**OQ-003:** Who will conduct the native speaker validation? (Internal team member or external validator?)

**OQ-004:** What is the acceptable timeline for native speaker feedback? (Same week or following week?)

**OQ-005:** If POC succeeds, what is the budget ceiling for production usage? (Current estimate: $0-50/month)

**OQ-006:** Should IPA be tested as an alternative to X-SAMPA if initial X-SAMPA results have issues?

**OQ-007:** Are there specific audiobook genres or content types to prioritize for testing? (Religious texts, literature, educational content?)

**OQ-008:** What is the fallback plan if Polly doesn't meet requirements? (Evaluate XTTS, commercial alternatives, or continue with eSpeak?)

---

## 10. Post-POC Decision Path

Upon POC completion, the following steps are required:

**Step 1: Expand Testing (OQ-001, OQ-007)**
- Extend test corpus from 5 to 25 sentences
- Cover diverse content types and phonetic patterns
- Document any pronunciation issues discovered

**Step 2: Native Speaker Validation (OQ-003, OQ-004)**
- Conduct structured listening session with native Arabic speaker
- Use standardized evaluation criteria (pronunciation, naturalness, clarity)
- Document feedback and specific issues

**Step 3: Document Decision Criteria (All metrics)**
- Compile all success metrics (SM-001 through SM-009)
- Calculate projected costs for production volumes
- Create recommendation report with Go/No-Go/Iterate options

**Step 4: Stakeholder Review**
- Present findings to project stakeholders
- Discuss budget implications if proceeding to production
- Obtain approval for next phase or alternative approach

---

## Appendix A: Test Sentence Examples

*Note: Final sentences should be selected by native speaker or linguistics expert*

**Suggested test sentences:**

1. **Simple:** صباح الخير (Good morning)
2. **Consonant clusters:** المدرسة الجديدة (The new school)
3. **Tanween:** كتابٌ جديدٌ (A new book)
4. **Longer:** ذهبتُ إلى السوق لشراء بعض الخضروات والفواكه (I went to the market to buy some vegetables and fruits)
5. **Challenging:** القواعد الإملائية والنحوية (Spelling and grammatical rules)

---

## Appendix B: Success Criteria Checklist

Before proceeding to production integration, verify:

- [ ] All 5 test audio files generated successfully
- [ ] Subjective quality assessment: Polly > eSpeak
- [ ] Native speaker validation completed (≥90% accuracy)
- [ ] Native speaker confirms "acceptable for audiobooks"
- [ ] No breaking changes to existing pipeline
- [ ] AWS costs: $0 during POC
- [ ] Code changes: ≤100 lines
- [ ] POC completed within 1 week
- [ ] Decision criteria documented
- [ ] Post-POC path defined and approved

---

**END OF PRD**

---

## Next Steps

1. Review and approve this PRD
2. Select final test sentences (with native speaker input)
3. Implement PollyTTS wrapper (~2 hours)
4. Execute test script and generate audio
5. Conduct listening evaluation
6. Schedule native speaker validation
7. Document findings and recommendation
