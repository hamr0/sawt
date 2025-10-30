# Arabic TTS - MVP Implementation Plan

**Version:** 1.0  
**Date:** October 30, 2025  
**Timeline:** 6 Weeks to MVP  
**Scope:** MSA Dialect, IPA-Based Processing, Audio Output

---

## Table of Contents

1. [Processing Pipeline Overview](#1-processing-pipeline-overview)
2. [Current State Assessment](#2-current-state-assessment)
3. [Immediate Tasks (Week 1)](#3-immediate-tasks-week-1)
4. [Next Phase Tasks (Weeks 2-6)](#4-next-phase-tasks-weeks-2-6)
5. [Prerequisites & Dependencies](#5-prerequisites--dependencies)
6. [Risk Assessment Matrix](#6-risk-assessment-matrix)
7. [Success Criteria & KPIs](#7-success-criteria--kpis)
8. [Validation & Testing Plan](#8-validation--testing-plan)

---

## 1. Processing Pipeline Overview

### 1.1 Validated Processing Order

| Step | Component | Purpose | Status | Priority |
|------|-----------|---------|--------|----------|
| **0** | Dialect Selection | User selects target dialect (MSA, EG, etc.) | ✅ Working | - |
| **0.5** | **Diacritization** | Add vowels to undiacritized text | ❌ Missing | 🔴 Critical |
| **1** | Tokenization | Split text into words/chars | ✅ Working | - |
| **2** | Character Analysis | Identify position (initial/medial/final) | ✅ Working | - |
| **3** | Word Grouping | Group Arabic characters into words | ✅ Working | - |
| **4** | **Syllabification** | Segment into syllables (CV, CVC, CVCC, CVV) | ⚠️ Broken | 🔴 Critical |
| **5.1** | **Gemination** | Process shadda (ّ) - double consonant | ❌ Missing | 🔴 Critical |
| **5.2** | **Sun Letter Assimilation** | Handle /al/ + sun letter → gemination | ❌ Missing | 🔴 Critical |
| **5.3** | Positional Allophones | Apply position-dependent IPA | ⚠️ Partial | 🟡 High |
| **5.4** | **Emphatic Spread** | Pharyngealization near emphatics | ❌ Missing | 🟡 High |
| **5.5** | Context Rules | Dialect-specific adjustments | ⚠️ Partial | 🟡 High |
| **6** | IPA Mapping | Convert to IPA/X-SAMPA | ⚠️ Partial | 🟡 High |
| **7** | Prosody (Future) | Stress, intonation, pauses | ❌ Not MVP | ⚪ Low |
| **8** | **TTS Engine** | Generate audio from IPA | ❌ Missing | 🔴 Critical |

### 1.2 Component Status Legend

| Symbol | Status | Meaning |
|--------|--------|---------|
| ✅ | Working | Implementation complete and tested |
| ⚠️ | Broken/Partial | Exists but has critical bugs or incomplete |
| ❌ | Missing | Not implemented at all |
| 🔴 | Critical | Must fix for MVP |
| 🟡 | High | Important for quality |
| 🟢 | Medium | Can improve later |
| ⚪ | Low | Post-MVP enhancement |

---

## 2. Current State Assessment

### 2.1 What We HAVE

| Component | File/Location | Completeness | Quality | Notes |
|-----------|---------------|--------------|---------|-------|
| Flask Web App | `app.py` | 90% | Good | Working UI, API endpoints |
| Web Interface | `templates/index.html` | 90% | Good | Dialect selection, JSON display |
| Master Dictionary | `data/dictionaries/masterTTS.json` | 60% | Good | 19,581 lines, EG complete, MSA partial |
| Tokenization | `src/main.py` - `tokenize()` | 95% | Good | Splits text properly |
| Character Analysis | `src/main.py` - `analyze_char()` | 95% | Good | Position detection works |
| Word Grouping | `src/main.py` - `group_arabic_words()` | 95% | Good | Groups Arabic chars correctly |
| Test Structure | `tests/unit/`, `tests/integration/` | 40% | Fair | Test files exist, many fail |
| Documentation | `README.md`, `PROJECT_DOCUMENTATION.md` | 85% | Excellent | Comprehensive docs |

### 2.2 What's BROKEN

| Component | File/Location | Problem | Impact | Effort to Fix |
|-----------|---------------|---------|--------|---------------|
| **Syllabification** | `src/main.py` - `ArabicSyllabifier` | Returns "UNKNOWN" patterns | 🔴 Critical - breaks phonology | 3-5 days |
| **syllable_patterns.json** | `data/dictionaries/` | File doesn't exist | 🔴 Critical - tests fail | 1 day |
| **IPA Mapping** | `src/main.py` - `map_to_ipa()` | Incomplete logic, missing positional rules | 🟡 High - poor quality | 2-3 days |
| **Positional Rules** | N/A | Not systematically applied | 🟡 High - wrong pronunciation | 2-3 days |

### 2.3 What's MISSING (Critical for MVP)

| Component | Purpose | Where to Add | Effort | Blocks |
|-----------|---------|--------------|--------|--------|
| **Diacritization Module** | Add vowels to text | New: `src/core/diacritizer.py` | 2 days | Real-world text processing |
| **Gemination Processor** | Handle shadda (ّ) | New: `src/core/gemination.py` | 2 days | Phonological rules |
| **Sun Letter Module** | /al/ assimilation | New: `src/core/sun_letters.py` | 2 days | Pronunciation accuracy |
| **Emphatic Spread** | Pharyngealization | New: `src/core/emphatic.py` | 2 days | Dialect authenticity |
| **TTS Integration** | Audio output | New: `src/integrations/espeak.py` | 1 day | End-to-end testing |
| **Phonological Rules Engine** | Orchestrate rules in order | New: `src/core/phonological_rules.py` | 3 days | Core processing |
| **Test Dataset** | Validation examples | New: `data/test_cases/mvp_test_set.txt` | 2 days | Quality validation |

---

## 3. Immediate Tasks (Week 1)

### 3.1 Week 1 Overview

**Goal:** Fix broken components and establish working baseline  
**Outcome:** Processing pipeline works end-to-end (IPA generation + audio)  
**Success Criteria:** Tests pass, can process 10 example sentences

### 3.2 Task Breakdown

| Day | Task | Owner | Files Changed | Hours | Status |
|-----|------|-------|---------------|-------|--------|
| **Mon** | Fix syllabification algorithm | Dev | `src/main.py`, `src/core/syllabifier.py` | 6-8h | 🔴 Not Started |
| **Mon-Tue** | Create syllable_patterns.json | Dev | `data/dictionaries/syllable_patterns.json` | 4h | 🔴 Not Started |
| **Tue** | Write syllabification tests | Dev | `tests/unit/test_syllabifier.py` | 3h | 🔴 Not Started |
| **Wed** | Implement gemination processor | Dev | `src/core/gemination.py` | 6-8h | 🔴 Not Started |
| **Wed** | Write gemination tests | Dev | `tests/unit/test_gemination.py` | 2h | 🔴 Not Started |
| **Thu** | Integrate espeak-ng | Dev | `src/integrations/espeak.py` | 4h | 🔴 Not Started |
| **Thu-Fri** | End-to-end pipeline test | Dev | `tests/integration/test_mvp_pipeline.py` | 4h | 🔴 Not Started |
| **Fri** | Create 10-example test dataset | Dev | `data/test_cases/mvp_examples.txt` | 2h | 🔴 Not Started |
| **Fri** | Documentation updates | Dev | `docs/WEEK1_PROGRESS.md` | 1h | 🔴 Not Started |

### 3.3 Detailed Task Specifications

#### Task 1.1: Fix Syllabification Algorithm

**File:** `src/main.py` (lines 11-60) - `ArabicSyllabifier` class

**Current Problem:**
```python
# Current code returns:
{
  "syllable": "مرحبا",
  "pattern": "UNKNOWN",  # ❌ This is wrong!
  "ipa": "..."
}
```

**Required Fix:**
```python
# Should return proper patterns:
{
  "syllable": "مَرْ",
  "pattern": "CVC",  # ✅ Correct!
  "ipa": "mar"
}
```

**Acceptance Criteria:**
- [ ] Correctly identifies CV patterns (e.g., "مَ" → CV)
- [ ] Correctly identifies CVC patterns (e.g., "مَرْ" → CVC)
- [ ] Correctly identifies CVCC patterns (e.g., "شَمْس" → CVCC)
- [ ] Correctly identifies CVV patterns (e.g., "كاْ" → CVV)
- [ ] No "UNKNOWN" patterns for valid syllables
- [ ] Unit tests pass (10 examples minimum)

**Dependencies:**
- syllable_patterns.json must exist
- Understanding of Arabic vowel markers (َ ُ ِ ْ ّ ا و ي)

**Risk Assessment:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Algorithm complexity | Medium | High | Start with simple rule-based approach |
| Edge cases (sukun, tanween) | High | Medium | Document unsupported cases for Phase 2 |
| Test coverage insufficient | Medium | Medium | Create 50+ test cases |

**KPIs:**
- **Syllabification Accuracy:** Target >95%
- **Processing Speed:** <100ms per word
- **Test Pass Rate:** 100% of basic patterns

---

#### Task 1.2: Create syllable_patterns.json

**File:** `data/dictionaries/syllable_patterns.json` (NEW)

**Purpose:** Define valid syllable structures per dialect

**Content Structure:**
```json
{
  "MSA": {
    "CV": {
      "structure": "consonant + short_vowel",
      "examples": ["مَ", "لِ", "بُ"],
      "ipa_pattern": "C V",
      "allowed_positions": ["initial", "medial", "final"],
      "constraints": {}
    },
    "CVC": {
      "structure": "consonant + vowel + consonant",
      "examples": ["مَنْ", "كَتَ", "بِنْ"],
      "ipa_pattern": "C V C",
      "allowed_positions": ["initial", "medial", "final"],
      "constraints": {
        "final_consonant_can_be_geminated": true
      }
    },
    "CVCC": {
      "structure": "consonant + vowel + consonant + consonant",
      "examples": ["شَمْس", "كَتْب"],
      "ipa_pattern": "C V C C",
      "allowed_positions": ["final"],
      "constraints": {
        "second_consonant_must_be": ["geminate", "sun_letter", "valid_cluster"]
      }
    },
    "CVV": {
      "structure": "consonant + long_vowel",
      "examples": ["كا", "لِي", "بُو"],
      "ipa_pattern": "C V:",
      "allowed_positions": ["initial", "medial", "final"],
      "constraints": {}
    }
  },
  "EG": {
    "CV": { /* Similar to MSA */ },
    "CVC": { /* Similar with dialect variations */ },
    "CVCC": { /* Dialect-specific constraints */ },
    "CVV": { /* Similar to MSA */ }
  }
}
```

**Acceptance Criteria:**
- [ ] Valid JSON format
- [ ] Contains all 4 patterns (CV, CVC, CVCC, CVV)
- [ ] Includes MSA and EG dialects
- [ ] Has examples for each pattern
- [ ] Defines constraints clearly
- [ ] Validated against `tests/unit/test_syllabifier.py`

**Effort:** 4 hours (2h creation + 2h testing)

**Dependencies:** None (can start immediately)

**KPIs:**
- **Completeness:** All 4 patterns defined for 2 dialects
- **Validation:** Schema validates correctly
- **Test Integration:** Tests can load and parse file

---

#### Task 1.3: Implement Gemination Processor

**File:** `src/core/gemination.py` (NEW)

**Purpose:** Detect and process shadda (ّ) marks to indicate consonant doubling

**Implementation Spec:**

```python
# src/core/gemination.py

class GeminationProcessor:
    """
    Handles gemination (consonant doubling) marked by shadda (ّ)
    MUST BE APPLIED FIRST before other phonological rules
    """
    
    def __init__(self, dialect: str):
        self.dialect = dialect
        self.shadda_mark = 'ّ'
    
    def detect_gemination(self, word: str) -> list:
        """
        Detect all gemination positions in word
        
        Args:
            word: Arabic word with diacritics
        
        Returns:
            List of (position, consonant) tuples
        
        Example:
            Input: "مُدَّرِس"
            Output: [(2, 'د')]  # Position 2 has shadda on د
        """
        pass
    
    def apply_gemination(self, syllables: list) -> list:
        """
        Mark geminated consonants in IPA representation
        
        Args:
            syllables: List of syllable dictionaries
        
        Returns:
            Modified syllables with gemination marks
        
        Example:
            Input: [{"syllable": "مُدْ", "ipa": "mud"}, 
                    {"syllable": "دَ", "ipa": "da"}]
            Output: [{"syllable": "مُدْ", "ipa": "mud"}, 
                     {"syllable": "دَ", "ipa": "dːa"}]  # Note the ː
        """
        pass
    
    def process_word(self, word_data: dict) -> dict:
        """
        Main processing function for a single word
        
        Args:
            word_data: Word dictionary with syllables
        
        Returns:
            Modified word_data with gemination applied
        """
        pass
```

**Test Cases Required:**

| Test | Input | Expected Output | Purpose |
|------|-------|-----------------|---------|
| Simple gemination | مُدَّرِس | [mud][dːa][ris] | Basic shadda detection |
| No gemination | مُدَرِس | [mu][da][ris] | Control case |
| Multiple geminations | مُعَلِّمٌ | [muʕalːimun] | Multiple shaddas |
| Initial position | ّلا | [Invalid] | Shadda can't be initial |
| With sun letter | الشَّمْس | [aʃːams] | Interaction test |

**Acceptance Criteria:**
- [ ] Detects shadda (ّ) correctly in all positions
- [ ] Marks preceding consonant as geminated [C:]
- [ ] Handles multiple shaddas in one word
- [ ] Returns error for invalid shadda positions
- [ ] Unit tests pass (15 test cases minimum)
- [ ] Integration with syllabification works

**Dependencies:**
- Syllabification must work first
- Understanding of IPA gemination notation (ː symbol)

**Risk Assessment:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shadda position detection | Low | High | Use regex patterns, extensive testing |
| IPA notation inconsistency | Medium | Medium | Define standard in constants |
| Edge cases with other diacritics | Medium | Low | Document and test combinations |

**KPIs:**
- **Detection Accuracy:** 100% (shadda is explicit marker)
- **Processing Speed:** <10ms per word
- **Test Coverage:** >95% code coverage

**Effort:** 6-8 hours (4h implementation + 3h testing + 1h documentation)

---

#### Task 1.4: Integrate espeak-ng for Audio Output

**File:** `src/integrations/espeak.py` (NEW)

**Purpose:** Generate audio from IPA representation for validation

**Implementation Spec:**

```python
# src/integrations/espeak.py

import subprocess
import os
from pathlib import Path
from typing import Optional

class ESpeakIntegration:
    """
    Integration with eSpeak NG for audio generation
    Uses IPA input mode for precise pronunciation control
    """
    
    def __init__(self, voice: str = "ar", speed: int = 175):
        """
        Initialize eSpeak integration
        
        Args:
            voice: Language voice code (ar for Arabic)
            speed: Speech speed (words per minute)
        """
        self.voice = voice
        self.speed = speed
        self.check_installation()
    
    def check_installation(self) -> bool:
        """
        Verify espeak-ng is installed
        
        Returns:
            True if installed, raises Exception otherwise
        """
        pass
    
    def ipa_to_audio(self, ipa: str, output_file: str) -> bool:
        """
        Convert IPA string to audio file
        
        Args:
            ipa: IPA/X-SAMPA phonetic string
            output_file: Path to output WAV file
        
        Returns:
            True if successful, False otherwise
        
        Example:
            >>> espeak = ESpeakIntegration()
            >>> espeak.ipa_to_audio("[ʔalħamdu lillɑːh]", "test.wav")
            True
        """
        pass
    
    def text_to_ipa_to_audio(self, text: str, dialect: str, 
                             output_file: str) -> bool:
        """
        Full pipeline: Arabic text → IPA → Audio
        
        Args:
            text: Arabic text
            dialect: Dialect code (MSA, EG, etc.)
            output_file: Path to output WAV file
        
        Returns:
            True if successful
        """
        # 1. Process text through your pipeline
        # 2. Get IPA representation
        # 3. Generate audio
        pass
```

**Installation Instructions:**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install espeak-ng

# Test installation
espeak-ng --version

# Test Arabic voice
espeak-ng -v ar "مرحبا" -w test.wav

# Test with IPA input (this is what we'll use)
espeak-ng -v ar --ipa="[marħaban]" -w test_ipa.wav
```

**Acceptance Criteria:**
- [ ] Can detect if espeak-ng is installed
- [ ] Can generate WAV file from IPA string
- [ ] Can process full text through pipeline to audio
- [ ] Audio file is valid and playable
- [ ] Integration test works end-to-end
- [ ] Error handling for missing installation

**Test Cases:**

| Test | Input | Expected Output | Validation |
|------|-------|-----------------|------------|
| Simple IPA | [marħaban] | test1.wav | File exists, duration >0 |
| MSA sentence | السلام عليكم | test2.wav | Audible, correct pronunciation |
| EG dialect | ازيك | test3.wav | Audible, Egyptian pronunciation |
| Empty input | "" | Error | Raises exception |
| Invalid IPA | [xyz123] | Error/Warning | Handles gracefully |

**Dependencies:**
- espeak-ng installed on system
- Working IPA generation pipeline
- File system write access

**Risk Assessment:**

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| espeak-ng not installed | High | High | Add installation check + docs |
| IPA format incompatibility | Medium | Medium | Test with various IPA strings |
| Audio quality poor | High | Low | Expected for MVP, upgrade later |
| File path issues | Low | Low | Use pathlib, handle errors |

**KPIs:**
- **Success Rate:** 100% for valid IPA
- **Audio Generation Speed:** <5 seconds per sentence
- **File Size:** Reasonable (<1MB per minute of audio)

**Effort:** 4 hours (2h implementation + 1h testing + 1h documentation)

---

### 3.4 Week 1 Risks

| Risk | Impact | Probability | Mitigation Strategy |
|------|--------|-------------|---------------------|
| Syllabification more complex than expected | 🔴 High | Medium | Timebox to 2 days, simplify if needed |
| Gemination edge cases break system | 🟡 Medium | Medium | Start with basic cases, add complexity iteratively |
| espeak-ng installation issues | 🟡 Medium | High | Document installation, provide Docker alternative |
| Not enough time to complete all tasks | 🔴 High | Medium | Prioritize: syllabification > gemination > espeak |
| Tests reveal more bugs than expected | 🟡 Medium | High | Allocate 20% buffer time for bug fixes |

### 3.5 Week 1 Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Tests Passing** | 100% of core tests | `pytest tests/unit/ -v` |
| **Syllabification Accuracy** | >95% | Manual review of 50 examples |
| **Gemination Detection** | 100% | Test suite with 15 examples |
| **Audio Generation** | Works for 10 examples | Manual listening test |
| **Code Quality** | No critical bugs | Code review + linting |
| **Documentation** | All tasks documented | Review README updates |

### 3.6 Week 1 Deliverables Checklist

- [ ] Fixed syllabification algorithm
- [ ] Created syllable_patterns.json
- [ ] Implemented gemination processor
- [ ] Integrated espeak-ng
- [ ] All unit tests passing
- [ ] 10-example test dataset created
- [ ] End-to-end pipeline works
- [ ] Audio files generated for validation
- [ ] WEEK1_PROGRESS.md written
- [ ] Git commits with clear messages

---

## 4. Next Phase Tasks (Weeks 2-6)

### 4.1 Phase Overview

| Week | Focus Area | Goal | Key Deliverables |
|------|------------|------|------------------|
| **Week 2** | Phonological Rules | Implement sun letter + emphatic | 2 rule processors, tests |
| **Week 3** | Diacritization | Handle real-world text | Mishkal integration, testing |
| **Week 4** | IPA Refinement | Improve accuracy | Positional rules, quality tests |
| **Week 5** | Testing & Dataset | Validate quality | 100-example dataset, A/B test |
| **Week 6** | Integration & Polish | Prepare for demo | Bug fixes, documentation, demo |

### 4.2 Week 2: Phonological Rules

#### Goals
- Implement sun letter assimilation
- Implement emphatic spread
- Orchestrate rule application order

#### Tasks Table

| Day | Task | Files | Hours | Priority |
|-----|------|-------|-------|----------|
| Mon | Design phonological rules engine | `src/core/phonological_rules.py` | 4h | 🔴 Critical |
| Mon-Tue | Implement sun letter assimilation | `src/core/sun_letters.py` | 6h | 🔴 Critical |
| Wed | Write sun letter tests | `tests/unit/test_sun_letters.py` | 3h | 🔴 Critical |
| Wed-Thu | Implement emphatic spread | `src/core/emphatic.py` | 6h | 🟡 High |
| Thu | Write emphatic tests | `tests/unit/test_emphatic.py` | 3h | 🟡 High |
| Fri | Integration testing | `tests/integration/test_phonology.py` | 4h | 🔴 Critical |
| Fri | Code review & refactoring | All rule files | 2h | 🟢 Medium |

#### Success Criteria

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| Sun letter accuracy | 100% | 20 test examples |
| Emphatic spread accuracy | >90% | 15 test examples |
| Rule ordering correct | 100% | Integration test |
| Processing speed | <200ms per sentence | Benchmark |
| Code coverage | >85% | pytest-cov |

#### Risks

| Risk | Mitigation |
|------|------------|
| Rule interactions cause bugs | Test combinations systematically |
| Performance degradation | Profile code, optimize hotspots |
| Dialect differences | Keep rules modular per dialect |

---

### 4.3 Week 3: Diacritization Integration

#### Goals
- Integrate mishkal for vowel prediction
- Handle undiacritized text
- Test with real-world examples

#### Tasks Table

| Day | Task | Files | Hours | Priority |
|-----|------|-------|-------|----------|
| Mon | Research mishkal API | Documentation | 2h | 🔴 Critical |
| Mon | Install & test mishkal | System setup | 2h | 🔴 Critical |
| Tue | Create diacritization wrapper | `src/core/diacritizer.py` | 4h | 🔴 Critical |
| Tue-Wed | Integrate into pipeline | `src/main.py` | 6h | 🔴 Critical |
| Wed-Thu | Test with Wikipedia articles | Test data collection | 6h | 🟡 High |
| Thu | Error handling & edge cases | All diacritizer code | 4h | 🟡 High |
| Fri | Performance optimization | Caching, batching | 3h | 🟢 Medium |
| Fri | Documentation | `docs/DIACRITIZATION.md` | 2h | 🟢 Medium |

#### Dependencies

| Dependency | Status | Action |
|------------|--------|--------|
| mishkal package | External | Install: `pip install mishkal` |
| Python 3.10+ | ✅ Installed | None |
| Test Arabic text corpus | Create | Download Wikipedia samples |
| Baseline accuracy metrics | Define | Set targets (>80%) |

#### Success Criteria

| Metric | Target | Test Method |
|--------|--------|-------------|
| Diacritization accuracy | >85% | Compare with manual diacritization |
| Processing speed | <3 sec per paragraph | Benchmark on 100 paragraphs |
| Integration stability | No crashes | Process 1000 sentences |
| Error handling | Graceful degradation | Test malformed input |

---

### 4.4 Week 4: IPA Refinement

#### Goals
- Improve IPA mapping accuracy
- Apply positional allophone rules
- Enhance dialect-specific rules

#### Tasks Table

| Day | Task | Files | Hours | Priority |
|-----|------|-------|-------|----------|
| Mon | Audit IPA mapping quality | Code review | 3h | 🔴 Critical |
| Mon-Tue | Implement positional rules | `src/core/positional_rules.py` | 8h | 🔴 Critical |
| Wed | Enhance masterTTS.json usage | `src/core/ipa_mapper.py` | 6h | 🔴 Critical |
| Thu | Dialect-specific adjustments | `src/dialects/msa.py` | 4h | 🟡 High |
| Thu | Write IPA validation tests | `tests/unit/test_ipa_mapper.py` | 4h | 🟡 High |
| Fri | Manual quality review | Listen to outputs | 4h | 🟡 High |
| Fri | Bug fixes | Various files | 3h | 🟢 Medium |

#### Quality Metrics

| Aspect | Target | Measurement |
|--------|--------|-------------|
| IPA accuracy | >95% | Expert review of 100 words |
| Position handling | 100% | Initial/medial/final all correct |
| Dialect consistency | >90% | No mixing of dialect features |
| Edge cases handled | >80% | Test unusual words |

---

### 4.5 Week 5: Testing & Dataset Creation

#### Goals
- Create comprehensive test dataset
- Conduct A/B testing vs Google TTS
- Measure quality metrics

#### Tasks Table

| Day | Task | Deliverables | Hours | Priority |
|-----|------|--------------|-------|----------|
| Mon | Create 100-example dataset | `data/test_cases/mvp_test_set.txt` | 6h | 🔴 Critical |
| Tue | Generate audio for all examples | 100 WAV files | 4h | 🔴 Critical |
| Tue-Wed | Google TTS comparison baseline | Comparison audio files | 6h | 🔴 Critical |
| Wed-Thu | Recruit 5-10 beta testers | User list | 4h | 🟡 High |
| Thu-Fri | Conduct A/B listening test | Survey results | 8h | 🔴 Critical |
| Fri | Analyze results | Report | 4h | 🔴 Critical |

#### Test Dataset Specification

| Category | Count | Examples | Purpose |
|----------|-------|----------|---------|
| Simple sentences | 30 | "السلام عليكم" | Basic validation |
| Complex sentences | 20 | Long sentences with subordinate clauses | Stress test |
| Common words | 20 | Frequently used words | Coverage |
| Edge cases | 10 | Numbers, loan words, names | Robustness |
| Dialect features | 10 | MSA-specific features | Dialect accuracy |
| Gemination examples | 10 | Words with shadda | Rule validation |

#### A/B Testing Protocol

| Step | Action | Participants | Duration |
|------|--------|--------------|----------|
| 1. Preparation | Generate both audio sets | - | 1 day |
| 2. Randomization | Blind test ordering | - | 2 hours |
| 3. Listening test | Participants rate 1-5 | 5-10 people | 3 days |
| 4. Feedback collection | Open-ended comments | All | Continuous |
| 5. Analysis | Statistical significance | - | 4 hours |

#### Success Criteria

| Metric | Target | Validation |
|--------|--------|------------|
| User preference | >60% prefer your system | A/B test results |
| MOS score | >3.5/5.0 | Average rating |
| Pronunciation errors | <5% | Expert review |
| User satisfaction | >70% satisfied | Survey |

---

### 4.6 Week 6: Integration & Polish

#### Goals
- Fix bugs found in testing
- Polish documentation
- Prepare demo/presentation

#### Tasks Table

| Day | Task | Deliverables | Hours | Priority |
|-----|------|--------------|-------|----------|
| Mon | Bug triage & prioritization | Bug list | 2h | 🔴 Critical |
| Mon-Tue | Fix critical bugs | Code fixes | 10h | 🔴 Critical |
| Wed | Fix medium priority bugs | Code fixes | 6h | 🟡 High |
| Wed-Thu | Documentation polish | Updated docs | 8h | 🟡 High |
| Thu | Create demo examples | Demo materials | 4h | 🔴 Critical |
| Fri | Final testing | Test report | 4h | 🔴 Critical |
| Fri | MVP completion review | Report | 2h | 🔴 Critical |

#### Documentation Updates Required

| Document | Updates Needed | Status |
|----------|----------------|--------|
| README.md | Add MVP results, usage examples | 🔴 Required |
| PROJECT_DOCUMENTATION.md | Update with implementation details | 🟡 Nice to have |
| API_REFERENCE.md | Document all functions | 🔴 Required |
| TESTING_GUIDE.md | How to run tests, interpret results | 🟡 Nice to have |
| MVP_RESULTS.md | A/B test results, metrics achieved | 🔴 Required |

#### Demo Preparation

| Element | Description | Duration |
|---------|-------------|----------|
| Slide deck | 10-15 slides explaining approach | 2 hours |
| Live demo | Process text → hear audio | 1 hour |
| Comparison demo | Side-by-side with Google TTS | 1 hour |
| Results presentation | Show metrics, user feedback | 1 hour |

---

## 5. Prerequisites & Dependencies

### 5.1 Development Environment

| Requirement | Status | Installation Command | Verification |
|-------------|--------|---------------------|-------------|
| Python 3.10+ | ✅ Installed | - | `python3 --version` |
| pip/pip3 | ✅ Installed | - | `pip3 --version` |
| git | ✅ Installed | - | `git --version` |
| espeak-ng | ❌ Not Installed | `sudo apt install espeak-ng` | `espeak-ng --version` |
| Text editor/IDE | ✅ Available | - | VSCode, PyCharm, etc. |

### 5.2 Python Dependencies

| Package | Version | Status | Installation | Purpose |
|---------|---------|--------|--------------|---------|
| Flask | 3.1.2 | ✅ Installed | `pip install flask` | Web application |
| NumPy | 2.2.6 | ✅ Installed | `pip install numpy` | Numerical operations |
| Pandas | 2.3.3 | ✅ Installed | `pip install pandas` | Data manipulation |
| PyYAML | (system) | ✅ Installed | `pip install pyyaml` | Config files |
| pytest | 8.4.2 | ✅ Installed | `pip install pytest` | Testing |
| python-Levenshtein | 0.27.1 | ✅ Installed | `pip install python-Levenshtein` | String matching |
| **mishkal** | TBD | ❌ Not Installed | `pip install mishkal` | Diacritization |
| **pytest-cov** | TBD | ❌ Not Installed | `pip install pytest-cov` | Code coverage |

### 5.3 Data Files

| File | Location | Status | Size | Purpose |
|------|----------|--------|------|---------|
| masterTTS.json | `data/dictionaries/` | ✅ Exists | 19,581 lines | Phonetic dictionary |
| **syllable_patterns.json** | `data/dictionaries/` | ❌ Missing | ~200 lines | Syllable rules |
| MSA test samples | `data/test_cases/` | ✅ Exists | Small | Testing |
| EG test samples | `data/test_cases/` | ✅ Exists | Small | Testing |
| **MVP test set** | `data/test_cases/` | ❌ Missing | 100 examples | Quality validation |

### 5.4 Knowledge Dependencies

| Knowledge Area | Status | Action Required |
|----------------|--------|-----------------|
| Arabic phonology basics | ✅ Understood | - |
| IPA notation | ✅ Understood | - |
| Gemination concepts | ✅ Understood | - |
| Sun letter rules | ✅ Understood | - |
| **mishkal API** | ❌ Unknown | Read documentation |
| **espeak-ng IPA mode** | ❌ Unknown | Test and document |
| Python testing best practices | ⚠️ Partial | Review pytest docs |

### 5.5 External Resources

| Resource | Type | Status | Action |
|----------|------|--------|--------|
| GitHub starred repos | Reference | ✅ Available | Review as needed |
| Academic papers | Reference | ✅ Available | Cite in docs |
| Arabic text corpus | Data | ⚠️ Need more | Download Wikipedia articles |
| Native speaker consultant | Human | ❌ Not engaged | Recruit for testing |

---

## 6. Risk Assessment Matrix

### 6.1 Technical Risks

| Risk | Probability | Impact | Severity | Mitigation Strategy | Owner |
|------|-------------|--------|----------|---------------------|-------|
| Syllabification algorithm more complex than estimated | Medium | High | 🔴 **Critical** | Timebox to 2 days; use simplified approach if needed | Dev |
| mishkal integration breaks pipeline | Medium | High | 🔴 **Critical** | Test thoroughly; have fallback (skip diacritization for MVP) | Dev |
| espeak-ng audio quality too poor | High | Medium | 🟡 **High** | Expected for MVP; plan Coqui TTS upgrade for Phase 2 | Dev |
| Gemination edge cases break system | Medium | Medium | 🟡 **High** | Start with common cases; document unsupported edge cases | Dev |
| Performance bottlenecks in processing | Low | Medium | 🟢 **Medium** | Profile code; optimize after MVP works | Dev |
| Test coverage insufficient | Medium | Medium | 🟡 **High** | Allocate 30% of time to testing; use TDD approach | Dev |
| Dialect-specific rules conflict | Low | High | 🟡 **High** | Keep rules strictly separated per dialect; namespace carefully | Dev |
| Master dictionary incomplete for MSA | Medium | High | 🔴 **Critical** | Focus on most common 1000 words first; expand iteratively | Dev |

### 6.2 Resource Risks

| Risk | Probability | Impact | Severity | Mitigation Strategy |
|------|-------------|--------|----------|---------------------|
| Developer time overcommitted | Medium | High | 🔴 **Critical** | Work 6-8 hours/day minimum; communicate delays early |
| Native speaker unavailable for testing | High | Medium | 🟡 **High** | Recruit multiple testers; use online communities |
| Computing resources insufficient | Low | Low | 🟢 **Low** | Use cloud if local machine too slow |
| Third-party dependencies break | Low | High | 🟡 **High** | Pin versions in requirements.txt; test before upgrading |

### 6.3 Quality Risks

| Risk | Probability | Impact | Severity | Mitigation Strategy |
|------|-------------|--------|----------|---------------------|
| A/B test shows no improvement vs Google TTS | Medium | Critical | 🔴 **Critical** | Iterate quickly on feedback; adjust scope if needed |
| Pronunciation errors too frequent | Medium | High | 🔴 **Critical** | Extensive testing with natives; fix top 10 errors first |
| Synthetic voice rejected by users | High | High | 🔴 **Critical** | Set expectations; focus on accuracy over naturalness for MVP |
| Dialect mixing occurs | Low | High | 🟡 **High** | Strict dialect isolation; validation tests per dialect |

### 6.4 Timeline Risks

| Risk | Probability | Impact | Severity | Mitigation Strategy |
|------|-------------|--------|----------|---------------------|
| Week 1 tasks spill into Week 2 | High | Medium | 🟡 **High** | Build buffer; prioritize must-haves over nice-to-haves |
| Testing reveals major architectural issues | Medium | Critical | 🔴 **Critical** | Test early and often; refactor aggressively if needed |
| External dependencies delayed (mishkal issues) | Medium | High | 🔴 **Critical** | Have contingency plans; test dependencies Week 1 |
| 6-week timeline too aggressive | Medium | High | 🔴 **Critical** | Reduce scope if needed; focus on working demo vs perfection |

---

## 7. Success Criteria & KPIs

### 7.1 MVP Success Metrics

| Category | Metric | Target | Measurement Method | Pass/Fail |
|----------|--------|--------|-------------------|-----------|
| **Technical** | | | | |
| | Syllabification accuracy | >95% | Manual review of 50 examples | Pass: >95%, Fail: <90% |
| | Gemination detection | 100% | Automated tests (shadda explicit) | Pass: 100%, Fail: <98% |
| | IPA generation accuracy | >90% | Expert review of 100 words | Pass: >90%, Fail: <85% |
| | Processing speed | <60 sec per 1K words | Benchmark on test corpus | Pass: <60s, Fail: >120s |
| | Test pass rate | 100% | `pytest tests/` | Pass: 100%, Fail: <95% |
| | Code coverage | >80% | `pytest --cov` | Pass: >80%, Fail: <70% |
| **Quality** | | | | |
| | Audio generated successfully | 100% | Test on 100 examples | Pass: 100%, Fail: <95% |
| | Pronunciation errors | <10% | Native speaker review | Pass: <10%, Fail: >20% |
| | Dialect consistency | >90% | No feature mixing detected | Pass: >90%, Fail: <80% |
| | Edge case handling | >80% | Test unusual inputs | Pass: >80%, Fail: <60% |
| **User Validation** | | | | |
| | A/B test preference | >60% prefer yours | Blind listening test (5-10 users) | Pass: >60%, Fail: <50% |
| | MOS score | >3.5/5.0 | Average user rating | Pass: >3.5, Fail: <3.0 |
| | User satisfaction | >70% satisfied | Post-test survey | Pass: >70%, Fail: <50% |
| | Willingness to use | >50% would use | User feedback | Pass: >50%, Fail: <30% |

### 7.2 Weekly KPIs

| Week | Key Milestone | KPI | Target | Validation |
|------|---------------|-----|--------|------------|
| **Week 1** | Core fixes complete | Tests passing | 100% | `pytest tests/unit/` |
| | | Audio generation works | 10 examples | Manual test |
| | | Syllabification fixed | 0 "UNKNOWN" patterns | Code review |
| **Week 2** | Phonological rules | Sun letter accuracy | 100% | 20 test cases |
| | | Emphatic accuracy | >90% | 15 test cases |
| | | Rule integration | No conflicts | Integration test |
| **Week 3** | Diacritization | Mishkal integrated | Working | Process 10 Wiki articles |
| | | Accuracy on real text | >85% | Manual verification |
| | | Performance acceptable | <3 sec/paragraph | Benchmark |
| **Week 4** | IPA refinement | IPA accuracy | >95% | Expert review |
| | | Positional rules applied | 100% | Test all positions |
| | | No critical bugs | 0 | Bug tracker |
| **Week 5** | Testing & validation | Test dataset complete | 100 examples | File exists |
| | | A/B test conducted | 5+ participants | Survey results |
| | | User preference | >60% | Statistical analysis |
| **Week 6** | Polish & demo | All bugs fixed | 0 critical bugs | Bug tracker |
| | | Documentation complete | 100% | Doc checklist |
| | | Demo ready | Working demo | Practice run |

### 7.3 Go/No-Go Decision Criteria

**At end of Week 3 (Mid-point Review):**

| Criterion | Go Threshold | Status Check |
|-----------|--------------|-------------|
| Core pipeline works | End-to-end processing succeeds | Try 50 examples |
| Major components implemented | Syllabification + gemination + diacritization | Code review |
| No critical blockers | All P0 bugs resolved | Bug tracker |
| On schedule | <1 week behind | Timeline review |

**Decision:** If 3/4 criteria met → Continue to Week 4-6
**If <3 criteria met →** Re-scope or extend timeline

---

**At end of Week 6 (MVP Completion Review):**

| Criterion | Go Threshold | Status Check |
|-----------|--------------|-------------|
| Technical metrics | >80% of targets met | KPI dashboard |
| Quality acceptable | <10% pronunciation errors | Expert review |
| User validation | >50% prefer your system | A/B test results |
| Stable & documented | No crashes, docs complete | Final testing |

**Decision:** If 3/4 criteria met → MVP SUCCESS, proceed to Phase 2
**If <3 criteria met →** Iterate another 2 weeks on weakest areas

---

## 8. Validation & Testing Plan

### 8.1 Test Strategy Overview

| Test Type | Purpose | Frequency | Owner | Tools |
|-----------|---------|-----------|-------|-------|
| Unit Tests | Validate individual functions | Every commit | Dev | pytest |
| Integration Tests | Validate component interactions | Daily | Dev | pytest |
| End-to-End Tests | Validate full pipeline | Weekly | Dev | pytest + manual |
| Regression Tests | Ensure fixes don't break existing | Every merge | Dev | pytest |
| Performance Tests | Validate speed requirements | Weekly | Dev | pytest-benchmark |
| Quality Tests | Validate pronunciation accuracy | Weekly | Native speakers | Manual review |
| User Acceptance | Validate user satisfaction | End of MVP | Beta testers | Survey |

### 8.2 Test Pyramid

```
        /\
       /  \  User Acceptance (5%)
      /----\  
     / E2E  \ End-to-End Tests (15%)
    /--------\
   /Integration\ Integration Tests (30%)
  /--------------\
 /   Unit Tests   \ Unit Tests (50%)
/------------------\
```

### 8.3 Unit Test Coverage Plan

| Module | File | Test File | Test Cases | Priority |
|--------|------|-----------|------------|----------|
| Syllabifier | `src/core/syllabifier.py` | `tests/unit/test_syllabifier.py` | 25 | 🔴 Critical |
| Gemination | `src/core/gemination.py` | `tests/unit/test_gemination.py` | 15 | 🔴 Critical |
| Sun Letters | `src/core/sun_letters.py` | `tests/unit/test_sun_letters.py` | 20 | 🔴 Critical |
| Emphatic | `src/core/emphatic.py` | `tests/unit/test_emphatic.py` | 15 | 🟡 High |
| Diacritizer | `src/core/diacritizer.py` | `tests/unit/test_diacritizer.py` | 20 | 🔴 Critical |
| IPA Mapper | `src/core/ipa_mapper.py` | `tests/unit/test_ipa_mapper.py` | 30 | 🔴 Critical |
| eSpeak Integration | `src/integrations/espeak.py` | `tests/unit/test_espeak.py` | 10 | 🟡 High |

**Total Unit Tests:** ~135 test cases

### 8.4 Integration Test Scenarios

| Test Scenario | Description | Input | Expected Output | Priority |
|---------------|-------------|-------|-----------------|----------|
| Full Pipeline MSA | Text → IPA → Audio | "السلام عليكم" | Valid audio file | 🔴 Critical |
| Gemination Chain | Syllabification → Gemination | "مُعَلِّم" | IPA with [lː] | 🔴 Critical |
| Sun Letter Flow | Gemination → Sun Letter | "الشمس" | IPA: [aʃːams] | 🔴 Critical |
| Diacritization Chain | Raw text → Diacritized → IPA | "مرحبا" | Correct IPA | 🔴 Critical |
| Emphatic Spread | Sun Letter → Emphatic → IPA | "الصلاة" | Pharyngealized vowels | 🟡 High |
| Multi-sentence | Process paragraph | 3 sentences | 3 audio files | 🟡 High |

### 8.5 Test Data Requirements

| Dataset | Size | Content | Purpose | Status |
|---------|------|---------|---------|--------|
| Unit test examples | 50 words | Manually created | Targeted testing | ⚠️ Partial |
| Integration test examples | 20 sentences | Manually created | Component interaction | ❌ Missing |
| MVP validation set | 100 examples | Diverse real text | Quality validation | ❌ Missing |
| Wikipedia corpus | 100 paragraphs | Real-world text | Stress testing | ❌ Missing |
| Edge cases | 30 examples | Unusual constructs | Robustness | ❌ Missing |

### 8.6 Quality Validation Protocol

**Manual Review Process:**

| Step | Reviewer | Input | Output | Duration |
|------|----------|-------|--------|----------|
| 1. Generate audio | System | 100 test sentences | 100 WAV files | 30 min |
| 2. Random selection | System | 100 files | 30 random samples | 5 min |
| 3. Expert review | Native speaker | 30 audio files | Error annotations | 2 hours |
| 4. Error categorization | Dev | Annotations | Error types & counts | 1 hour |
| 5. Prioritization | Dev | Error list | Fix priority | 30 min |

**Error Categories:**

| Category | Example | Severity | Action |
|----------|---------|----------|--------|
| Wrong phoneme | /k/ instead of /q/ | 🔴 Critical | Fix immediately |
| Missing gemination | [dar] instead of [darː] | 🔴 Critical | Fix immediately |
| Wrong stress | Stress on wrong syllable | 🟡 Medium | Fix if time permits |
| Unnatural prosody | Robotic rhythm | 🟢 Low | Post-MVP |
| Audio quality | Crackling, noise | 🟢 Low | Expected for eSpeak |

### 8.7 A/B Testing Methodology

**Test Setup:**

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Sample size | 5-10 participants | Sufficient for MVP validation |
| Test sentences | 20 pairs (yours vs Google) | Balance thoroughness & fatigue |
| Presentation | Randomized, blind | Eliminate bias |
| Rating scale | 1-5 (1=worst, 5=best) | Standard MOS scale |
| Duration | 30-45 min per participant | Manageable attention span |

**Test Procedure:**

```
1. Participant briefing (5 min)
   - Explain task: rate audio quality
   - No right/wrong answers
   - Focus on pronunciation accuracy

2. Practice round (5 min)
   - 3 example pairs
   - Ensure participant understands

3. Main test (25-35 min)
   - 20 sentence pairs
   - For each pair:
     a. Listen to version A
     b. Listen to version B
     c. Rate A (1-5)
     d. Rate B (1-5)
     e. Which preferred? (A/B/Equal)

4. Open feedback (5 min)
   - What did you notice?
   - Specific issues?
   - Would you use for audiobooks?

5. Thank you & compensation
```

**Analysis Plan:**

| Metric | Calculation | Success Threshold |
|--------|-------------|-------------------|
| Mean preference | Count A vs B wins | >60% prefer yours |
| Mean Opinion Score | Average rating | >3.5/5.0 |
| Statistical significance | t-test (p<0.05) | Significant difference |
| Qualitative feedback | Thematic analysis | Positive themes dominant |

### 8.8 Continuous Testing Schedule

| Day | Test Activity | Duration | Owner |
|-----|---------------|----------|-------|
| **Daily** | Run unit tests before commit | 5 min | Dev |
| | Run integration tests before push | 10 min | Dev |
| | Code review checklist | 15 min | Dev |
| **Weekly** | Full test suite | 30 min | Dev |
| | Performance benchmarks | 20 min | Dev |
| | Quality spot-check (10 examples) | 30 min | Native speaker |
| **Bi-weekly** | Regression testing | 1 hour | Dev |
| | Documentation review | 30 min | Dev |
| **End of MVP** | Full A/B testing | 2 days | Team |
| | Comprehensive quality review | 1 day | Team |

---

## 9. Project Tracking & Reporting

### 9.1 Daily Progress Log Template

```markdown
# Daily Progress - [Date]

## Completed Today
- [ ] Task 1
- [ ] Task 2

## Blocked Issues
- Issue description | Blocker details | Resolution plan

## Tomorrow's Plan
- [ ] Task 1
- [ ] Task 2

## Metrics
- Tests passing: X/Y
- Code coverage: Z%
- Audio generation: N successes

## Notes
- Key learnings
- Questions to resolve
```

### 9.2 Weekly Status Report Template

| Section | Content |
|---------|---------|
| **Week Summary** | High-level accomplishments |
| **Completed Tasks** | Checklist with links to commits |
| **Metrics Achieved** | KPIs vs targets |
| **Risks & Issues** | New risks identified, mitigation status |
| **Next Week Plan** | Top 3 priorities |
| **Decisions Needed** | Questions requiring input |
| **Help Needed** | Resources or support required |

### 9.3 Milestone Tracking

| Milestone | Target Date | Status | Dependencies | Owner |
|-----------|-------------|--------|--------------|-------|
| Week 1 Complete | Day 7 | 🔴 Not Started | None | Dev |
| Week 2 Complete | Day 14 | 🔴 Not Started | Week 1 | Dev |
| Week 3 Complete | Day 21 | 🔴 Not Started | Week 2 | Dev |
| Mid-point Review | Day 21 | 🔴 Not Started | Week 3 | Team |
| Week 4 Complete | Day 28 | 🔴 Not Started | Week 3 | Dev |
| Week 5 Complete | Day 35 | 🔴 Not Started | Week 4 | Dev |
| Week 6 Complete | Day 42 | 🔴 Not Started | Week 5 | Dev |
| MVP Demo Ready | Day 42 | 🔴 Not Started | Week 6 | Team |

---

## 10. Communication & Collaboration

### 10.1 Stakeholder Communication Plan

| Stakeholder | Role | Update Frequency | Format | Key Info |
|-------------|------|------------------|--------|----------|
| Self (Developer) | Builder | Daily | Progress log | Tasks, blockers |
| Future Beta Testers | Validators | Weekly | Email update | Progress, when to test |
| Native Speaker Consultant | Quality checker | Bi-weekly | Video call | Examples to review |
| GitHub Community | Observers | Weekly | Commit messages | What's changing |

### 10.2 Decision Log Template

| Date | Decision | Rationale | Impact | Alternatives Considered |
|------|----------|-----------|--------|------------------------|
| | | | | |

---

## 11. Post-MVP Planning

### 11.1 Phase 2 Preparation (Weeks 7-12)

| Focus Area | Goal | Key Tasks |
|------------|------|-----------|
| Egyptian Dialect | Add EG support | Complete EG phonological rules |
| Audio Quality | Upgrade from eSpeak | Integrate Coqui TTS with VITS |
| Prosody | Natural rhythm | Implement stress & intonation |
| Scale Testing | Handle larger corpus | Test on 10+ books |
| API Development | Programmatic access | Build REST API |
| Documentation | User-facing | Create tutorials, examples |

### 11.2 Success Criteria for Phase 2

| Metric | Target |
|--------|--------|
| Dialects supported | 2 (MSA + EG) |
| Audio quality MOS | >4.0/5.0 |
| Paying beta customers | 3-5 |
| Processing speed | <30 sec per 1K words |

---

## Appendix A: Command Reference

### Testing Commands

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/unit/test_syllabifier.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run only failed tests from last run
pytest --lf

# Run tests matching keyword
pytest -k "syllabification"
```

### Development Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Install new dependency
pip install mishkal
pip freeze > requirements.txt

# Run Flask app
python3 app.py

# Generate audio with eSpeak
espeak-ng -v ar "مرحبا" -w output.wav
```

### Git Workflow

```bash
# Daily commit pattern
git status
git add <files>
git commit -m "feat: implement gemination processor"
git push origin main

# Feature branch (for larger changes)
git checkout -b feature/sun-letters
# ... work ...
git commit -m "feat: add sun letter assimilation"
git checkout main
git merge feature/sun-letters
git push origin main
```

---

## Appendix B: File Structure

```
ArabicTTS/
├── app.py                              # Flask web application
├── requirements.txt                    # Python dependencies
├── pytest.ini                          # Pytest configuration
├── README.md                           # Project overview
├── PROJECT_DOCUMENTATION.md            # Technical documentation
├── BUSINESS_ANALYSIS_REPORT.md         # Strategic analysis
├── MVP_IMPLEMENTATION_PLAN.md          # This file
│
├── src/
│   ├── main.py                         # Main TTS processor
│   ├── core/
│   │   ├── __init__.py
│   │   ├── syllabifier.py              # ✅ Fix Week 1
│   │   ├── gemination.py               # ❌ Create Week 1
│   │   ├── sun_letters.py              # ❌ Create Week 2
│   │   ├── emphatic.py                 # ❌ Create Week 2
│   │   ├── positional_rules.py         # ❌ Create Week 4
│   │   ├── diacritizer.py              # ❌ Create Week 3
│   │   ├── ipa_mapper.py               # ⚠️ Enhance Week 4
│   │   ├── tts_processor.py            # Existing
│   │   └── phonological_rules.py       # ❌ Create Week 2
│   ├── dialects/
│   │   ├── __init__.py
│   │   ├── base_dialect.py
│   │   ├── msa.py                      # ⚠️ Enhance
│   │   ├── egyptian.py
│   │   ├── gulf.py
│   │   ├── levantine.py
│   │   └── maghreb.py
│   ├── integrations/
│   │   ├── __init__.py
│   │   └── espeak.py                   # ❌ Create Week 1
│   └── utils/
│       ├── __init__.py
│       ├── text_utils.py
│       ├── file_io.py
│       └── debug.py
│
├── data/
│   ├── dictionaries/
│   │   ├── masterTTS.json              # ✅ Exists
│   │   └── syllable_patterns.json      # ❌ Create Week 1
│   └── test_cases/
│       ├── msa_sample.txt              # ✅ Exists
│       ├── eg_sample.txt               # ✅ Exists
│       ├── mvp_examples.txt            # ❌ Create Week 1
│       └── mvp_test_set.txt            # ❌ Create Week 5
│
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── test_syllabifier.py         # ⚠️ Fix Week 1
│   │   ├── test_gemination.py          # ❌ Create Week 1
│   │   ├── test_sun_letters.py         # ❌ Create Week 2
│   │   ├── test_emphatic.py            # ❌ Create Week 2
│   │   ├── test_diacritizer.py         # ❌ Create Week 3
│   │   ├── test_ipa_mapper.py          # ❌ Create Week 4
│   │   └── test_espeak.py              # ❌ Create Week 1
│   └── integration/
│       ├── test_full_pipeline.py       # ⚠️ Enhance
│       ├── test_mvp_pipeline.py        # ❌ Create Week 1
│       └── test_phonology.py           # ❌ Create Week 2
│
├── templates/
│   └── index.html                      # ✅ Exists
│
└── docs/
    ├── WEEK1_PROGRESS.md               # ❌ Create Week 1
    ├── WEEK2_PROGRESS.md               # ❌ Create Week 2
    ├── DIACRITIZATION.md               # ❌ Create Week 3
    ├── API_REFERENCE.md                # ❌ Create Week 6
    ├── TESTING_GUIDE.md                # ❌ Create Week 6
    └── MVP_RESULTS.md                  # ❌ Create Week 6
```

---

**END OF MVP IMPLEMENTATION PLAN**

**Next Action:** Review this plan, confirm priorities, and begin Week 1 Task 1.1 (Fix Syllabification Algorithm).

**Questions or clarifications needed before starting?**
