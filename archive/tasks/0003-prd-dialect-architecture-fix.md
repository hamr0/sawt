# PRD: Dialect Architecture Fix - Universal Processing with Deferred IPA Lookup

**Product:** Arabic Text-to-Speech System
**Phase:** Architecture Refactor
**Version:** 1.0
**Date:** December 14, 2025
**Owner:** Development Team
**Status:** Ready for Implementation

---

## 1. Introduction/Overview

### Problem Statement

The current Arabic TTS system has a fundamental architectural flaw: **dialect selection happens prematurely in the processing pipeline**. Specifically:

1. **AllophoneProcessor** loads dialect-specific IPA mappings during `__init__()`, "baking in" dialect data at construction time
2. **GeminationProcessor**, **SunLetterProcessor**, and **EmphaticProcessor** accept `dialect` parameters they never use (misleading API)
3. **ArabicSyllabifier** loads dialect-specific pattern data during initialization
4. The **AllophoneProcessor** conflates two separate responsibilities: position detection (universal) and IPA lookup (dialect-specific)

This causes several issues:
- Cannot switch dialects without recreating processor instances
- Phonological rules incorrectly appear dialect-dependent when they are universal
- Testing is complicated because dialect is coupled to processing logic
- Code is harder to understand and maintain

### Correct Architecture Philosophy

**Phonological processing rules are UNIVERSAL across all Arabic dialects.** The phenomena of:
- Gemination (shadda doubling consonants)
- Sun letter assimilation (/al/ + sun letter)
- Position detection (initial/medial/final)
- Emphatic spread (pharyngealization)

...work identically in Egyptian, MSA, Gulf, Levantine, and Maghrebi Arabic. These are core Arabic phonological rules.

**Only the final character-to-IPA mapping is dialect-specific.** Different dialects pronounce the same letter differently:
- ج is /g/ in Egyptian but /dz/ in MSA
- ق is /ʔ/ in Egyptian but /q/ in MSA

### Solution Overview

Refactor the pipeline to:
1. Make all phonological processors truly universal (no dialect parameter)
2. Create a dedicated **IPAMapper** component that handles dialect-specific lookup
3. Move dialect selection to the FINAL step before audio generation
4. Clean up the API to accurately reflect what is universal vs dialect-specific

### High-Level Goal

Achieve a clean separation between:
- **Universal phonological processing** (detects features, marks syllables, applies rules)
- **Dialect-specific IPA generation** (converts processed syllables to IPA using dialect data)

---

## 2. Goals

### Primary Goals

1. **Architectural Correctness**: Separate universal processing from dialect-specific IPA lookup
2. **API Clarity**: Remove misleading dialect parameters from universal processors
3. **Maintainability**: Single point of dialect selection at the final step
4. **Testability**: Test processors independently of dialect data
5. **Flexibility**: Enable dialect switching without recreating instances

### Secondary Goals

1. Improve code documentation to explain the architecture clearly
2. Reduce code complexity in AllophoneProcessor by splitting responsibilities
3. Enable future features like runtime dialect switching
4. Prepare architecture for streaming/real-time processing

### Success Criteria

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| **Test Pass Rate** | 100% | All 329+ existing tests pass after refactor |
| **Processor Universality** | Verified | Processors produce identical output regardless of dialect |
| **Code Quality** | Improved | Reduced complexity, clearer responsibilities |
| **Performance** | No regression | Same or better throughput (3,059 words/sec) |
| **Documentation** | Complete | Architecture diagram and code comments updated |

---

## 3. User Stories

### As a Developer

**US-1:** As a developer, I want phonological processors to be dialect-agnostic so that I can test them without loading dialect data.

**US-2:** As a developer, I want a single point of dialect selection so that I can easily understand where dialect-specific logic lives.

**US-3:** As a developer, I want clear API signatures so that I know which components are universal vs dialect-specific.

**US-4:** As a developer, I want to switch dialects at runtime without recreating the entire processing pipeline.

### As a Maintainer

**US-5:** As a maintainer, I want separated concerns so that bugs in phonological processing are isolated from IPA mapping issues.

**US-6:** As a maintainer, I want comprehensive tests proving processors are universal so that future changes don't accidentally introduce dialect coupling.

### As a Future Contributor

**US-7:** As a contributor adding a new dialect, I want to only add entries to masterTTS.json without modifying processor code.

**US-8:** As a contributor, I want clear documentation explaining why the architecture separates universal rules from dialect lookup.

---

## 4. Functional Requirements

### 4.1 Universal Phonological Processors

**FR-1.1** GeminationProcessor MUST NOT accept a `dialect` parameter in its constructor.

**FR-1.2** SunLetterProcessor MUST NOT accept a `dialect` parameter in its constructor.

**FR-1.3** EmphaticProcessor MUST NOT accept a `dialect` parameter in its constructor.

**FR-1.4** All phonological processors MUST produce identical output for the same input, regardless of intended target dialect.

**FR-1.5** Phonological processors MUST only detect and mark features (gemination, sun letters, emphatic consonants, positions) without generating IPA.

### 4.2 Position Detection (Extracted from AllophoneProcessor)

**FR-2.1** The system MUST have a dedicated PositionDetector component (or method) that detects character/syllable positions (initial, medial, final).

**FR-2.2** Position detection MUST be universal and dialect-agnostic.

**FR-2.3** Position detection MUST run as part of the phonological processing phase, NOT during IPA lookup.

**FR-2.4** The PositionDetector MUST mark each syllable/character with its detected position without generating IPA.

### 4.3 Dedicated IPA Mapper

**FR-3.1** The system MUST have a dedicated IPAMapper class responsible for dialect-specific character-to-IPA conversion.

**FR-3.2** IPAMapper MUST accept dialect as a parameter to its lookup methods (not constructor).

**FR-3.3** IPAMapper MUST load masterTTS.json once and support lookups for any dialect without reloading.

**FR-3.4** IPAMapper MUST support position-based IPA lookup using positions detected by earlier processors.

**FR-3.5** IPAMapper MUST be the ONLY component that reads dialect-specific IPA from masterTTS.json for final output.

**FR-3.6** IPAMapper MUST handle the following lookup precedence:
   1. Position-specific IPA (word-initial, word-medial, word-final)
   2. Context-specific IPA (near emphatic, after vowel, etc.)
   3. Default IPA

### 4.4 Pipeline Integration

**FR-4.1** The ArabicTTS class MUST orchestrate the pipeline in this order:
   1. Preprocessing (diacritization) - universal
   2. Tokenization - universal
   3. Syllabification - universal (patterns are same across dialects)
   4. Phonological processing (in order):
      - Gemination detection - universal
      - Sun letter detection - universal
      - Position detection - universal
      - Emphatic detection - universal
   5. IPA mapping - DIALECT SELECTED HERE
   6. X-SAMPA conversion
   7. Audio generation

**FR-4.2** Dialect selection MUST happen at step 5 (IPA mapping) and ONLY at step 5.

**FR-4.3** The pipeline MUST support changing dialect between step 4 and step 5 without reprocessing steps 1-4.

### 4.5 ArabicSyllabifier Cleanup

**FR-5.1** ArabicSyllabifier SHOULD NOT load dialect-specific data during initialization for syllable patterns (patterns are universal).

**FR-5.2** If dialect-specific syllable patterns exist (they currently don't differ), they SHOULD be applied at syllabification time, not construction time.

**FR-5.3** The `apply_ipa_rules()` method in ArabicSyllabifier MUST be removed or refactored to use IPAMapper.

### 4.6 Backward Compatibility

**FR-6.1** The system MUST maintain backward compatibility with existing API calls where possible.

**FR-6.2** If breaking changes are required, they MUST be clearly documented with migration examples.

**FR-6.3** The system MUST continue to support dialect specification at ArabicTTS instantiation as a convenience (default dialect).

---

## 5. Non-Goals (Out of Scope)

**NG-1** Performance optimization beyond maintaining current throughput - focus is on correctness

**NG-2** Adding new dialects - this refactor prepares the architecture but doesn't add data

**NG-3** Changing the phonological rules themselves - only restructuring where they execute

**NG-4** Modifying masterTTS.json structure - use existing data format

**NG-5** Real-time streaming support - deferred to future work

**NG-6** UI/API endpoint changes - focus is on internal architecture

**NG-7** Audio generation changes - out of scope for this refactor

---

## 6. Design Considerations

### 6.1 New Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     REFACTORED ARABIC TTS PIPELINE                           │
└──────────────────────────────────────────────────────────────────────────────┘

Arabic Text Input
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ UNIVERSAL PROCESSING PHASE (No dialect dependency)                          │
│                                                                              │
│  [1] Diacritization (mishkal)                                               │
│       └── Add vowels/diacritics to undiacritized text                       │
│                                                                              │
│  [2] Tokenization                                                            │
│       └── Split into words, characters, punctuation                          │
│                                                                              │
│  [3] Syllabification                                                         │
│       └── Segment words into syllables (CV, CVC, CVV, CVCC patterns)        │
│                                                                              │
│  [4] Phonological Processing (ALL UNIVERSAL):                                │
│       ┌────────────────────────────────────────────────────────────────┐    │
│       │  4.1 GeminationProcessor                                        │    │
│       │      └── Detect shadda (ّ), mark geminated consonants           │    │
│       │                                                                  │    │
│       │  4.2 SunLetterProcessor                                         │    │
│       │      └── Detect ال + sun letter, mark for assimilation          │    │
│       │                                                                  │    │
│       │  4.3 PositionDetector                                           │    │
│       │      └── Detect initial/medial/final positions                  │    │
│       │                                                                  │    │
│       │  4.4 EmphaticProcessor                                          │    │
│       │      └── Detect emphatics (ص،ض،ط،ظ،ق), mark for pharyngealization│    │
│       └────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  OUTPUT: Processed syllables with markers:                                   │
│    - has_gemination: true/false                                             │
│    - geminated_consonant: 'ر'                                               │
│    - sun_letter_assimilation: true/false                                    │
│    - detected_position: 'word-initial'/'word-medial'/'word-final'          │
│    - has_emphatic: true/false                                               │
│    - emphatic_consonants: ['ص']                                             │
│    - pharyngealization_spread: true/false                                   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ Processed syllables (dialect-agnostic)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ DIALECT-SPECIFIC PHASE (Dialect selected here)                              │
│                                                                              │
│  [5] IPAMapper.map_to_ipa(syllables, dialect="EG")                          │
│       │                                                                      │
│       ├── Read markers from processed syllables                              │
│       ├── Look up character IPA from masterTTS.json[dialect]                │
│       ├── Apply position-specific IPA based on detected_position            │
│       ├── Apply gemination (double consonant) based on has_gemination       │
│       ├── Apply sun letter assimilation based on sun_letter_assimilation    │
│       ├── Apply pharyngealization based on pharyngealization_spread         │
│       │                                                                      │
│       └── OUTPUT: IPA transcription string                                  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    │ IPA string (dialect-specific)
    │
    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ AUDIO GENERATION PHASE                                                      │
│                                                                              │
│  [6] X-SAMPA Conversion                                                     │
│       └── IPA → X-SAMPA for eSpeak/Polly                                    │
│                                                                              │
│  [7] Audio Synthesis                                                        │
│       └── eSpeak NG or Amazon Polly                                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
    │
    ▼
WAV/MP3 Audio Output
```

### 6.2 Component Responsibilities

| Component | Responsibility | Dialect Aware? |
|-----------|---------------|----------------|
| **Diacritizer** | Add vowels to text | No |
| **Tokenizer** | Split text into tokens | No |
| **Syllabifier** | Segment into syllables | No |
| **GeminationProcessor** | Detect and mark shadda | No |
| **SunLetterProcessor** | Detect and mark sun letters | No |
| **PositionDetector** | Detect word positions | No |
| **EmphaticProcessor** | Detect and mark emphatics | No |
| **IPAMapper** | Convert to IPA | **YES** |
| **XSampaConverter** | IPA to X-SAMPA | No |
| **AudioGenerator** | Synthesize audio | No |

### 6.3 IPAMapper Design

```python
class IPAMapper:
    """
    Converts processed syllables to IPA using dialect-specific data.
    This is the ONLY component that is dialect-aware.
    """

    def __init__(self, master_tts_path: Optional[str] = None):
        """
        Initialize IPA mapper by loading masterTTS.json ONCE.
        Does NOT select a dialect at construction time.
        """
        self.master_tts = self._load_master_tts(master_tts_path)
        self._build_lookup_tables()  # Build tables for ALL dialects

    def map_to_ipa(self, syllables: List[Dict], dialect: str) -> str:
        """
        Convert processed syllables to IPA for specified dialect.

        Args:
            syllables: Processed syllables with markers from phonological processors
            dialect: Target dialect ("EG", "MSA", "Gulf", "Levantine", "Maghrebi")

        Returns:
            Complete IPA transcription string
        """
        ...

    def get_ipa_for_char(self, char: str, dialect: str,
                         position: str = "default",
                         context: Optional[Dict] = None) -> str:
        """
        Get IPA for a single character in specified dialect and position.
        """
        ...
```

### 6.4 Processor Refactoring

**Before (current):**
```python
class GeminationProcessor:
    def __init__(self, dialect: str):  # dialect NEVER USED
        self.dialect = dialect
        ...
```

**After (refactored):**
```python
class GeminationProcessor:
    def __init__(self):  # No dialect - universal
        ...
```

**Before (AllophoneProcessor):**
```python
class AllophoneProcessor:
    def __init__(self, dialect: str, master_tts_path: Optional[str] = None):
        self.dialect = dialect
        self.master_tts = json.load(...)  # Loads dialect data immediately
        self._build_allophone_maps()  # Builds dialect-specific maps
```

**After (split into PositionDetector + IPAMapper):**
```python
class PositionDetector:
    def __init__(self):  # No dialect - universal
        ...

    def detect_positions(self, syllables: List[Dict]) -> List[Dict]:
        """Mark positions without generating IPA."""
        ...

class IPAMapper:
    def __init__(self, master_tts_path: Optional[str] = None):
        self.master_tts = json.load(...)  # Load ALL dialects

    def map_to_ipa(self, syllables: List[Dict], dialect: str) -> str:
        """Generate IPA using specified dialect."""
        ...
```

---

## 7. Technical Considerations

### 7.1 File Changes Required

| File | Change Type | Description |
|------|-------------|-------------|
| `src/core/gemination.py` | Modify | Remove `dialect` parameter from `__init__` |
| `src/core/sun_letters.py` | Modify | Remove `dialect` parameter from `__init__` |
| `src/core/emphatic.py` | Modify | Remove `dialect` parameter from `__init__` |
| `src/core/allophones.py` | **Major refactor** | Split into PositionDetector; remove IPA generation |
| `src/core/ipa_mapper.py` | **Create new** | New dedicated IPA mapping component |
| `src/core/position_detector.py` | **Create new** | Position detection extracted from allophones |
| `src/main.py` | Modify | Update pipeline to use new architecture |
| `src/core/syllabifier.py` | Modify | Remove dialect-dependent IPA lookup |
| `tests/unit/test_*.py` | Modify | Update tests to verify universality |
| `tests/unit/test_ipa_mapper.py` | **Create new** | Tests for new IPAMapper |
| `tests/unit/test_position_detector.py` | **Create new** | Tests for PositionDetector |
| `tests/unit/test_universal_processors.py` | **Create new** | Universality verification tests |

### 7.2 Migration Strategy

**Phase 1: Create new components (non-breaking)**
1. Create `src/core/ipa_mapper.py` with new IPAMapper class
2. Create `src/core/position_detector.py` with PositionDetector class
3. Add comprehensive tests for new components
4. Ensure new components work alongside existing code

**Phase 2: Refactor existing processors (minimal breaking)**
1. Remove unused `dialect` parameter from GeminationProcessor
2. Remove unused `dialect` parameter from SunLetterProcessor
3. Remove unused `dialect` parameter from EmphaticProcessor
4. Update AllophoneProcessor to only do position detection (or deprecate)
5. Update tests to reflect new signatures

**Phase 3: Update pipeline integration**
1. Modify ArabicTTS to use new architecture
2. Update `apply_phonological_rules()` to not pass dialect
3. Add IPAMapper call after phonological processing
4. Run full regression test suite

**Phase 4: Cleanup and documentation**
1. Remove deprecated code paths
2. Update architecture documentation
3. Add inline code comments explaining design decisions
4. Update README and docstrings

### 7.3 Backward Compatibility

To maintain backward compatibility:

```python
# In ArabicTTS.__init__
class ArabicTTS:
    def __init__(self, dialect: str):
        self.dialect = dialect  # Default dialect for convenience

        # Universal processors (no dialect needed)
        self.gemination_processor = GeminationProcessor()
        self.sun_letter_processor = SunLetterProcessor()
        self.position_detector = PositionDetector()
        self.emphatic_processor = EmphaticProcessor()

        # Dialect-aware mapper (loads all dialects, uses default)
        self.ipa_mapper = IPAMapper()

    def process_text(self, text: str, dialect: Optional[str] = None) -> Dict:
        """
        Process text using specified dialect (or default).

        Args:
            text: Arabic text to process
            dialect: Target dialect (optional, uses self.dialect if not specified)
        """
        dialect = dialect or self.dialect

        # Steps 1-4: Universal processing
        syllables = self._universal_processing(text)

        # Step 5: Dialect-specific IPA mapping
        ipa = self.ipa_mapper.map_to_ipa(syllables, dialect)

        return {...}
```

### 7.4 Performance Considerations

- IPAMapper should load masterTTS.json ONCE and cache lookup tables for all dialects
- Position detection should be O(n) where n is number of syllables
- IPA lookup should be O(1) using pre-built hash maps
- No performance regression expected; slight improvement possible from reduced initialization

### 7.5 Dependencies

No new external dependencies required. Changes are internal refactoring only.

---

## 8. Success Metrics

### 8.1 Quantitative Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Existing test pass rate** | 100% | `pytest tests/` |
| **New test coverage** | 100% for new components | `pytest --cov` |
| **Processing throughput** | >= 3,059 words/sec | Performance benchmark |
| **Universality verification** | 100% | Same output across dialects |
| **Code complexity** | Reduced | Lines of code, cyclomatic complexity |

### 8.2 Qualitative Metrics

| Metric | Target | Evaluation Method |
|--------|--------|-------------------|
| **Architecture clarity** | Clear separation | Code review |
| **Documentation quality** | Complete | Documentation review |
| **API consistency** | Intuitive signatures | Developer feedback |
| **Maintainability** | Improved | Code review |

### 8.3 Universality Verification Tests

New test suite to verify processors are truly universal:

```python
class TestProcessorUniversality:
    """
    Verify that phonological processors produce identical output
    regardless of target dialect.
    """

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_gemination_is_universal(self, dialect):
        """Gemination detection should be identical across dialects."""
        processor = GeminationProcessor()  # No dialect parameter
        input_syllables = [{"syllable": "مُدَرِّس"}]
        result = processor.process(input_syllables)

        # Result should be same regardless of what dialect we'll use later
        assert result[0]["has_gemination"] == True
        assert result[0]["geminated_consonant"] == "ر"

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_sun_letter_is_universal(self, dialect):
        """Sun letter detection should be identical across dialects."""
        processor = SunLetterProcessor()  # No dialect parameter
        # Test with الشمس (the sun)
        ...

    def test_same_syllables_different_ipa_by_dialect(self):
        """
        Same processed syllables should produce different IPA
        based on dialect selection in IPAMapper.
        """
        # Process text universally
        syllables = universal_process("جمل")  # camel

        # Same input, different dialects
        eg_ipa = ipa_mapper.map_to_ipa(syllables, "EG")
        msa_ipa = ipa_mapper.map_to_ipa(syllables, "MSA")

        # EG: ج = /g/, MSA: ج = /dz/
        assert "g" in eg_ipa
        assert "dz" in msa_ipa or "d͡ʒ" in msa_ipa
```

---

## 9. Open Questions

**OQ-1:** Should we keep `AllophoneProcessor` as a deprecated wrapper for backward compatibility, or remove it entirely?

**Recommendation:** Keep as deprecated wrapper for one release cycle, then remove.

**OQ-2:** Should syllable patterns in `ArabicSyllabifier` be truly universal, or might future dialects need different patterns?

**Recommendation:** Currently patterns are identical across dialects. Keep universal for now; add dialect parameter to `segment_syllables()` if needed later.

**OQ-3:** Should `IPAMapper` support multiple simultaneous lookup calls for performance (batch processing)?

**Recommendation:** Start with single-call API; add batch method if performance testing shows need.

**OQ-4:** How should we handle the `apply_ipa_rules()` method in ArabicSyllabifier that currently does dialect lookup?

**Recommendation:** Deprecate and redirect to IPAMapper. Eventually remove.

**OQ-5:** Should we rename `AllophoneProcessor` to `PositionDetector` or create a new class?

**Recommendation:** Create new `PositionDetector` class; keep `AllophoneProcessor` as deprecated alias.

---

## 10. Implementation Checklist

### Phase 1: New Components (Week 1)
- [ ] Create `src/core/ipa_mapper.py` with IPAMapper class
- [ ] Create `src/core/position_detector.py` with PositionDetector class
- [ ] Create `tests/unit/test_ipa_mapper.py` with comprehensive tests
- [ ] Create `tests/unit/test_position_detector.py` with comprehensive tests
- [ ] Verify new components work correctly in isolation

### Phase 2: Processor Refactoring (Week 2)
- [ ] Remove `dialect` parameter from `GeminationProcessor.__init__()`
- [ ] Remove `dialect` parameter from `SunLetterProcessor.__init__()`
- [ ] Remove `dialect` parameter from `EmphaticProcessor.__init__()`
- [ ] Update/deprecate `AllophoneProcessor` to use `PositionDetector`
- [ ] Update all unit tests for modified processors
- [ ] Create `tests/unit/test_universal_processors.py` for universality verification

### Phase 3: Pipeline Integration (Week 2-3)
- [ ] Update `ArabicTTS.__init__()` to use new architecture
- [ ] Update `apply_phonological_rules()` to not pass dialect
- [ ] Add `IPAMapper` call in pipeline after phonological processing
- [ ] Update `ArabicSyllabifier` to remove dialect-dependent IPA lookup
- [ ] Run full regression test suite (329+ tests)

### Phase 4: Cleanup and Documentation (Week 3)
- [ ] Remove deprecated code paths (if any)
- [ ] Update `docs/ARCHITECTURE.md` with new pipeline diagram
- [ ] Update `docs/TECH_STACK.md` with component responsibilities
- [ ] Add inline code comments explaining architecture decisions
- [ ] Update `README.md` with any API changes
- [ ] Create migration guide for any breaking changes

### Verification Checklist
- [ ] All 329+ existing tests pass
- [ ] All new tests pass
- [ ] Universality tests pass (processors produce same output regardless of target dialect)
- [ ] Performance benchmark shows no regression
- [ ] Code review completed
- [ ] Documentation review completed

---

## Appendix A: Current Code Analysis

### AllophoneProcessor Issues (src/core/allophones.py)

**Lines 31-50:** Dialect selected at construction time
```python
def __init__(self, dialect: str, master_tts_path: Optional[str] = None):
    self.dialect = dialect  # PROBLEM: Baked in at construction
    ...
    self._build_allophone_maps()  # PROBLEM: Builds dialect-specific maps
```

**Lines 64-85:** Dialect data loaded immediately
```python
def _build_allophone_maps(self):
    if self.dialect not in self.master_tts:
        raise ValueError(...)
    dialect_data = self.master_tts[self.dialect]  # PROBLEM: Uses specific dialect
```

**Lines 210-231:** IPA lookup mixed with position detection
```python
def get_ipa_for_char(self, char: str, position: str) -> str:
    # PROBLEM: This should be in IPAMapper, not AllophoneProcessor
    if char in self.allophone_map:
        if position in self.allophone_map[char]:
            return self.allophone_map[char][position]
```

### Unused dialect Parameters

**GeminationProcessor (src/core/gemination.py, line 22-29):**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # NEVER USED in any method
    self.shadda = 'ّ'
```

**SunLetterProcessor (src/core/sun_letters.py, line 32-38):**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # NEVER USED - sun letters are universal
```

**EmphaticProcessor (src/core/emphatic.py, line 33-49):**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # NEVER USED - emphatic consonants are universal
```

---

## Appendix B: masterTTS.json Structure Reference

```json
{
    "EG": [
        {
            "Arabic letter": "أ",
            "IPA": "ʔ",
            "X-SAMPA": "?",
            "Position": "default",
            ...
        },
        {
            "Arabic letter": "أ",
            "IPA": "∅",
            "Position": "word-medial",
            ...
        },
        {
            "Arabic letter": "أ",
            "IPA": "[ʔ]",
            "Position": "word-initial",
            ...
        }
    ],
    "MSA": [...],
    "Gulf": [...],
    "Levantine": [...],
    "Maghrebi": [...]
}
```

**Key fields for IPAMapper:**
- `Arabic letter`: Character to look up
- `IPA`: IPA transcription for this character
- `Position`: Position context ("default", "word-initial", "word-medial", "word-final")
- Dialect is selected by top-level key ("EG", "MSA", etc.)

---

## Appendix C: Test Case Examples

### Universality Test Cases

| Input | Feature | Expected Detection | IPA (EG) | IPA (MSA) |
|-------|---------|-------------------|----------|-----------|
| مُدَرِّس | Gemination | `has_gemination: true, geminated_consonant: ر` | mudarːis | mudarːis |
| الشمس | Sun letter | `sun_letter_assimilation: true` | aʃːams | aʃːams |
| صباح | Emphatic | `has_emphatic: true, emphatic_consonants: [ص]` | sˁɑbɑːħ | sˁabaaħ |
| جمل | Position | `detected_position: word-initial` | gamal | dʒamal |

**Note:** Detection is identical; IPA differs by dialect only in final lookup.

---

**Document Version:** 1.0
**Last Updated:** December 14, 2025
**Status:** Ready for Implementation

---

**END OF PRD**
