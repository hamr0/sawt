# Task List: Dialect Architecture Fix - Universal Processing with Deferred IPA Lookup

**PRD Reference:** `tasks/0003-prd-dialect-architecture-fix.md`
**Status:** Ready for Implementation
**Date Created:** December 14, 2025
**Total Estimated Duration:** 3-4 weeks (60-80 hours)
**Difficulty:** High (architectural refactor)

---

## Overview

This task list breaks down the dialect architecture refactoring into 4 sequential phases:

1. **Phase 1:** Create new universal components (IPAMapper, PositionDetector)
2. **Phase 2:** Refactor existing processors to be dialect-agnostic
3. **Phase 3:** Update main pipeline to use new architecture
4. **Phase 4:** Testing, validation, and documentation

Each task includes:
- Clear acceptance criteria
- Specific code changes required
- Test cases to implement
- Dependencies on other tasks
- Estimated effort (hours)

---

## Phase 1: Create New Components (Non-Breaking)

### Task 1.1: Create IPAMapper Class

**Objective:** Implement a new dedicated component for dialect-specific IPA mapping.

**Description:**

Create a new `src/core/ipa_mapper.py` file containing the `IPAMapper` class. This class centralizes all dialect-specific character-to-IPA conversion logic that is currently scattered across `AllophoneProcessor` and `ArabicSyllabifier`.

**Acceptance Criteria:**

- [ ] File `src/core/ipa_mapper.py` created with full IPAMapper implementation
- [ ] IPAMapper loads masterTTS.json ONCE at construction (not per-lookup)
- [ ] IPAMapper builds lookup tables for ALL dialects at initialization
- [ ] No dialect is selected during construction (dialect passed to lookup methods only)
- [ ] IPAMapper provides two main methods:
  - `map_to_ipa(syllables: List[Dict], dialect: str) -> str`
  - `get_ipa_for_char(char: str, dialect: str, position: str = "default", context: Optional[Dict] = None) -> str`
- [ ] IPAMapper respects lookup precedence: position-specific → context-specific → default
- [ ] IPAMapper handles missing characters gracefully (returns fallback or raises clear error)
- [ ] Class docstring clearly states: "This is the ONLY dialect-aware component"

**Code Changes Required:**

**New file:** `src/core/ipa_mapper.py`

```python
class IPAMapper:
    """
    Maps processed Arabic syllables to IPA using dialect-specific data.

    ARCHITECTURE NOTE: This is the ONLY component that is dialect-aware.
    All phonological processing happens BEFORE this mapper and is universal.
    Dialect selection happens AT THIS STEP ONLY.
    """

    def __init__(self, master_tts_path: Optional[str] = None):
        """
        Initialize by loading masterTTS.json ONCE and building lookup tables.
        Does NOT select a dialect - dialect is passed to lookup methods.

        Args:
            master_tts_path: Path to masterTTS.json (defaults to data/dictionaries/masterTTS.json)
        """
        # Load master TTS data
        self.master_tts = self._load_master_tts(master_tts_path)

        # Build lookup tables for ALL dialects (one-time cost)
        self.lookup_tables = {}
        for dialect in self.master_tts:
            self.lookup_tables[dialect] = self._build_lookup_table(dialect)

    def _load_master_tts(self, path: Optional[str]) -> Dict:
        """Load masterTTS.json from disk."""
        # Implementation details
        pass

    def _build_lookup_table(self, dialect: str) -> Dict:
        """
        Build efficient lookup structure for a dialect.

        Structure:
        {
            'أ': {
                'default': 'ʔ',
                'word-initial': '[ʔ]',
                'word-medial': '∅',
                'word-final': '[ʔ]'
            },
            'ب': { ... },
            ...
        }
        """
        # Implementation details
        pass

    def map_to_ipa(self, syllables: List[Dict], dialect: str) -> str:
        """
        Convert processed syllables to IPA for specified dialect.

        Args:
            syllables: Processed syllables with markers from phonological processors
            dialect: Target dialect ("EG", "MSA", "Gulf", "Levantine", "Maghrebi")

        Returns:
            Complete IPA transcription string

        Raises:
            ValueError: If dialect not in master_tts
        """
        # Implementation details
        pass

    def get_ipa_for_char(self, char: str, dialect: str,
                         position: str = "default",
                         context: Optional[Dict] = None) -> str:
        """
        Get IPA for a single character in specified dialect and position.

        Lookup precedence:
        1. Position-specific IPA (word-initial, word-medial, word-final)
        2. Context-specific IPA (if context provided and relevant)
        3. Default IPA

        Args:
            char: Arabic character to look up
            dialect: Target dialect
            position: Position context ("default", "word-initial", "word-medial", "word-final")
            context: Optional context dict with keys like 'after_emphatic', 'before_vowel'

        Returns:
            IPA string for this character in this context

        Raises:
            KeyError: If character not found in dialect data
        """
        # Implementation details
        pass
```

**Test Cases:**

Create `tests/unit/test_ipa_mapper.py` with:

- [ ] Test IPAMapper initialization loads all dialects without error
- [ ] Test IPAMapper lookup returns correct IPA for EG dialect (10 characters)
- [ ] Test IPAMapper lookup returns correct IPA for MSA dialect (10 characters)
- [ ] Test position-specific lookup (word-initial, word-medial, word-final)
- [ ] Test default fallback when position not available
- [ ] Test handling of characters not in dialect data (should raise KeyError or return fallback)
- [ ] Test `map_to_ipa()` with 5 test syllables from existing test dataset
- [ ] Test dialect switching: same syllables → different IPA by dialect
- [ ] Test that masterTTS.json is loaded only once during initialization
- [ ] Test performance: 1000 lookups should complete in <100ms

**Dependencies:**

- Existing `data/dictionaries/masterTTS.json` (no changes needed)
- Existing test dataset structure

**Estimated Effort:** 6-8 hours

**Success Verification:**

```bash
pytest tests/unit/test_ipa_mapper.py -v
# All tests should pass
# No errors loading masterTTS.json
# No performance degradation
```

---

### Task 1.2: Create PositionDetector Class

**Objective:** Extract position detection logic from AllophoneProcessor into a dedicated universal component.

**Description:**

Create a new `src/core/position_detector.py` file containing the `PositionDetector` class. This class detects word positions (initial, medial, final) for each character or syllable, without any dialect awareness or IPA generation.

**Acceptance Criteria:**

- [ ] File `src/core/position_detector.py` created with full PositionDetector implementation
- [ ] PositionDetector has NO dialect parameter in constructor
- [ ] PositionDetector provides `detect_positions(syllables: List[Dict]) -> List[Dict]` method
- [ ] Method adds `detected_position` key to each syllable dict
- [ ] Correctly detects word-initial, word-medial, word-final positions
- [ ] Handles edge cases: single-character words, multiple words, punctuation
- [ ] Does NOT generate IPA (only marks positions)
- [ ] Output format compatible with existing processor output format

**Code Changes Required:**

**New file:** `src/core/position_detector.py`

```python
class PositionDetector:
    """
    Detects word positions (initial, medial, final) for syllables.

    ARCHITECTURE NOTE: This component is UNIVERSAL and dialect-agnostic.
    It only marks positions without generating IPA.
    """

    def __init__(self):
        """Initialize position detector (no dialect needed)."""
        pass

    def detect_positions(self, syllables: List[Dict]) -> List[Dict]:
        """
        Mark word positions for each syllable.

        Args:
            syllables: List of syllable dicts from syllabification
                      Expected keys: 'syllable', 'word_index', 'position_in_word'

        Returns:
            Same syllables with added 'detected_position' key:
            - "word-initial" (first syllable in word)
            - "word-medial" (middle syllables)
            - "word-final" (last syllable in word)

        Raises:
            ValueError: If syllables format is unexpected
        """
        # Implementation details
        pass

    def _get_position(self, word_index: int, syllable_index: int,
                      total_syllables_in_word: int) -> str:
        """
        Determine position of a syllable within its word.

        Args:
            word_index: Index of syllable within word
            syllable_index: Index of syllable in overall list
            total_syllables_in_word: How many syllables in this word

        Returns:
            "word-initial", "word-medial", or "word-final"
        """
        # Implementation details
        pass
```

**Test Cases:**

Create `tests/unit/test_position_detector.py` with:

- [ ] Test detection of word-initial position (first char)
- [ ] Test detection of word-medial positions (middle chars)
- [ ] Test detection of word-final position (last char)
- [ ] Test single-character words (should be both initial and final)
- [ ] Test multi-word input (positions reset per word)
- [ ] Test with punctuation (should be skipped/handled)
- [ ] Test output format includes 'detected_position' key
- [ ] Test 5 real sentences from test dataset
- [ ] Test that PositionDetector can be instantiated with no arguments
- [ ] Test output is identical regardless of target dialect (universality)

**Dependencies:**

- Existing syllabification output format

**Estimated Effort:** 4-6 hours

**Success Verification:**

```bash
pytest tests/unit/test_position_detector.py -v
# All tests should pass
# No dialect-specific logic detected in code
```

---

### Task 1.3: Write Unit Tests for New Components

**Objective:** Ensure IPAMapper and PositionDetector are thoroughly tested and correct.

**Description:**

Expand test coverage for the two new components created in 1.1 and 1.2. This includes edge cases, performance tests, and integration scenarios.

**Acceptance Criteria:**

- [ ] `tests/unit/test_ipa_mapper.py` has at least 20 test methods
- [ ] `tests/unit/test_position_detector.py` has at least 15 test methods
- [ ] Combined code coverage for new components >= 90%
- [ ] All edge cases identified and tested
- [ ] Performance tests verify no regression
- [ ] Tests document expected behavior clearly

**Test Cases to Add:**

**For IPAMapper:**
- [ ] Test all 5 dialects load correctly and have different mappings
- [ ] Test character lookup with various positions
- [ ] Test handling of characters with no position-specific IPA
- [ ] Test handling of missing characters (error handling)
- [ ] Test batch processing of syllables
- [ ] Test preservation of gemination markers in IPA
- [ ] Test preservation of sun-letter assimilation marks
- [ ] Test emphasis/pharyngealization markers preserved
- [ ] Test X-SAMPA compatibility (IPA output is valid X-SAMPA)
- [ ] Performance: 10,000 lookups < 1 second

**For PositionDetector:**
- [ ] Test detection accuracy on 25 test sentences
- [ ] Test with undiacritized text (after diacritization)
- [ ] Test with text containing numbers/punctuation
- [ ] Test consistency: same input → same output always
- [ ] Test with mixed Arabic-English text
- [ ] Test that output integrates with existing processors

**Dependencies:**

- Task 1.1 (IPAMapper exists)
- Task 1.2 (PositionDetector exists)

**Estimated Effort:** 5-7 hours

**Success Verification:**

```bash
pytest tests/unit/test_ipa_mapper.py tests/unit/test_position_detector.py -v --cov
# All tests pass
# Coverage >= 90%
```

---

### Task 1.4: Integration Tests with Existing Pipeline

**Objective:** Verify new components work correctly alongside existing processors.

**Description:**

Create integration tests that verify:
1. New components produce correct output
2. New components can coexist with existing code
3. New components integrate properly into the pipeline

**Acceptance Criteria:**

- [ ] New file `tests/integration/test_new_components_integration.py` created
- [ ] Integration tests run existing pipeline WITH new components
- [ ] No breaking changes to existing API
- [ ] Output remains consistent with previous versions
- [ ] All 329 existing tests still pass

**Integration Test Cases:**

- [ ] IPAMapper produces same IPA as previous AllophoneProcessor for EG dialect
- [ ] PositionDetector produces same positions as existing position detection
- [ ] IPAMapper + PositionDetector together produce correct combined output
- [ ] Can call IPAMapper multiple times with different dialects on same syllables
- [ ] Full 5-sentence test with both new components
- [ ] Performance: full pipeline with new components <= 3,059 words/sec
- [ ] Both components handle the 25 test sentences correctly

**Dependencies:**

- Task 1.1 (IPAMapper)
- Task 1.2 (PositionDetector)
- Task 1.3 (Unit tests)
- Existing processors (unchanged at this point)

**Estimated Effort:** 4-6 hours

**Success Verification:**

```bash
pytest tests/integration/test_new_components_integration.py -v
pytest tests/ -v  # All 329+ tests should pass
# No performance degradation
```

---

## Phase 2: Refactor Existing Processors

### Task 2.1: Refactor GeminationProcessor - Remove Dialect Parameter

**Objective:** Make GeminationProcessor truly universal by removing unused dialect parameter.

**Description:**

Update `src/core/gemination.py` to remove the `dialect` parameter from `__init__()`. This is a minimal change since the dialect was never actually used in the class.

**Acceptance Criteria:**

- [ ] `GeminationProcessor.__init__()` no longer accepts `dialect` parameter
- [ ] All references to `self.dialect` in class removed
- [ ] Method signatures unchanged (only constructor)
- [ ] Output remains identical to previous version
- [ ] Class docstring updated to note universality
- [ ] No other methods modified

**Code Changes Required:**

**File:** `src/core/gemination.py`

**Before:**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # REMOVED
    self.shadda = 'ّ'
    # ... rest unchanged
```

**After:**
```python
def __init__(self):
    # dialect parameter REMOVED - no longer needed
    self.shadda = 'ّ'
    # ... rest unchanged
```

**Test Cases:**

- [ ] GeminationProcessor can be instantiated with no arguments
- [ ] All existing 26 gemination tests still pass
- [ ] Output is identical to previous version
- [ ] Test that processor is universal (output same regardless of target dialect)

**Dependencies:**

- None (changes only this class)

**Estimated Effort:** 1-2 hours

**Success Verification:**

```bash
pytest tests/unit/test_gemination.py -v
# All 26 tests pass
# No errors on instantiation
```

---

### Task 2.2: Refactor SunLetterProcessor - Remove Dialect Parameter

**Objective:** Make SunLetterProcessor truly universal by removing unused dialect parameter.

**Description:**

Update `src/core/sun_letters.py` to remove the `dialect` parameter from `__init__()`. Similar to Task 2.1, this is a minimal change since dialect was never used.

**Acceptance Criteria:**

- [ ] `SunLetterProcessor.__init__()` no longer accepts `dialect` parameter
- [ ] All references to `self.dialect` removed
- [ ] All sun/moon letter detection logic unchanged
- [ ] Output identical to previous version
- [ ] Class docstring updated to clarify universality
- [ ] No other methods modified

**Code Changes Required:**

**File:** `src/core/sun_letters.py`

**Before:**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # REMOVED
    self.sun_letters = {'ت', 'ث', 'د', ...}
    # ... rest unchanged
```

**After:**
```python
def __init__(self):
    # dialect parameter REMOVED
    self.sun_letters = {'ت', 'ث', 'د', ...}
    # ... rest unchanged
```

**Test Cases:**

- [ ] SunLetterProcessor can be instantiated with no arguments
- [ ] All existing 37 sun letter tests still pass
- [ ] Output identical to previous version
- [ ] Test universality: output same regardless of target dialect

**Dependencies:**

- None (changes only this class)

**Estimated Effort:** 1-2 hours

**Success Verification:**

```bash
pytest tests/unit/test_sun_letters.py -v
# All 37 tests pass
```

---

### Task 2.3: Refactor EmphaticProcessor - Remove Dialect Parameter

**Objective:** Make EmphaticProcessor truly universal by removing unused dialect parameter.

**Description:**

Update `src/core/emphatic.py` to remove the `dialect` parameter from `__init__()`. Like the previous two, dialect was never used.

**Acceptance Criteria:**

- [ ] `EmphaticProcessor.__init__()` no longer accepts `dialect` parameter
- [ ] All references to `self.dialect` removed
- [ ] Emphatic detection logic unchanged
- [ ] Output identical to previous version
- [ ] Class docstring updated
- [ ] No other methods modified

**Code Changes Required:**

**File:** `src/core/emphatic.py`

**Before:**
```python
def __init__(self, dialect: str):
    self.dialect = dialect  # REMOVED
    self.emphatics = {'ص', 'ض', 'ط', 'ظ', 'ق'}
    # ... rest unchanged
```

**After:**
```python
def __init__(self):
    # dialect parameter REMOVED
    self.emphatics = {'ص', 'ض', 'ط', 'ظ', 'ق'}
    # ... rest unchanged
```

**Test Cases:**

- [ ] EmphaticProcessor can be instantiated with no arguments
- [ ] All existing 52 emphatic tests still pass
- [ ] Output identical to previous version
- [ ] Test universality: output same regardless of target dialect

**Dependencies:**

- None (changes only this class)

**Estimated Effort:** 1-2 hours

**Success Verification:**

```bash
pytest tests/unit/test_emphatic.py -v
# All 52 tests pass
```

---

### Task 2.4: Update/Deprecate AllophoneProcessor

**Objective:** Refactor AllophoneProcessor to remove IPA generation (move to IPAMapper) and position detection (move to PositionDetector).

**Description:**

AllophoneProcessor currently conflates two responsibilities:
1. Position detection (universal) → should use PositionDetector
2. IPA lookup (dialect-specific) → should use IPAMapper

This task refactors AllophoneProcessor to either:
- **Option A:** Deprecate it entirely with clear migration path
- **Option B:** Keep it as a thin wrapper that delegates to PositionDetector + IPAMapper

**Recommendation:** Use Option B for backward compatibility.

**Acceptance Criteria:**

- [ ] AllophoneProcessor no longer generates IPA directly
- [ ] AllophoneProcessor no longer loads dialect data
- [ ] AllophoneProcessor delegates to PositionDetector for position detection
- [ ] AllophoneProcessor is marked as deprecated with clear migration path
- [ ] All existing 34 tests still pass with new implementation
- [ ] Docstring clearly explains deprecation and recommends using PositionDetector + IPAMapper
- [ ] Migration examples provided in docstring

**Code Changes Required:**

**File:** `src/core/allophones.py`

**Before:**
```python
class AllophoneProcessor:
    def __init__(self, dialect: str, master_tts_path: Optional[str] = None):
        self.dialect = dialect
        self.master_tts = load_master_tts(master_tts_path)
        self._build_allophone_maps()

    def get_ipa_for_char(self, char: str, position: str) -> str:
        # IPA lookup logic - MOVE TO IPAMapper
        ...
```

**After:**
```python
class AllophoneProcessor:
    """
    DEPRECATED: This class is deprecated.

    Use PositionDetector + IPAMapper instead:
    - PositionDetector for position detection (universal)
    - IPAMapper for IPA generation (dialect-specific)

    This class kept for backward compatibility only.

    Migration example:

        # Old (deprecated):
        processor = AllophoneProcessor(dialect="EG")
        processor.process(syllables)

        # New (recommended):
        pos_detector = PositionDetector()
        ipa_mapper = IPAMapper()

        syllables = pos_detector.detect_positions(syllables)
        ipa = ipa_mapper.map_to_ipa(syllables, dialect="EG")
    """

    def __init__(self, dialect: str, master_tts_path: Optional[str] = None):
        """
        Initialize AllophoneProcessor.

        WARNING: This class is deprecated. Use PositionDetector + IPAMapper.
        """
        import warnings
        warnings.warn(
            "AllophoneProcessor is deprecated. "
            "Use PositionDetector for position detection "
            "and IPAMapper for IPA mapping.",
            DeprecationWarning,
            stacklevel=2
        )

        self.dialect = dialect
        self.position_detector = PositionDetector()
        self.ipa_mapper = IPAMapper(master_tts_path)

    def process(self, syllables):
        """Delegate to new components."""
        syllables = self.position_detector.detect_positions(syllables)
        # Keep old behavior: attach IPA directly
        # (This enables backward compatibility)
        for i, syll in enumerate(syllables):
            ipa = self.ipa_mapper.get_ipa_for_char(
                syll.get('syllable', ''),
                self.dialect,
                syll.get('detected_position', 'default')
            )
            syll['ipa'] = ipa  # For backward compatibility
        return syllables
```

**Test Cases:**

- [ ] AllophoneProcessor still instantiates (with deprecation warning)
- [ ] All existing 34 tests pass
- [ ] Deprecation warning is raised when instantiated
- [ ] Migration examples work correctly
- [ ] Output compatible with existing code

**Dependencies:**

- Task 1.1 (IPAMapper exists)
- Task 1.2 (PositionDetector exists)

**Estimated Effort:** 3-5 hours

**Success Verification:**

```bash
pytest tests/unit/test_allophones.py -v
# All 34 tests pass
# DeprecationWarning raised
# Output compatible with existing code
```

---

### Task 2.5: Fix All Tests for Refactored Processors

**Objective:** Update all test files to work with refactored processors (no dialect parameters).

**Description:**

Update test files to reflect the removal of dialect parameters from processors. This includes:
- Remove dialect arguments from processor instantiation calls
- Add new universality tests
- Update test docstrings

**Acceptance Criteria:**

- [ ] `tests/unit/test_gemination.py` updated - no dialect parameter
- [ ] `tests/unit/test_sun_letters.py` updated - no dialect parameter
- [ ] `tests/unit/test_emphatic.py` updated - no dialect parameter
- [ ] `tests/unit/test_allophones.py` updated - deprecation warning expected
- [ ] All 149 existing processor tests still pass
- [ ] New universality tests verify output is dialect-independent
- [ ] No test failures

**Test Updates Required:**

**Pattern for all processor tests:**

**Before:**
```python
def test_gemination_detection():
    processor = GeminationProcessor(dialect="EG")  # REMOVE dialect
    result = processor.process(syllables)
    assert result[0]['has_gemination'] == True
```

**After:**
```python
def test_gemination_detection():
    processor = GeminationProcessor()  # No dialect
    result = processor.process(syllables)
    assert result[0]['has_gemination'] == True

@pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
def test_gemination_is_universal(dialect):
    """Verify gemination detection is same regardless of target dialect."""
    processor = GeminationProcessor()
    result = processor.process(syllables)
    # Result should be identical regardless of dialect
    # (dialect selection happens later in IPAMapper)
    assert result[0]['has_gemination'] == True
```

**Universality Tests to Add:**

Create `tests/unit/test_universal_processors.py` with comprehensive universality verification:

```python
class TestProcessorUniversality:
    """
    Verify that phonological processors are truly universal
    and produce identical output regardless of target dialect.
    """

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_gemination_processor_universal(self, dialect):
        """Gemination detection is identical for all dialects."""
        # Same processor instance
        processor = GeminationProcessor()
        result = processor.process(test_syllables)

        # Output should be same regardless of dialect
        # (because dialect affects IPA generation, not detection)
        assert result[0]['has_gemination'] == True
        assert result[0]['geminated_consonant'] == 'ر'

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_sun_letter_processor_universal(self, dialect):
        """Sun letter detection is identical for all dialects."""
        processor = SunLetterProcessor()
        result = processor.process(test_syllables)

        assert result[0]['sun_letter_assimilation'] == True

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_emphatic_processor_universal(self, dialect):
        """Emphatic detection is identical for all dialects."""
        processor = EmphaticProcessor()
        result = processor.process(test_syllables)

        assert result[0]['has_emphatic'] == True
        assert 'ص' in result[0]['emphatic_consonants']
```

**Dependencies:**

- Task 2.1-2.4 (processors refactored)
- Existing test structure

**Estimated Effort:** 6-8 hours

**Success Verification:**

```bash
pytest tests/unit/test_gemination.py -v
pytest tests/unit/test_sun_letters.py -v
pytest tests/unit/test_emphatic.py -v
pytest tests/unit/test_allophones.py -v
pytest tests/unit/test_universal_processors.py -v
# All tests pass, universality verified
```

---

## Phase 3: Update Main Pipeline Integration

### Task 3.1: Restructure ArabicTTS.__init__()

**Objective:** Update ArabicTTS initialization to use new components and remove dialect from universal processors.

**Description:**

Modify `src/main.py` ArabicTTS class to:
1. Instantiate universal processors WITHOUT dialect
2. Instantiate new PositionDetector
3. Instantiate new IPAMapper
4. Keep dialect as instance variable for backward compatibility

**Acceptance Criteria:**

- [ ] ArabicTTS.__init__ uses refactored processors (no dialect parameter)
- [ ] GeminationProcessor instantiated without dialect
- [ ] SunLetterProcessor instantiated without dialect
- [ ] EmphaticProcessor instantiated without dialect
- [ ] PositionDetector instantiated
- [ ] IPAMapper instantiated
- [ ] Dialect stored as instance variable for default use
- [ ] Docstring updated to explain new architecture

**Code Changes Required:**

**File:** `src/main.py`

**Before:**
```python
class ArabicTTS:
    def __init__(self, dialect: str):
        self.dialect = dialect
        self.syllabifier = ArabicSyllabifier()
        self.gemination_processor = GeminationProcessor(dialect=dialect)
        self.sun_letter_processor = SunLetterProcessor(dialect=dialect)
        self.emphatic_processor = EmphaticProcessor(dialect=dialect)
        self.allophone_processor = AllophoneProcessor(dialect=dialect)
        self.diacritizer = ...
        self.tokenizer = ...
```

**After:**
```python
class ArabicTTS:
    def __init__(self, dialect: str = "EG"):
        """
        Initialize Arabic TTS system.

        Args:
            dialect: Default dialect for text processing.
                    Individual calls can override this via process_text(dialect="MSA").
                    Currently supports: "EG", "MSA", "Gulf", "Levantine", "Maghrebi"

        Architecture:
            Steps 1-4 are universal (no dialect):
            1. Diacritization
            2. Tokenization
            3. Syllabification
            4. Phonological processing (gemination, sun letters, positions, emphatics)

            Step 5 is dialect-specific:
            5. IPAMapper (converts processed syllables to dialect-specific IPA)
        """
        self.dialect = dialect

        # Universal processors (no dialect dependency)
        self.syllabifier = ArabicSyllabifier()
        self.gemination_processor = GeminationProcessor()  # No dialect
        self.sun_letter_processor = SunLetterProcessor()   # No dialect
        self.emphatic_processor = EmphaticProcessor()      # No dialect
        self.position_detector = PositionDetector()        # No dialect

        # Diacritization
        self.diacritizer = ...

        # Dialect-specific component (loaded once, used for any dialect)
        self.ipa_mapper = IPAMapper()  # All dialects loaded at init
```

**Test Cases:**

- [ ] ArabicTTS can be instantiated with dialect parameter
- [ ] ArabicTTS can be instantiated with default dialect
- [ ] All processors are instantiated correctly
- [ ] No errors during initialization
- [ ] ipa_mapper is ready for any dialect
- [ ] Instance maintains dialect state
- [ ] Can process text immediately after init

**Dependencies:**

- Task 2.1-2.4 (processors refactored)
- Task 1.1 (IPAMapper)
- Task 1.2 (PositionDetector)

**Estimated Effort:** 2-3 hours

**Success Verification:**

```bash
python3 -c "from src.main import ArabicTTS; tts = ArabicTTS(dialect='EG'); print('OK')"
# Should print OK with no errors
```

---

### Task 3.2: Update apply_phonological_rules() Method

**Objective:** Refactor the main pipeline method to use refactored processors.

**Description:**

Update the `apply_phonological_rules()` method in ArabicTTS to:
1. Remove dialect parameter passing to processors
2. Use PositionDetector instead of AllophoneProcessor for position detection
3. Ensure output format is compatible with IPAMapper input

**Acceptance Criteria:**

- [ ] `apply_phonological_rules()` method refactored
- [ ] No longer passes dialect to universal processors
- [ ] Uses PositionDetector instead of AllophoneProcessor
- [ ] Output format unchanged (compatible with IPAMapper)
- [ ] Method docstring updated
- [ ] All processor results merged correctly

**Code Changes Required:**

**File:** `src/main.py`

**Before:**
```python
def apply_phonological_rules(self, syllables: List[Dict]) -> List[Dict]:
    """Apply all phonological rules in order."""
    # Step 1: Gemination
    syllables = self.gemination_processor.process(syllables)

    # Step 2: Sun letters
    syllables = self.sun_letter_processor.process(syllables)

    # Step 3: Allophones (includes position detection + IPA)
    syllables = self.allophone_processor.process(syllables)

    # Step 4: Emphatic spread
    syllables = self.emphatic_processor.process(syllables)

    return syllables
```

**After:**
```python
def apply_phonological_rules(self, syllables: List[Dict]) -> List[Dict]:
    """
    Apply universal phonological rules to syllables.

    This method applies all phonological rules that are identical
    across all Arabic dialects. Dialect-specific IPA mapping happens
    in a separate step (see process_text).

    Steps applied:
    1. Gemination detection (shadda)
    2. Sun/moon letter assimilation detection
    3. Position detection (word-initial, word-medial, word-final)
    4. Emphatic consonant detection and pharyngealization marking

    Note: These rules are universal. IPA generation (dialect-specific)
    happens separately in IPAMapper.step 5.
    """
    # Step 1: Gemination (detect shadda, mark for doubling)
    syllables = self.gemination_processor.process(syllables)

    # Step 2: Sun letters (detect al + sun, mark for assimilation)
    syllables = self.sun_letter_processor.process(syllables)

    # Step 3: Position detection (initial/medial/final)
    # NOTE: No longer using AllophoneProcessor for this
    syllables = self.position_detector.detect_positions(syllables)

    # Step 4: Emphatic spread (detect emphaics, mark pharyngealization)
    syllables = self.emphatic_processor.process(syllables)

    return syllables
```

**Test Cases:**

- [ ] apply_phonological_rules() processes test syllables correctly
- [ ] Output includes gemination markers
- [ ] Output includes sun-letter markers
- [ ] Output includes detected_position for each syllable
- [ ] Output includes emphatic markers
- [ ] Output format compatible with IPAMapper input
- [ ] All 5 test sentences process without error

**Dependencies:**

- Task 3.1 (ArabicTTS.__init__ refactored)
- Task 2.1-2.4 (processors refactored)

**Estimated Effort:** 2-3 hours

**Success Verification:**

```bash
pytest tests/integration/test_complete_pipeline.py -v
# Apply phonological rules tests pass
```

---

### Task 3.3: Add IPAMapper Call in Pipeline

**Objective:** Integrate IPAMapper into the main processing pipeline at the correct point (after universal processing, before audio generation).

**Description:**

Update the main `process_text()` method to call IPAMapper after phonological rules and before audio generation. This is where dialect selection happens.

**Acceptance Criteria:**

- [ ] `process_text()` method calls IPAMapper after universal processing
- [ ] IPAMapper receives processed syllables from `apply_phonological_rules()`
- [ ] IPAMapper uses specified dialect (or default)
- [ ] IPAMapper output is IPA string
- [ ] IPA is passed to X-SAMPA converter
- [ ] Method supports both positional and keyword dialect argument
- [ ] Dialect can be overridden per call or use default
- [ ] No errors in pipeline integration

**Code Changes Required:**

**File:** `src/main.py`

**Before:**
```python
def process_text(self, text: str, dialect: Optional[str] = None) -> Dict:
    """Process Arabic text."""
    dialect = dialect or self.dialect

    # ... steps 1-4: universal processing ...

    # Step 5: IPA generation (dialect-specific)
    # PROBLEM: This happens in AllophoneProcessor.process()
    # which conflates position detection + IPA generation

    # Steps 6-7: audio generation
    x_sampa = self.espeak.ipa_to_xsampa(ipa)
    audio = self.espeak.generate_audio(x_sampa)

    return {...}
```

**After:**
```python
def process_text(self, text: str, dialect: Optional[str] = None) -> Dict:
    """
    Process Arabic text to speech.

    Pipeline:
    1. Diacritization (universal)
    2. Tokenization (universal)
    3. Syllabification (universal)
    4. Phonological processing (universal)
    5. IPA mapping (DIALECT SELECTED HERE)
    6. X-SAMPA conversion
    7. Audio generation

    Args:
        text: Arabic text to process
        dialect: Target dialect (optional, uses self.dialect if not specified)

    Returns:
        Dict with processed results including 'ipa' and 'audio'
    """
    # Use specified dialect or default
    target_dialect = dialect or self.dialect

    # Validate dialect
    if target_dialect not in ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"]:
        raise ValueError(f"Unsupported dialect: {target_dialect}")

    # ========== STEPS 1-4: UNIVERSAL PROCESSING ==========
    # (No dialect dependency)

    # Step 1: Diacritization
    diacritized = self.diacritizer.add_diacritics(text)

    # Step 2: Tokenization
    tokens = self.tokenizer.tokenize(diacritized)

    # Step 3: Syllabification
    syllables = self.syllabifier.syllabify_tokens(tokens)

    # Step 4: Phonological processing (universal rules)
    syllables = self.apply_phonological_rules(syllables)

    # ========== STEP 5: DIALECT-SPECIFIC IPA MAPPING ==========
    # DIALECT SELECTION HAPPENS HERE (ONLY PLACE)

    ipa = self.ipa_mapper.map_to_ipa(syllables, dialect=target_dialect)

    # ========== STEPS 6-7: AUDIO GENERATION ==========

    # Step 6: X-SAMPA conversion
    x_sampa = self.espeak.ipa_to_xsampa(ipa)

    # Step 7: Audio generation
    audio = self.espeak.generate_audio(x_sampa)

    # Build result
    return {
        'text': text,
        'diacritized': diacritized,
        'syllables': syllables,
        'ipa': ipa,
        'x_sampa': x_sampa,
        'audio': audio,
        'dialect': target_dialect,
        'processing_time': ...
    }
```

**Test Cases:**

- [ ] process_text() calls IPAMapper
- [ ] Can switch dialect between calls without recreating pipeline
- [ ] Default dialect used if not specified
- [ ] Dialect override works correctly
- [ ] Same text produces different IPA for different dialects
- [ ] All 25 test sentences process correctly
- [ ] Error handling for invalid dialects
- [ ] Pipeline is truly separated (universal vs dialect-specific)

**Dependencies:**

- Task 3.1 (ArabicTTS refactored)
- Task 3.2 (apply_phonological_rules updated)
- Task 1.1 (IPAMapper)

**Estimated Effort:** 3-4 hours

**Success Verification:**

```bash
python3 << 'EOF'
from src.main import ArabicTTS

tts = ArabicTTS(dialect="EG")

# Test 1: Default dialect
result_eg = tts.process_text("صباح الخير")
print(f"EG IPA: {result_eg['ipa']}")

# Test 2: Override dialect
result_msa = tts.process_text("صباح الخير", dialect="MSA")
print(f"MSA IPA: {result_msa['ipa']}")

# Verify they're different
assert result_eg['ipa'] != result_msa['ipa'], "Different dialects should produce different IPA"
print("✓ Dialect switching works!")
EOF
```

---

### Task 3.4: Maintain Backward Compatibility

**Objective:** Ensure existing code using ArabicTTS continues to work without modification.

**Description:**

Verify that all changes maintain backward compatibility with existing API and that no breaking changes affect users of the library.

**Acceptance Criteria:**

- [ ] Existing code using `ArabicTTS(dialect="EG")` works unchanged
- [ ] Existing `process_text(text)` calls work unchanged
- [ ] All 329 existing tests pass without modification
- [ ] Deprecation warnings are clear but not blocking
- [ ] Migration guide provided for new architecture (optional but recommended)

**Test Cases:**

- [ ] Legacy code example 1: `ArabicTTS("EG").process_text("صباح")`
- [ ] Legacy code example 2: `ArabicTTS().process_text("صباح")`
- [ ] Legacy code example 3: Integration with existing Flask app
- [ ] New code example 1: `tts.process_text("صباح", dialect="MSA")`
- [ ] New code example 2: Using PositionDetector directly
- [ ] New code example 3: Using IPAMapper directly

**Documentation:**

Create migration guide explaining:
- Old architecture vs new architecture
- Why changes were made
- How to update code (minimal for most users)
- Examples of new dialect-switching capability

**Dependencies:**

- Task 3.1-3.3 (pipeline updated)
- All previous Phase 3 tasks

**Estimated Effort:** 2-3 hours

**Success Verification:**

```bash
pytest tests/ -v
# All 329+ tests pass
# No breaking changes to API
```

---

## Phase 4: Testing, Validation, and Documentation

### Task 4.1: Create Universality Verification Tests

**Objective:** Create comprehensive tests proving all processors are truly universal.

**Description:**

Expand test suite with dedicated universality verification tests. These tests prove that phonological processors produce identical output regardless of which dialect will eventually be used.

**Acceptance Criteria:**

- [ ] New file `tests/unit/test_universal_processors.py` created with comprehensive tests
- [ ] Tests parametrized across all 5 dialects
- [ ] Tests prove gemination is universal
- [ ] Tests prove sun-letter detection is universal
- [ ] Tests prove position detection is universal
- [ ] Tests prove emphatic detection is universal
- [ ] Tests show IPA differs by dialect (in IPAMapper)
- [ ] All tests pass

**Test Cases to Implement:**

```python
class TestGeminationUniversality:
    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_gemination_identical_across_dialects(self, dialect):
        """Gemination markers should be identical regardless of dialect."""
        processor = GeminationProcessor()
        result = processor.process(test_syllables_with_shadda)

        # These assertions should be true regardless of dialect value
        assert result[0]['has_gemination'] == True
        assert result[0]['geminated_consonant'] == 'ر'
        # ... dialect doesn't affect detection ...

class TestSunLetterUniversality:
    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_sun_letter_identical_across_dialects(self, dialect):
        """Sun letter detection should be identical regardless of dialect."""
        processor = SunLetterProcessor()
        result = processor.process(test_syllables_with_sun_letter)

        assert result[0]['sun_letter_assimilation'] == True
        # ... dialect doesn't affect detection ...

class TestPositionDetectionUniversality:
    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_position_identical_across_dialects(self, dialect):
        """Position detection should be identical regardless of dialect."""
        detector = PositionDetector()
        result = detector.detect_positions(test_syllables)

        assert result[0]['detected_position'] == 'word-initial'
        # ... dialect doesn't affect position detection ...

class TestEmphaticUniversality:
    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_emphatic_identical_across_dialects(self, dialect):
        """Emphatic detection should be identical regardless of dialect."""
        processor = EmphaticProcessor()
        result = processor.process(test_syllables_with_emphatic)

        assert result[0]['has_emphatic'] == True
        assert 'ص' in result[0]['emphatic_consonants']
        # ... dialect doesn't affect detection ...

class TestIPAVarianceByDialect:
    """Verify that ONLY IPA generation differs by dialect, not detection."""

    def test_same_processed_syllables_different_ipa_by_dialect(self):
        """
        After universal processing, same syllables should produce
        different IPA based on dialect selection in IPAMapper.
        """
        # Process universally (no dialect)
        syllables = universal_process("جمل")  # camel

        # Same input, different dialects
        mapper = IPAMapper()
        eg_ipa = mapper.map_to_ipa(syllables, "EG")
        msa_ipa = mapper.map_to_ipa(syllables, "MSA")

        # Detection is same
        assert syllables[0]['detected_position'] == 'word-initial'
        assert syllables[0]['sun_letter_assimilation'] == False

        # But IPA differs
        # EG: ج = /g/, MSA: ج = /dʒ/ or /d͡ʒ/
        assert eg_ipa != msa_ipa
```

**Dependencies:**

- Task 2.1-2.5 (processors refactored)
- Task 1.1-1.3 (new components created)

**Estimated Effort:** 5-7 hours

**Success Verification:**

```bash
pytest tests/unit/test_universal_processors.py -v
# All universality tests pass
# Parametrization covers all 5 dialects
```

---

### Task 4.2: Dialect-Specific Integration Tests

**Objective:** Create comprehensive integration tests for each supported dialect.

**Description:**

Create integration tests that verify the full pipeline works correctly for each supported dialect, proving that switching dialects produces appropriate output differences.

**Acceptance Criteria:**

- [ ] New file `tests/integration/test_dialect_integration.py` created
- [ ] Tests cover all 5 supported dialects
- [ ] Tests verify different dialects produce different IPA for same input
- [ ] Tests verify phonological rules are applied consistently across dialects
- [ ] Tests validate output format is correct for each dialect
- [ ] All 25 test sentences process correctly for each dialect
- [ ] All tests pass

**Test Cases:**

```python
class TestDialectIntegration:
    """Integration tests for each dialect."""

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_full_pipeline_each_dialect(self, dialect):
        """Verify full pipeline works for each dialect."""
        tts = ArabicTTS(dialect=dialect)

        for sentence in test_dataset:
            result = tts.process_text(sentence['arabic'])

            assert result['dialect'] == dialect
            assert 'ipa' in result
            assert 'x_sampa' in result
            assert 'audio' in result
            assert len(result['ipa']) > 0

    def test_dialect_switching_same_instance(self):
        """Verify dialect can be switched between calls."""
        tts = ArabicTTS(dialect="EG")

        # Same text, different dialects
        result_eg = tts.process_text("صباح", dialect="EG")
        result_msa = tts.process_text("صباح", dialect="MSA")

        # IPA should differ
        assert result_eg['ipa'] != result_msa['ipa']

        # Processing should handle both correctly
        assert len(result_eg['ipa']) > 0
        assert len(result_msa['ipa']) > 0

    def test_same_universal_processing_different_ipa(self):
        """
        Verify that universal processing is identical
        but IPA differs by dialect.
        """
        tts = ArabicTTS()

        # Process same text with different dialects
        result_eg = tts.process_text("الشمس", dialect="EG")
        result_msa = tts.process_text("الشمس", dialect="MSA")

        # Syllables should be the same (universal processing)
        assert len(result_eg['syllables']) == len(result_msa['syllables'])

        # But IPA differs
        assert result_eg['ipa'] != result_msa['ipa']

    @pytest.mark.parametrize("dialect", ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"])
    def test_complete_test_dataset_each_dialect(self, dialect):
        """Process all 25 test sentences with each dialect."""
        tts = ArabicTTS(dialect=dialect)

        for i, sentence in enumerate(complete_test_dataset):
            result = tts.process_text(sentence['arabic'])

            # Verify results
            assert result['dialect'] == dialect
            assert 'ipa' in result
            assert len(result['ipa']) > 0

            # Verify phonological markers detected
            has_any_feature = any(
                syll.get('has_gemination') or
                syll.get('sun_letter_assimilation') or
                syll.get('has_emphatic')
                for syll in result['syllables']
            )
            # Most test sentences should have at least one feature
            if i in expected_feature_indices:
                assert has_any_feature
```

**Dependencies:**

- Task 3.1-3.4 (pipeline integrated)
- Task 4.1 (universality tests)

**Estimated Effort:** 5-7 hours

**Success Verification:**

```bash
pytest tests/integration/test_dialect_integration.py -v
# All dialect-specific tests pass
# Switching works correctly
```

---

### Task 4.3: Performance Benchmarks - No Regression

**Objective:** Verify that refactoring doesn't cause performance regression.

**Description:**

Create comprehensive performance tests verifying that:
1. Processing throughput maintained (3,059+ words/sec)
2. No new bottlenecks introduced
3. IPAMapper lookup is efficient
4. PositionDetector adds minimal overhead

**Acceptance Criteria:**

- [ ] Performance test file `tests/unit/test_performance_refactored.py` created
- [ ] Throughput >= 3,059 words/second (no regression)
- [ ] Syllabification speed unchanged
- [ ] IPAMapper lookups efficient (O(1) with caching)
- [ ] Position detection adds < 5% overhead
- [ ] Full pipeline throughput maintained
- [ ] Memory usage stable

**Performance Test Cases:**

```python
class TestPerformanceAfterRefactoring:
    """Verify no performance regression after refactoring."""

    def test_syllabification_performance(self):
        """Syllabification should maintain performance."""
        syllabifier = ArabicSyllabifier()
        large_text = generate_large_text(10000)  # 10k words

        start = time.time()
        for word in large_text.split():
            syllabifier.syllabify_word(word)
        elapsed = time.time() - start

        words_per_sec = 10000 / elapsed
        assert words_per_sec >= 3000  # No significant regression

    def test_ipa_mapper_lookup_performance(self):
        """IPAMapper lookups should be O(1) and fast."""
        mapper = IPAMapper()

        chars = ['أ', 'ب', 'ت', 'ث', 'ج'] * 1000  # 5000 lookups

        start = time.time()
        for char in chars:
            mapper.get_ipa_for_char(char, "EG")
        elapsed = time.time() - start

        # 5000 lookups in < 100ms (50 microsec per lookup)
        assert elapsed < 0.1

    def test_position_detector_performance(self):
        """Position detection should add minimal overhead."""
        detector = PositionDetector()

        syllables = generate_test_syllables(10000)

        start = time.time()
        detector.detect_positions(syllables)
        elapsed = time.time() - start

        # 10k syllables should process in < 50ms
        assert elapsed < 0.05

    def test_full_pipeline_throughput(self):
        """Full pipeline should maintain throughput."""
        tts = ArabicTTS(dialect="EG")

        test_sentences = [
            "صباح الخير",
            "السلام عليكم",
            "كيف حالك",
            # ... 22 more sentences from test dataset
        ] * 25  # 750 sentences

        start = time.time()
        for sentence in test_sentences:
            tts.process_text(sentence)
        elapsed = time.time() - start

        total_words = sum(len(s.split()) for s in test_sentences)
        words_per_sec = total_words / elapsed

        # Should maintain > 3000 words/sec
        assert words_per_sec > 3000
```

**Dependencies:**

- Task 3.1-3.4 (pipeline integrated)
- All Phase 2 tasks

**Estimated Effort:** 4-6 hours

**Success Verification:**

```bash
pytest tests/unit/test_performance_refactored.py -v -s
# All performance benchmarks pass
# No regression verified
```

---

### Task 4.4: Full Pipeline Validation with Test Dataset

**Objective:** Comprehensive end-to-end validation of entire refactored system.

**Description:**

Run the complete refactored system through the full 25-sentence test dataset, verifying:
1. All sentences process correctly
2. Output quality maintained
3. Phonological rules applied correctly
4. All dialects supported

**Acceptance Criteria:**

- [ ] All 25 test sentences process without errors
- [ ] Output format matches expected structure
- [ ] Phonological features detected correctly
- [ ] IPA generation works for all dialects
- [ ] Audio generation works end-to-end
- [ ] All existing tests still pass (329+)
- [ ] Documentation validates against test results

**Validation Test Cases:**

```python
class TestCompleteValidation:
    """Complete end-to-end validation of refactored system."""

    def test_all_test_sentences_all_dialects(self):
        """Process all 25 sentences with all 5 dialects."""
        for dialect in ["EG", "MSA", "Gulf", "Levantine", "Maghrebi"]:
            tts = ArabicTTS(dialect=dialect)

            for i, sentence in enumerate(complete_test_dataset):
                result = tts.process_text(sentence['arabic'])

                # Verify all required fields
                assert 'text' in result
                assert 'ipa' in result
                assert 'x_sampa' in result
                assert 'syllables' in result
                assert 'dialect' in result

                # Verify content
                assert result['text'] == sentence['arabic']
                assert result['dialect'] == dialect
                assert len(result['ipa']) > 0

    def test_phonological_features_detected(self):
        """Verify phonological features are detected correctly."""
        tts = ArabicTTS(dialect="EG")

        # Test gemination
        result_mudarris = tts.process_text("مُدَرِّس")
        assert any(s.get('has_gemination') for s in result_mudarris['syllables'])

        # Test sun letters
        result_shams = tts.process_text("الشمس")
        assert any(s.get('sun_letter_assimilation') for s in result_shams['syllables'])

        # Test emphatics
        result_sabah = tts.process_text("صباح")
        assert any(s.get('has_emphatic') for s in result_sabah['syllables'])

    def test_regression_all_existing_tests_pass(self):
        """Verify all 329+ existing tests still pass."""
        # This is tested via pytest discovery
        # Documented here for completeness
        import subprocess
        result = subprocess.run(['pytest', 'tests/', '-v'], capture_output=True)
        assert result.returncode == 0, "Not all tests pass"

    def test_output_compatibility(self):
        """Verify output format is compatible with existing code."""
        tts = ArabicTTS(dialect="EG")
        result = tts.process_text("صباح الخير")

        # Verify compatibility with existing audio generation
        assert isinstance(result['ipa'], str)
        assert isinstance(result['x_sampa'], str)
        assert isinstance(result['syllables'], list)

        # Verify syllable format
        for syll in result['syllables']:
            assert 'syllable' in syll or 'arabic' in syll
            assert 'detected_position' in syll
```

**Dependencies:**

- All previous Phase 4 tasks
- All Phase 1-3 tasks

**Estimated Effort:** 4-6 hours

**Success Verification:**

```bash
pytest tests/integration/test_validation.py -v
pytest tests/ -v  # All 329+ tests
# All validations pass
# No regressions
```

---

## Summary Task List

### Phase 1: Create New Components (Week 1)
- [ ] Task 1.1: Create IPAMapper Class (6-8 hrs)
- [ ] Task 1.2: Create PositionDetector Class (4-6 hrs)
- [ ] Task 1.3: Write Unit Tests for Both (5-7 hrs)
- [ ] Task 1.4: Integration Tests (4-6 hrs)
- **Phase 1 Total:** 19-27 hours

### Phase 2: Refactor Existing Processors (Week 1-2)
- [ ] Task 2.1: Refactor GeminationProcessor (1-2 hrs)
- [ ] Task 2.2: Refactor SunLetterProcessor (1-2 hrs)
- [ ] Task 2.3: Refactor EmphaticProcessor (1-2 hrs)
- [ ] Task 2.4: Update/Deprecate AllophoneProcessor (3-5 hrs)
- [ ] Task 2.5: Fix All Tests for Refactored Processors (6-8 hrs)
- **Phase 2 Total:** 12-19 hours

### Phase 3: Update Main Pipeline (Week 2-3)
- [ ] Task 3.1: Restructure ArabicTTS.__init__() (2-3 hrs)
- [ ] Task 3.2: Update apply_phonological_rules() (2-3 hrs)
- [ ] Task 3.3: Add IPAMapper Call in Pipeline (3-4 hrs)
- [ ] Task 3.4: Maintain Backward Compatibility (2-3 hrs)
- **Phase 3 Total:** 9-13 hours

### Phase 4: Testing, Validation, Documentation (Week 3-4)
- [ ] Task 4.1: Create Universality Verification Tests (5-7 hrs)
- [ ] Task 4.2: Dialect-Specific Integration Tests (5-7 hrs)
- [ ] Task 4.3: Performance Benchmarks (4-6 hrs)
- [ ] Task 4.4: Full Pipeline Validation (4-6 hrs)
- **Phase 4 Total:** 18-26 hours

### Grand Total: 58-85 hours (2-3 weeks at 30-40 hrs/week)

---

## Success Criteria Checklist

### Functional Requirements Met
- [ ] All phonological processors are universal (no dialect parameter)
- [ ] IPAMapper is dedicated dialect-aware component
- [ ] PositionDetector is universal position detection component
- [ ] Dialect selection happens only in IPAMapper
- [ ] Pipeline can switch dialects between calls
- [ ] All 329+ existing tests pass
- [ ] Backward compatibility maintained

### Non-Functional Requirements Met
- [ ] Performance: >= 3,059 words/second (no regression)
- [ ] Code quality: Improved, better separation of concerns
- [ ] Maintainability: Single point of dialect selection
- [ ] Documentation: Complete with architecture diagrams
- [ ] Test coverage: 100% for new components, >90% overall

### Architecture Requirements Met
- [ ] Universal processing phase (steps 1-4) identified
- [ ] Dialect-specific phase (step 5) isolated
- [ ] Clear responsibility separation in components
- [ ] New architecture diagram documented
- [ ] Old and new components coexist during migration

---

## Risk Mitigation

### Risk 1: Breaking Existing Code
**Mitigation:** Maintain backward compatibility through deprecation warnings and wrapper classes.

### Risk 2: Performance Regression
**Mitigation:** Comprehensive performance tests at each phase.

### Risk 3: Missing Edge Cases
**Mitigation:** Extensive test coverage including universality verification.

### Risk 4: Integration Failures
**Mitigation:** Non-breaking Phase 1 allows validation before refactoring.

---

## Dependencies Between Tasks

```
Phase 1:
├── 1.1 (IPAMapper)
├── 1.2 (PositionDetector)
├── 1.3 (depends on 1.1, 1.2)
└── 1.4 (depends on 1.1, 1.2, 1.3)

Phase 2 (depends on Phase 1):
├── 2.1 (GeminationProcessor)
├── 2.2 (SunLetterProcessor)
├── 2.3 (EmphaticProcessor)
├── 2.4 (depends on 1.1, 1.2)
└── 2.5 (depends on 2.1, 2.2, 2.3, 2.4)

Phase 3 (depends on Phase 1, 2):
├── 3.1 (depends on 2.1, 2.2, 2.3, 1.2)
├── 3.2 (depends on 3.1)
├── 3.3 (depends on 3.1, 3.2, 1.1)
└── 3.4 (depends on 3.1, 3.2, 3.3)

Phase 4 (depends on Phase 2, 3):
├── 4.1 (depends on 2.1-2.5)
├── 4.2 (depends on 3.1-3.4)
├── 4.3 (depends on 3.1-3.4)
└── 4.4 (depends on 4.1, 4.2, 4.3)
```

---

**Document Version:** 1.0
**Created:** December 14, 2025
**Last Updated:** December 14, 2025
**Status:** Ready for Implementation

---

**END OF TASK LIST**
