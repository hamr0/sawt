# PRD: Arabic TTS MVP - Phase 1

**Product:** Arabic Text-to-Speech System (IPA-Based)  
**Phase:** 1 (MVP)  
**Version:** 1.0  
**Date:** October 30, 2025  
**Owner:** Developer  
**Status:** Ready for Implementation

---

## 1. Introduction/Overview

### Problem Statement
Current commercial Arabic TTS systems (Google, Amazon, Microsoft) produce poor-quality audio unsuitable for audiobook production, particularly for dialect-specific content. They lack proper handling of Arabic phonological rules and cannot support regional dialects effectively.

### Solution
Build an IPA (International Phonetic Alphabet) intermediate representation system that accurately processes Arabic phonological rules BEFORE generating audio. This approach provides explicit control over pronunciation, enabling higher accuracy and dialect-specific handling.

### High-Level Goal
Prove that the IPA-based approach produces better Arabic pronunciation than direct text-to-audio commercial TTS systems, validating the architecture for future expansion to multiple dialects and commercial audiobook production.

---

## 2. Goals

### Primary Goals
1. **Validate IPA Approach**: Demonstrate that IPA intermediate layer produces more accurate pronunciation than commercial TTS
2. **Working End-to-End Pipeline**: Build functional text → IPA → audio pipeline that processes real Arabic text
3. **Technical Validation**: Achieve >95% syllabification accuracy and >90% IPA mapping accuracy
4. **Proof of Concept**: Create demo-able prototype showing Egyptian Arabic processing with correct phonological rules

### Secondary Goals
1. Enable testing with real-world undiacritized Arabic text (Wikipedia, news, books)
2. Establish foundation for Phase 2 expansion (additional dialects, better audio quality)
3. Document learnings and validate technical approach for scaling

### Success Criteria
- Syllabification accuracy >95% on test dataset
- IPA generation accuracy >90% on test dataset
- Pronunciation errors <10% on native speaker review
- All automated tests passing (100%)
- Working demo processing 10+ example sentences

---

## 3. User Stories

### As a Developer (Primary User)
1. **As a developer**, I want to input undiacritized Arabic text so that I can test the system with real-world content
2. **As a developer**, I want to see the IPA representation of Arabic text so that I can validate pronunciation rules are applied correctly
3. **As a developer**, I want to hear audio output so that I can verify the pronunciation sounds correct
4. **As a developer**, I want to run automated tests so that I can validate each component works correctly
5. **As a developer**, I want to process text in the web interface so that I can demo the system easily

### As a Native Arabic Speaker (Validator)
1. **As a native Egyptian Arabic speaker**, I want to listen to generated audio so that I can validate pronunciation accuracy
2. **As a validator**, I want to compare the system output with commercial TTS so that I can judge which sounds better
3. **As a validator**, I want to hear words with gemination and sun letters so that I can verify phonological rules work correctly

### As a Future Beta User
1. **As an audiobook publisher**, I want to see a working demo so that I can evaluate if this solves my pronunciation problems
2. **As a potential customer**, I want to hear Egyptian Arabic audio so that I can assess if the dialect support is accurate

---

## 4. Functional Requirements

### 4.1 Text Input & Processing
**FR-1.1** The system MUST accept Arabic text input through a web interface  
**FR-1.2** The system MUST accept both diacritized and undiacritized Arabic text  
**FR-1.3** The system MUST automatically add diacritics to undiacritized text using mishkal  
**FR-1.4** The system MUST tokenize text into words, characters, and punctuation  
**FR-1.5** The system MUST identify character positions (initial, medial, final)

### 4.2 Syllabification
**FR-2.1** The system MUST segment Arabic words into syllables  
**FR-2.2** The system MUST classify syllable patterns as CV, CVC, CVCC, or CVV  
**FR-2.3** The system MUST achieve >95% accuracy on syllable pattern classification  
**FR-2.4** The system MUST NOT return "UNKNOWN" patterns for valid Arabic syllables  
**FR-2.5** The system MUST validate syllable patterns against dialect-specific rules

### 4.3 Phonological Rule Processing
**FR-3.1** The system MUST detect gemination (shadda ّ) and mark consonants as doubled [C:]  
**FR-3.2** The system MUST apply sun letter assimilation (/al/ + sun letter → gemination)  
**FR-3.3** The system MUST apply emphatic spread (pharyngealization near ص، ط، ض، ظ)  
**FR-3.4** The system MUST apply positional allophone rules based on character position  
**FR-3.5** The system MUST apply phonological rules in correct order:
   1. Gemination (first)
   2. Sun letter assimilation (second)
   3. Positional allophones (third)
   4. Emphatic spread (fourth)
   5. Context rules (fifth)

### 4.4 IPA Generation
**FR-4.1** The system MUST generate IPA/X-SAMPA representation for each word  
**FR-4.2** The system MUST use masterTTS.json dictionary for phonetic mappings  
**FR-4.3** The system MUST apply Egyptian Arabic (EG) dialect rules  
**FR-4.4** The system MUST mark syllable boundaries in IPA output  
**FR-4.5** The system MUST achieve >90% IPA accuracy compared to expert validation

### 4.5 Audio Generation
**FR-5.1** The system MUST generate audio from IPA using eSpeak NG  
**FR-5.2** The system MUST produce intelligible audio (MOS score >3.0)  
**FR-5.3** The system MUST generate WAV format audio files  
**FR-5.4** The system MUST allow users to download generated audio  
**FR-5.5** The system MUST process audio generation in <10 seconds per sentence

### 4.6 Web Interface
**FR-6.1** The system MUST provide a web interface at http://localhost:5000  
**FR-6.2** The system MUST display input text area with RTL (right-to-left) support  
**FR-6.3** The system MUST show IPA output in JSON format  
**FR-6.4** The system MUST provide audio player to listen to generated speech  
**FR-6.5** The system MUST allow downloading results as JSON file

### 4.7 Testing & Validation
**FR-7.1** The system MUST have automated unit tests for each component  
**FR-7.2** The system MUST have integration tests for full pipeline  
**FR-7.3** The system MUST pass 100% of automated tests  
**FR-7.4** The system MUST include test dataset with 10+ Egyptian Arabic examples  
**FR-7.5** The system MUST provide test runner command for validation

### 4.8 Data Requirements
**FR-8.1** The system MUST load masterTTS.json phonetic dictionary on startup  
**FR-8.2** The system MUST load syllable_patterns.json for pattern validation  
**FR-8.3** The system MUST use Egyptian Arabic (EG) dialect data from masterTTS.json  
**FR-8.4** The system MUST define sun letters list: {ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن}  
**FR-8.5** The system MUST define emphatic consonants list: {ص، ض، ط، ظ، ق}

---

## 5. Non-Goals (Out of Scope for Phase 1)

### Explicitly Out of Scope
**NG-1** Multiple dialects - Only Egyptian Arabic (EG) in Phase 1. MSA, Gulf, Levantine deferred to Phase 2+  
**NG-2** Prosody modeling - No stress assignment, intonation, or rhythm modeling. Deferred to Phase 3  
**NG-3** High-quality audio - eSpeak NG is sufficient. Coqui TTS/Tacotron2 upgrade deferred to Phase 2  
**NG-4** Performance optimization - Speed is not a concern for MVP. Optimization deferred  
**NG-5** REST API - Flask web UI only. API development deferred to Phase 2  
**NG-6** User accounts/authentication - No login system needed for MVP  
**NG-7** Custom voice training - Standard voices only  
**NG-8** Real-time processing - Batch processing is sufficient  
**NG-9** Mobile apps - Web interface only  
**NG-10** Cloud deployment - Local/VPS deployment only (no AWS/Azure/GCP)

### Why Egyptian Arabic First (Not MSA)
- Egyptian Arabic phonetic database in masterTTS.json is ~80% complete
- MSA phonetic database is only ~30-40% complete
- Better data quality enables better validation
- Can expand to MSA in Phase 2 after proving approach works

---

## 6. Design Considerations

### 6.1 User Interface
**Existing Flask Web Interface** (`templates/index.html`)
- Single-page web application
- Arabic text input with RTL support
- Dialect selector (will show only "Egyptian" for Phase 1)
- "Parse Text" button triggers processing
- JSON output display area
- Audio player for generated speech
- Download buttons for JSON results

**Design Principles:**
- Simple, functional interface (not focused on aesthetics)
- Clear feedback during processing
- Easy to demo to stakeholders
- Accessible for testing by native speakers

### 6.2 Processing Pipeline Visualization
```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1 MVP Pipeline                                         │
└─────────────────────────────────────────────────────────────┘

INPUT: Arabic Text (diacritized or undiacritized)
   ↓
[0] Diacritization (mishkal) ← Added Week 1
   ↓
[1] Tokenization
   - Split into words/chars/punctuation
   ↓
[2] Character Analysis  
   - Identify position (initial/medial/final)
   - Classify type (letter/diacritic/punctuation)
   ↓
[3] Word Grouping
   - Group Arabic characters into words
   ↓
[4] Syllabification ← FIX REQUIRED
   - Segment into syllables
   - Classify patterns (CV/CVC/CVCC/CVV)
   ↓
[5] Phonological Rules (IN ORDER)
   5.1 Gemination (shadda ّ) ← NEW
   5.2 Sun Letter Assimilation ← NEW
   5.3 Positional Allophones
   5.4 Emphatic Spread ← NEW
   5.5 Context Rules
   ↓
[6] IPA Mapping
   - Convert to IPA/X-SAMPA
   - Use Egyptian Arabic rules
   ↓
[7] Audio Generation
   - eSpeak NG with IPA input
   ↓
OUTPUT: IPA JSON + WAV Audio File
```

### 6.3 Data Flow
```
User Input → Flask Backend → Processing Pipeline → Audio + JSON → User Download
```

---

## 7. Technical Considerations

### 7.1 Technology Stack (APPROVED - No Changes)

| Component | Technology | Version | Rationale |
|-----------|------------|---------|-----------|
| **Language** | Python | 3.10+ | Perfect for NLP/ML, matches preferences |
| **Web Framework** | Flask | 3.1.2 | Lightweight, simple, Python-native |
| **Data Processing** | NumPy, Pandas | Latest | Standard tools, mature, open-source |
| **Testing** | pytest | 8.4.2 | Preferred testing framework |
| **Diacritization** | mishkal | Latest | Free, OSS, ~84% accuracy |
| **TTS Engine** | eSpeak NG | Latest | Free, OSS, lightweight, swappable |
| **Storage** | JSON files | N/A | Simple, no DB needed for MVP |
| **Deployment** | Local first | N/A | Can deploy to VPS in Phase 2 |

**Total MVP Cost:** $0 ✅

### 7.2 Dependencies
**Existing (already installed):**
- Flask 3.1.2
- NumPy 2.2.6
- Pandas 2.3.3
- pytest 8.4.2
- PyYAML
- python-Levenshtein

**New (to be installed Week 1):**
- **mishkal** - Arabic text diacritization
- **pytest-cov** - Code coverage reporting

**System (to be installed Week 1):**
- **espeak-ng** - TTS audio generation (`sudo apt install espeak-ng`)

### 7.3 File Structure
```
ArabicTTS/
├── app.py                          # Flask web app (existing)
├── src/
│   ├── main.py                     # Main processor (existing, needs fixes)
│   ├── core/
│   │   ├── syllabifier.py          # ⚠️ FIX REQUIRED - broken algorithm
│   │   ├── gemination.py           # ❌ CREATE Week 1
│   │   ├── sun_letters.py          # ❌ CREATE Week 2  
│   │   ├── emphatic.py             # ❌ CREATE Week 2
│   │   ├── diacritizer.py          # ❌ CREATE Week 1
│   │   └── ipa_mapper.py           # ⚠️ ENHANCE - improve accuracy
│   ├── integrations/
│   │   └── espeak.py               # ❌ CREATE Week 1
│   └── utils/
│       └── (existing utilities)
├── data/
│   ├── dictionaries/
│   │   ├── masterTTS.json          # ✅ EXISTS (19,581 lines)
│   │   └── syllable_patterns.json  # ❌ CREATE Week 1
│   └── test_cases/
│       └── mvp_examples.txt        # ❌ CREATE Week 1 (10 examples)
├── tests/
│   ├── unit/
│   │   ├── test_syllabifier.py     # ⚠️ FIX - currently failing
│   │   ├── test_gemination.py      # ❌ CREATE Week 1
│   │   ├── test_sun_letters.py     # ❌ CREATE Week 2
│   │   ├── test_diacritizer.py     # ❌ CREATE Week 1
│   │   └── test_espeak.py          # ❌ CREATE Week 1
│   └── integration/
│       └── test_mvp_pipeline.py    # ❌ CREATE Week 1
└── docs/                           # ✅ EXISTS (comprehensive docs)
```

### 7.4 Constraints & Limitations
**Technical Constraints:**
- Processing speed: <60 seconds per 1,000 words (not critical for MVP)
- Audio quality: MOS 3.0-3.5 (intelligible, not production-quality)
- Diacritization accuracy: ~84% (mishkal limitation, acceptable for MVP)
- Egyptian Arabic only: Limited by masterTTS.json completeness

**Resource Constraints:**
- Zero budget for MVP (all free/OSS tools)
- Single developer (no team)
- 6-week timeline (flexible +1-2 weeks if needed)

**Known Limitations:**
- eSpeak NG audio quality is robotic (acceptable, upgradeable later)
- mishkal diacritization has ~16% error rate (acceptable for MVP)
- No prosody modeling (monotone speech, acceptable for MVP)
- Manual testing required (no automated audio quality metrics yet)

### 7.5 Integration Points
**Current Integrations:**
- Flask ↔ Processing pipeline (existing)
- Processing pipeline ↔ masterTTS.json (existing, needs enhancement)

**New Integrations (Week 1):**
- Processing pipeline ↔ mishkal (diacritization)
- Processing pipeline ↔ eSpeak NG (audio generation)

**Future Integrations (Phase 2+):**
- Coqui TTS (better audio quality)
- REST API (programmatic access)
- PostgreSQL (user data, usage tracking)

### 7.6 Suggested Technical Approach

**Week 1 Implementation Order:**
1. **Install mishkal** - Test on 10 examples first
2. **Fix syllabification** - Algorithm is broken (returns "UNKNOWN")
3. **Create syllable_patterns.json** - Define Egyptian Arabic patterns
4. **Implement gemination** - Highest priority phonological rule
5. **Install eSpeak NG** - Enable audio output
6. **End-to-end test** - Verify full pipeline works

**Testing Strategy:**
- Unit tests for each new component (>80% coverage)
- Integration test for full pipeline
- Manual validation with 10 Egyptian Arabic examples
- Native speaker review (if available)

**Risk Mitigation:**
- Start with diacritization to unblock real-world text testing
- Timebox syllabification fix to 2 days (simplify if needed)
- Keep gemination implementation simple (basic shadda detection first)
- Test audio output early (Day 4) to ensure eSpeak works

---

## 8. Success Metrics

### Technical Metrics (Primary)
| Metric | Target | Measurement Method | Priority |
|--------|--------|-------------------|----------|
| Syllabification accuracy | >95% | Manual review of 50 examples | 🔴 Critical |
| IPA generation accuracy | >90% | Expert/native speaker review of 100 words | 🔴 Critical |
| Gemination detection | 100% | Automated tests (shadda is explicit) | 🔴 Critical |
| Sun letter assimilation | 100% | Automated tests (20 examples) | 🔴 Critical |
| Test pass rate | 100% | `pytest tests/` | 🔴 Critical |
| Pronunciation errors | <10% | Native speaker review | 🟡 High |

### Process Metrics (Secondary)
| Metric | Target | Measurement Method | Priority |
|--------|--------|-------------------|----------|
| Processing speed | <60 sec per 1K words | Benchmark on test corpus | 🟢 Medium |
| Audio generation | Works for 10 examples | Manual testing | 🔴 Critical |
| Code coverage | >80% | `pytest --cov` | 🟡 High |
| Diacritization accuracy | >80% | Compare with manual diacritization | 🟡 High |

### Deliverables Metrics
| Deliverable | Target | Validation | Priority |
|-------------|--------|------------|----------|
| Working code | All components functional | End-to-end test passes | 🔴 Critical |
| Test suite | Unit + integration tests | Tests pass | 🔴 Critical |
| Test dataset | 10 Egyptian Arabic examples | File exists | 🔴 Critical |
| Results report | Document findings | Report written | 🟡 High |
| Demo presentation | 5-slide deck | Slides created | 🟢 Medium |

### User Validation Metrics (Aspirational)
| Metric | Target | Measurement Method | Priority |
|--------|--------|-------------------|----------|
| User preference | >60% prefer this vs Google TTS | A/B test (5-10 users) | 🟡 High |
| MOS score | >3.5/5.0 | User rating survey | 🟡 High |
| User satisfaction | >70% satisfied | Post-test survey | 🟢 Medium |

**Note:** User validation metrics are aspirational - if time permits, recruit 5-10 native Egyptian Arabic speakers for validation.

---

## 9. Open Questions

### Technical Questions
**Q1:** Should we create a comprehensive IPA validation tool to systematically test all phoneme mappings?  
**Status:** Open - defer to Phase 2 if time-constrained

**Q2:** How should we handle edge cases like foreign words (English/French) in Arabic text?  
**Status:** Open - for now, pass them through as-is, handle in Phase 2

**Q3:** Should we implement caching for frequently-used words to improve performance?  
**Status:** Open - not needed for MVP, consider in Phase 2

**Q4:** What's the best way to validate emphatic spread across syllable boundaries?  
**Status:** Open - needs linguistic research, may simplify for MVP

### Process Questions
**Q5:** Who can we recruit as native Egyptian Arabic speakers for validation?  
**Status:** Open - explore Arabic-speaking communities, Reddit, language exchange platforms

**Q6:** Should we create a standardized evaluation rubric for pronunciation quality?  
**Status:** Open - defer to Phase 2, use informal feedback for MVP

**Q7:** How do we handle version control for masterTTS.json as it evolves?  
**Status:** Open - use git, consider semantic versioning in Phase 2

### Scope Questions
**Q8:** If Week 6 arrives and we're missing one component (e.g., emphatic spread), do we ship anyway?  
**Decision needed:** Timeline is flexible 1-2 weeks, but clarify priorities

**Q9:** Should we build a command-line interface in addition to web UI?  
**Status:** Open - defer unless needed for automated testing

**Q10:** Do we need to document the IPA notation standards we're using (IPA vs X-SAMPA)?  
**Status:** Open - good practice, add to technical documentation if time permits

---

## 10. Appendices

### A. Phonological Rules Reference

**Gemination (Shadda ّ)**
- Doubles consonant duration
- Example: مُدَّرِس [mudːaris] (teacher)
- Must process FIRST before other rules

**Sun Letter Assimilation**
- /al/ + sun letter → gemination
- Sun letters: {ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن}
- Example: الشمس [aʃːams] (sun) not [alʃams]

**Emphatic Spread**
- Pharyngealization near emphatic consonants
- Emphatics: {ص، ض، ط، ظ، ق}
- Example: /s/ → /sˁ/ near ص

**Positional Allophones**
- Different IPA based on position (initial/medial/final)
- Example: ء → [ʔ] initial, ∅ medial (can be deleted)

### B. Test Examples (Initial Set)

**Egyptian Arabic Test Sentences:**
1. ازيك؟ (How are you?)
2. الحمد لله (Praise be to God)
3. مرحبا بيك (Welcome)
4. الشمس طالعة (The sun is out)
5. أنا جعان (I'm hungry)
6. الدرس صعب (The lesson is difficult)
7. روح بسرعة (Go quickly)
8. الولد شاطر (The boy is clever)
9. البنت جميلة (The girl is beautiful)
10. الأكل لذيذ (The food is delicious)

**Why these examples:**
- Cover gemination (shadda in several words)
- Include sun letters (الشمس، الدرس)
- Include emphatic consonants (صعب، طالعة)
- Real-world Egyptian Arabic usage
- Mix of simple and complex phonology

### C. Week 1 Task Checklist

**Day 1 (Monday)**
- [ ] Install mishkal: `pip install mishkal`
- [ ] Test mishkal on 5 examples
- [ ] Start fixing syllabification algorithm

**Day 2 (Tuesday)**
- [ ] Complete syllabification fix
- [ ] Create syllable_patterns.json
- [ ] Write syllabification tests

**Day 3 (Wednesday)**
- [ ] Implement gemination processor
- [ ] Write gemination tests
- [ ] Test gemination with 15 examples

**Day 4 (Thursday)**
- [ ] Install eSpeak NG: `sudo apt install espeak-ng`
- [ ] Create eSpeak integration layer
- [ ] Test audio generation on 3 examples

**Day 5 (Friday)**
- [ ] End-to-end pipeline test
- [ ] Create 10-example test dataset
- [ ] Fix any bugs found
- [ ] Write Week 1 progress report

### D. Glossary

**IPA (International Phonetic Alphabet)** - Standardized phonetic notation system for representing sounds of all languages

**X-SAMPA** - ASCII-based representation of IPA, easier for computer processing

**Gemination** - Doubling of consonant duration, marked by shadda (ّ) in Arabic

**Tashkeel** - Arabic diacritical marks (vowels): َ ُ ِ ْ ً ٌ ٍ

**Diacritization** - Process of adding vowels (tashkeel) to Arabic text

**Allophone** - Variant pronunciation of a phoneme based on position/context

**Emphatic consonants** - Arabic consonants pronounced with pharyngealization: ص، ض، ط، ظ، ق

**Sun letters** - Arabic letters that assimilate the /l/ in /al/: ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن

**Moon letters** - Arabic letters that don't assimilate the /l/ in /al/: remaining letters

**MOS (Mean Opinion Score)** - Standard metric for audio quality (1-5 scale, 5=excellent)

**RTL (Right-to-Left)** - Text direction for Arabic script

### E. References

**Planning Documents:**
- `/docs/planning/MVP_IMPLEMENTATION_PLAN.md` - Detailed week-by-week plan
- `/docs/planning/COMPLETE_ROADMAP.md` - All phases roadmap
- `/docs/business/BUSINESS_ANALYSIS_REPORT.md` - Market research & validation

**Technical Documentation:**
- `/docs/technical/PROJECT_DOCUMENTATION.md` - Architecture overview
- `/docs/technical/AGENT_RULES.md` - Tech stack preferences

**External Resources:**
- mishkal documentation: https://github.com/linuxscout/mishkal
- eSpeak NG documentation: https://github.com/espeak-ng/espeak-ng
- Academic papers: See Business Analysis Report Appendix A

---

## 11. Approval & Sign-off

**PRD Status:** ✅ Ready for Implementation

**Reviewed By:**
- [X] Developer (Primary User)
- [X] Technical Architect (AI Agent Analysis)
- [ ] Native Arabic Speaker (Pending - recruit for validation)

**Approved On:** October 30, 2025

**Implementation Start:** Week 1, Day 1 (Next)

**Next Steps:**
1. Review this PRD
2. Confirm understanding of requirements
3. Begin Week 1, Day 1: Install mishkal + start syllabification fix
4. Use `/docs/planning/MVP_IMPLEMENTATION_PLAN.md` for daily tasks
5. Update progress in `/docs/reports/WEEK1_PROGRESS.md`

---

**END OF PRD**

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Location:** `/tasks/0001-prd-mvp-phase1.md`
