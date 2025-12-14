# ArabicTTS - Multi-Dialect Arabic Text-to-Speech System

> **Auto-loaded context for Claude Code**
> Last Updated: November 14, 2025

---

## 🎯 Project Status

**Phase:** MVP Phase 1 Complete → Polly Integration Active
**Version:** 1.0 (Production Ready)
**Tests:** 329/329 passing (100%)
**Primary Dialect:** Modern Standard Arabic (MSA) + Egyptian Arabic (EG)

### Current Quality Metrics
- **Syllabification Accuracy:** 96.30% (target: >90%)
- **IPA Generation Accuracy:** 94.44% (target: >90%)
- **Processing Speed:** 3,059 words/second (305x faster than target)
- **Test Coverage:** 100% (329 comprehensive tests)

### Active Work
**Amazon Polly Integration** - Migrating from eSpeak NG (robotic) to Polly (neural voice) for production-quality Arabic audiobooks.
- POC validation complete ✅
- Testing long-form content (chapter-level)
- Target: Production audiobook generation

---

## 🏗️ Architecture Overview

### Processing Pipeline
```
Arabic Text
    ↓
1. PREPROCESSING
   └── Diacritization (mishkal v0.4.1) → Text Cleaning → Tokenization
    ↓
2. SYLLABIFICATION
   └── Segment into syllables (6 patterns: CV, CVC, CVV, CVCC, CVVC, V)
    ↓
3. PHONOLOGICAL PROCESSING (4 Sequential Processors)
   ├── Gemination (shadda/ّ handling)
   ├── Sun Letter Assimilation (al + sun letter → gemination)
   ├── Positional Allophones (context-dependent variants)
   └── Emphatic Spread (pharyngealization propagation)
    ↓
4. IPA GENERATION
   └── International Phonetic Alphabet output
    ↓
5. X-SAMPA CONVERSION
   └── ASCII-safe phonetic notation
    ↓
6. AUDIO SYNTHESIS
   ├── eSpeak NG (development, robotic voice)
   └── Amazon Polly (production, neural voice) ← NEW
    ↓
WAV/MP3 Output (16-bit PCM, 22050 Hz)
```

### Critical Architecture Decision
**masterTTS.json lookup happens AFTER phonological processing** - This is intentional and correct. The processing rules apply first, then dictionary provides IPA mappings for processed syllables.

---

## 📦 Project Structure

```
ArabicTTS/
├── src/                          # Source code (~5,000 LOC, 24 files)
│   ├── main.py                   # Core TTS engine (ArabicTTS class)
│   ├── core/                     # 4 phonological processors
│   │   ├── syllabifier.py        # Syllabification engine (200 LOC)
│   │   ├── gemination.py         # Shadda processor (142 LOC)
│   │   ├── sun_letters.py        # Assimilation processor (288 LOC)
│   │   ├── allophones.py         # Allophone processor (316 LOC)
│   │   └── emphatic.py           # Emphatic spread (390 LOC)
│   ├── dialects/                 # 5 dialect implementations
│   ├── integrations/             # External service wrappers
│   │   ├── espeak.py             # eSpeak NG integration (300+ LOC)
│   │   └── polly.py              # Amazon Polly integration (NEW)
│   └── utils/                    # Utilities & helpers
├── data/
│   ├── dictionaries/
│   │   └── masterTTS.json        # 1,030 phonetic entries, 5 dialects, 99% complete
│   └── test_cases/               # 25 validated test sentences
├── tests/                        # 329 comprehensive tests
│   ├── smoke/                    # 23 dependency tests
│   ├── unit/                     # 237 component tests
│   └── integration/              # 38 pipeline tests
├── docs/                         # Complete documentation (2,000+ lines)
│   ├── ARCHITECTURE.md           # HLA/HLD, data flows (750 lines)
│   ├── TECH_STACK.md             # Technology decisions (820 lines)
│   ├── TESTING.md                # Testing guide (329 tests)
│   ├── polly/                    # Polly integration docs (7 files, 65 KB)
│   ├── guides/                   # Setup & quick start
│   ├── reports/                  # MVP validation results
│   └── INDEX.md                  # Documentation hub
├── tasks/                        # Planning & task tracking
├── scripts/                      # Demo & testing scripts
└── app.py                        # Flask REST API server
```

---

## 🔧 Technology Stack

### Core Dependencies
- **Python:** 3.10+
- **Diacritization:** mishkal v0.4.1 (adds vowels/diacritics)
- **Audio Engines:**
  - eSpeak NG v1.50 (development/testing)
  - Amazon Polly (production, neural voice)
- **Web Framework:** Flask 3.0+
- **Testing:** pytest (329 tests, 100% passing)

### Key Data Assets
- **masterTTS.json:** 1,030 phonetic entries across 5 dialects
  - 199 MSA entries (production-ready)
  - 230 EG entries (most complete)
  - 99% complete (only 1 minor char missing: ٍ kasratan)
- **Test Dataset:** 25 validated Arabic sentences with reference audio

### Dialects Supported
1. **MSA (Modern Standard Arabic)** - Primary production target
2. **Egyptian (EG)** - Most tested dialect (329 tests)
3. **Gulf** - Supported
4. **Levantine** - Supported
5. **Maghrebi** - Supported

---

## 🚀 Common Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v                    # Unit tests
pytest tests/integration/ -v             # Integration tests
pytest tests/smoke/ -v                   # Dependency tests

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

### Audio Generation
```bash
# eSpeak NG (development)
PYTHONPATH=. python3 scripts/demo_full_tts.py

# Amazon Polly (production) - NEW
PYTHONPATH=. python3 scripts/test_polly_integration.py
PYTHONPATH=. python3 scripts/test_polly_long.py        # Long-form content
PYTHONPATH=. python3 scripts/test_polly_chapter.py     # Chapter-level
```

### API Server
```bash
# Start Flask development server
python3 app.py

# Server runs on http://localhost:5000
# Endpoints: /synthesize, /health
```

### Development
```bash
# Install dependencies
pip install -r requirements.txt

# Install eSpeak NG (Ubuntu/Debian)
sudo apt-get install espeak-ng

# Configure AWS for Polly
aws configure
# Required: AWS Access Key, Secret Key, Region (us-east-1)
```

---

## 📊 Amazon Polly Integration

### Why Polly?
- **Voice Quality:** Neural voice, human-like (⭐⭐⭐⭐ vs eSpeak's ⭐⭐)
- **Architecture Fit:** IPA/X-SAMPA input matches our pipeline perfectly
- **Cost Efficiency:** ~$10 per 100k-word audiobook ($16/million characters)
- **AWS Free Tier:** 5M characters/month free = 8 audiobooks/month
- **Strategic Value:** We own linguistic IP, use commodity voice service

### Integration Status
- ✅ Research complete (60+ papers, 4 comprehensive docs)
- ✅ POC validation complete
- ✅ masterTTS.json validated (99% complete)
- ✅ X-SAMPA conversion working
- 🔄 Long-form content testing (in progress)
- 📋 Production wrapper development (next)

### Key Files
- `src/integrations/polly.py` - Polly wrapper implementation
- `scripts/test_polly_*.py` - Testing scripts
- `docs/polly/` - Complete integration documentation
  - `README.md` - Overview & quick navigation
  - `TTS_TECHNOLOGY_RESEARCH_2024.md` - 60+ sources, SOTA research
  - `POLLY_INTEGRATION_ANALYSIS.md` - Technical compatibility
  - `COLLABORATIVE_DECISION_POLLY.md` - Strategic decision rationale
  - `POLLY_IMPLEMENTATION_PLAN.md` - Execution roadmap

---

## 🎓 Key Concepts

### Phonological Processors (Order Matters!)
1. **Gemination** - Doubles consonants with shadda (ّ)
2. **Sun Letters** - Assimilates /al/ + sun letter (الشمس → aʃ-ʃams not al-ʃams)
3. **Allophones** - Context-dependent phoneme variants (word-initial vs word-final)
4. **Emphatic Spread** - Pharyngealization propagation from emphatic consonants

### Syllable Patterns (Arabic)
- **CV** - Consonant + Vowel (e.g., مَ /ma/)
- **CVC** - Consonant + Vowel + Consonant (e.g., كَتَ /kat/)
- **CVV** - Consonant + Long Vowel (e.g., كاْ /kaː/)
- **CVCC** - Consonant + Vowel + 2 Consonants (e.g., بِنْت /bint/)
- **CVVC** - Consonant + Long Vowel + Consonant
- **V** - Vowel only (rare)

### IPA vs X-SAMPA
- **IPA:** International Phonetic Alphabet (Unicode, human-readable)
- **X-SAMPA:** Extended SAMPA (ASCII-safe, machine-readable)
- **Use Case:** Our pipeline generates IPA, converts to X-SAMPA for Polly input

---

## 📚 Documentation Quick Links

### Essential Reading
- **@docs/INDEX.md** - Documentation hub (complete navigation)
- **@docs/ARCHITECTURE.md** - HLA/HLD, complete system design
- **@docs/TECH_STACK.md** - Technology decisions & rationale
- **@docs/TESTING.md** - Complete testing guide (329 tests)
- **@README.md** - Project overview, features, setup

### Polly Integration
- **@docs/polly/README.md** - Polly docs overview & navigation
- **@docs/polly/QUICKSTART_GUIDE.md** - Get started with Polly
- **@docs/polly/TTS_TECHNOLOGY_RESEARCH_2024.md** - SOTA research
- **@docs/polly/COLLABORATIVE_DECISION_POLLY.md** - Strategic analysis

### Planning & Tasks
- **@tasks/TASK_LIST.md** - Complete task tracking
- **@tasks/0001-prd-mvp-phase1.md** - MVP requirements
- **@tasks/0001-prd-polly-integration.md** - Polly integration PRD
- **@docs/planning/COMPLETE_ROADMAP.md** - 6-month roadmap

### Reports & Results
- **@docs/reports/MVP_PHASE1_COMPLETE.md** - MVP completion report
- **@docs/reports/MVP_VALIDATION_RESULTS.md** - Validation results
- **@docs/DEMO_PRESENTATION.md** - 28-slide demo presentation

---

## ⚠️ Critical Notes

### DO's
✅ Run tests before committing (`pytest tests/ -v`)
✅ Use masterTTS.json for phonetic lookups (1,030 entries)
✅ Follow phonological processor order (Gemination → Sun → Allophones → Emphatic)
✅ Test with both eSpeak (dev) and Polly (prod) when available
✅ Check docs/polly/ for Polly integration guidance
✅ Use X-SAMPA for Polly input (not raw IPA)

### DON'Ts
❌ Don't skip phonological processing (each rule is essential)
❌ Don't modify processor order (architectural decision)
❌ Don't commit without running tests (329 must pass)
❌ Don't use Polly without AWS credentials configured
❌ Don't modify masterTTS.json structure (1,030 entries validated)
❌ Don't mix eSpeak and Polly outputs (use separate directories)

### Known Issues & Workarounds
- **Empty X-SAMPA:** Some inputs produce empty X-SAMPA → Use plain Arabic text as fallback (handled in polly.py)
- **Polly Neural Voices:** Zeina (Arabic) only supports standard engine, not neural (fix: use standard)
- **AWS Free Tier:** 5M chars/month for first 12 months → Monitor usage to stay within limits

---

## 🎯 Success Criteria (MVP Phase 1) - ACHIEVED ✅

| Criterion | Target | Actual | Status |
|-----------|--------|--------|--------|
| Tests Passing | >95% | 100% (329/329) | ✅ Exceeded |
| Syllabification | >90% | 96.30% | ✅ Exceeded |
| IPA Accuracy | >90% | 94.44% | ✅ Exceeded |
| Processing Speed | ≥10 w/s | 3,059 w/s | ✅ 305x faster |
| Test Dataset | 10+ sentences | 25 sentences | ✅ Exceeded |
| Documentation | Complete | 2,000+ lines | ✅ Complete |

---

## 🔄 Recent Commits (Nov 3, 2025)

```
00e0ee7 - fix: handle empty X-SAMPA by using plain Arabic text for Polly
c580f1a - docs: add POC results template and quickstart guide
df61246 - chore: mark automated POC validation tasks complete (5.1-5.7)
089dc5e - fix: use standard engine for Zeina voice (neural not supported)
0a4c5c0 - chore: mark parent task 4.0 complete
```

**Focus:** Polly integration refinement and POC validation

---

## 💡 Development Workflow

### For New Features
1. Read relevant docs (@docs/ARCHITECTURE.md, @docs/TECH_STACK.md)
2. Write tests first (TDD approach)
3. Implement feature in src/
4. Run tests (`pytest tests/ -v`)
5. Update documentation if needed
6. Commit with descriptive message

### For Bug Fixes
1. Reproduce with test case
2. Debug using existing tests
3. Fix in appropriate module (src/core/, src/integrations/, etc.)
4. Verify all 329 tests still pass
5. Document fix if non-obvious

### For Polly Integration Work
1. Check @docs/polly/ for context
2. Use test scripts (scripts/test_polly_*.py)
3. Monitor AWS costs (free tier: 5M chars/month)
4. Test with sample content before long audiobooks
5. Compare quality with eSpeak baseline

---

## 🌐 External Resources

### OneNote Documentation
**Location:** `/home/hamr/PycharmProjects/OneNote/Arabic TTS/`
**Contains:** Processing flows, research notes, issue tracking

### GitHub References
- **mishkal** - Diacritization library
- **espeak-ng** - TTS engine
- **farasapy** - NLP toolkit (reference)
- **arabic-tacotron-tts** - Neural TTS (research reference)

### AWS Polly
- **Zeina Voice:** MSA (Modern Standard Arabic), standard engine only
- **Region:** us-east-1 (recommended for Arabic)
- **Pricing:** $16/million characters (neural), $4/million (standard)
- **Free Tier:** 5M chars/month, first 12 months

---

## 📈 Next Steps (Polly Integration)

### Immediate (This Week)
- [ ] Complete long-form content testing (chapter-level)
- [ ] Validate audio quality at scale (full audiobook sample)
- [ ] Measure actual costs and performance
- [ ] Compare Polly vs eSpeak quality metrics

### Short-term (2-4 Weeks)
- [ ] Build production Polly wrapper with error handling
- [ ] Add cost monitoring and usage tracking
- [ ] Implement audio caching for repeated content
- [ ] Process complete MSA audiobook (validation)

### Medium-term (1-3 Months)
- [ ] Launch MSA audiobook production pipeline
- [ ] Add Egyptian Arabic Polly support (if available)
- [ ] Optimize cost/quality trade-offs
- [ ] Expand to additional dialects (Gulf, Levantine)

---

**For complete context:** See @KNOWLEDGE_BASE.md
**For detailed architecture:** See @docs/ARCHITECTURE.md
**For Polly integration:** See @docs/polly/README.md
**For all documentation:** See @docs/INDEX.md

---

*This file is auto-loaded by Claude Code for optimal context awareness.*
