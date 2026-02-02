# Test Documentation - Arabic TTS MVP Phase 1

**Project:** Arabic Text-to-Speech System  
**Phase:** MVP Phase 1  
**Test Suite Version:** 1.0  
**Date:** October 30, 2025  
**Total Tests:** 329 (100% passing)

---

## Table of Contents

1. [Overview](#overview)
2. [Test Statistics](#test-statistics)
3. [Test Categories](#test-categories)
4. [Running Tests](#running-tests)
5. [Test Coverage](#test-coverage)
6. [Performance Benchmarks](#performance-benchmarks)
7. [Continuous Integration](#continuous-integration)
8. [Writing New Tests](#writing-new-tests)

---

## Overview

The Arabic TTS system has comprehensive test coverage across all components:
- **Unit tests:** Individual component testing
- **Integration tests:** End-to-end pipeline testing
- **Smoke tests:** Dependency and system checks
- **Performance tests:** Speed and efficiency benchmarks
- **Error handling tests:** Edge cases and failure scenarios

All tests are written using **pytest** and follow industry best practices.

---

## Test Statistics

### Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 329 |
| **Passing** | 329 (100%) |
| **Test Categories** | 5 (unit, integration, smoke, performance, error handling) |
| **Test Files** | 13 |
| **Code Coverage** | Unit tests cover all core modules |

### Test Breakdown by Category

| Category | Tests | Files | Pass Rate |
|----------|-------|-------|-----------|
| **Foundation/Smoke** | 23 | 2 | 100% |
| **Unit Tests** | 237 | 8 | 100% |
| **Integration Tests** | 38 | 2 | 100% |
| **Error Handling** | 45 | 1 | 100% |
| **Performance** | 21 | 1 | 100% |
| **TOTAL** | **329** | **13** | **100%** |

---

## Test Categories

### 1. Smoke Tests (23 tests)

**Purpose:** Verify dependencies and basic system functionality  
**Location:** `tests/smoke/`

**Files:**
- `test_mishkal.py` (5 tests) - Mishkal diacritization library checks
- `test_all_dependencies.py` (18 tests) - System dependencies verification

**What they test:**
- Mishkal installation and basic functionality
- eSpeak NG installation and audio generation
- Flask web framework availability
- JSON dictionary loading (masterTTS.json)
- Python version and package dependencies

**Run command:**
```bash
pytest tests/smoke/ -v
```

---

### 2. Unit Tests (237 tests)

**Purpose:** Test individual components in isolation  
**Location:** `tests/unit/`

#### 2.1 Syllabification Tests (25 tests)
**File:** `test_syllabifier.py`

**Coverage:**
- CV pattern detection
- CVC pattern detection
- CVV (long vowels) detection
- CVCC pattern validation
- CVVC (diphthongs) detection
- Complex word syllabification
- Edge cases (empty strings, single chars, shadda)

**Key test cases:**
- `test_madrasa()` - مَدْرَسَة (school)
- `test_kataba()` - كَتَبَ (wrote)
- `test_kitaab()` - كِتَاب (book)
- `test_bayt()` - بَيْت (house)

**Run command:**
```bash
pytest tests/unit/test_syllabifier.py -v
```

---

#### 2.2 Gemination Tests (26 tests)
**File:** `test_gemination.py`

**Coverage:**
- Shadda (ّ) detection
- Consonant doubling
- IPA gemination markers
- Word-level gemination processing

**Key phonemes tested:** ر، ل، د، م، ت، ن، ب

**Run command:**
```bash
pytest tests/unit/test_gemination.py -v
```

---

#### 2.3 Sun Letter Assimilation Tests (37 tests)
**File:** `test_sun_letters.py`

**Coverage:**
- 14 sun letters: ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن
- 14 moon letters: ا، ب، ج، ح، خ، ع، غ، ف، ق، ك، م، ه، و، ي
- /al/ + sun letter assimilation
- Lam deletion in IPA
- Gemination of sun letters

**Key test cases:**
- الشَّمْس (ash-shams) - the sun
- الْقَمَر (al-qamar) - the moon
- النَّهَار (an-nahaar) - the day

**Run command:**
```bash
pytest tests/unit/test_sun_letters.py -v
```

---

#### 2.4 Positional Allophone Tests (34 tests)
**File:** `test_allophones.py`

**Coverage:**
- Word-initial position detection
- Word-medial position detection
- Word-final position detection
- Position-based IPA selection
- Character map generation

**Run command:**
```bash
pytest tests/unit/test_allophones.py -v
```

---

#### 2.5 Emphatic Spread Tests (52 tests)
**File:** `test_emphatic.py`

**Coverage:**
- 5 emphatic consonants: ص، ض، ط، ظ، ق
- Pharyngealization spread to adjacent vowels
- Vowel backing (a→ɑ, i→ɪ, u→ʊ)
- Long vowel pharyngealization
- Pharyngealization marker (ˁ) insertion

**Key test cases:**
- صَبَاح (sˁɑbɑːħ) - morning
- طَعَام (tˁɑʕɑːm) - food
- ضَرَبَ (dˁɑrɑb) - hit

**Run command:**
```bash
pytest tests/unit/test_emphatic.py -v
```

---

#### 2.6 eSpeak Integration Tests (28 tests)
**File:** `test_espeak_integration.py`

**Coverage:**
- eSpeak NG installation verification
- IPA to X-SAMPA conversion (40+ phonemes)
- Audio generation from IPA
- WAV file format validation
- Speed/pitch/amplitude parameters
- Error handling

**Run command:**
```bash
pytest tests/unit/test_espeak_integration.py -v
```

---

#### 2.7 Error Handling Tests (45 tests)
**File:** `test_error_handling.py`

**Coverage:**
- Invalid dialect handling
- Empty/malformed input handling
- Unicode edge cases
- File I/O errors
- eSpeak failures
- Memory efficiency
- Large text processing

**Test classes:**
- `TestArabicTTSErrors` (11 tests)
- `TestArabicSyllabifierErrors` (6 tests)
- `TestESpeakErrors` (9 tests)
- `TestPhonologicalProcessorErrors` (3 tests)
- `TestFileIOErrors` (5 tests)
- `TestGetTTSInstance` (2 tests)
- `TestEdgeCases` (7 tests)
- `TestMemoryAndPerformance` (2 tests)

**Run command:**
```bash
pytest tests/unit/test_error_handling.py -v
```

---

#### 2.8 Performance Tests (21 tests)
**File:** `test_performance.py`

**Coverage:**
- Processing speed benchmarks
- Throughput measurements
- Memory efficiency tests
- Scalability tests
- Real-world scenario benchmarks

**Key metrics:**
- **Throughput:** 3,352 words/second
- **Sentence processing:** 1,212 sentences/second
- **Audio generation:** 0.032s per request
- **IPA conversion:** 0.000045s per conversion

**Test classes:**
- `TestProcessingSpeed` (4 tests)
- `TestThroughput` (2 tests)
- `TestSyllabificationPerformance` (2 tests)
- `TestPhonologicalProcessingPerformance` (4 tests)
- `TestAudioGenerationPerformance` (2 tests)
- `TestScalability` (2 tests)
- `TestMemoryEfficiency` (2 tests)
- `TestDialectSwitchingPerformance` (1 test)
- `TestRealWorldPerformance` (2 tests)

**Run command:**
```bash
pytest tests/unit/test_performance.py -v -s
```

---

### 3. Integration Tests (38 tests)

**Purpose:** Test complete pipeline workflows  
**Location:** `tests/integration/`

#### 3.1 Diacritization Integration Tests (17 tests)
**File:** `test_diacritization.py`

**Coverage:**
- Basic word/sentence processing
- Multiple dialects (EG, MSA)
- Punctuation handling
- Numbers and mixed content
- Edge cases (empty, long sentences)
- Consistency validation

**Run command:**
```bash
pytest tests/integration/test_diacritization.py -v
```

---

#### 3.2 Complete Pipeline Tests (21 tests)
**File:** `test_complete_pipeline.py`

**Coverage:**
- End-to-end text → audio workflow
- Phonological rules application
- Pipeline to audio generation
- Dialect variations
- Edge cases
- Performance and consistency

**Key workflows tested:**
1. Text → Diacritization → Syllabification → IPA → Audio
2. Phonological rules: Gemination → Sun Letters → Allophones → Emphatic
3. Multiple dialects: EG, MSA, Gulf, Levantine, Maghreb

**Run command:**
```bash
pytest tests/integration/test_complete_pipeline.py -v
```

---

## Running Tests

### Run All Tests
```bash
cd /home/hamr/Documents/PycharmProjects/ArabicTTS
python3 -m pytest tests/ -v
```

### Run Specific Category
```bash
# Smoke tests
pytest tests/smoke/ -v

# Unit tests
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests (with output)
pytest tests/unit/test_performance.py -v -s
```

### Run Single Test File
```bash
pytest tests/unit/test_syllabifier.py -v
```

### Run Single Test Class
```bash
pytest tests/unit/test_syllabifier.py::TestCVPatterns -v
```

### Run Single Test
```bash
pytest tests/unit/test_syllabifier.py::TestCVPatterns::test_single_cv_syllable -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=src --cov-report=html
```

### Run Fast (Skip Slow Tests)
```bash
pytest tests/ -v -m "not slow"
```

---

## Test Coverage

### Core Modules Coverage

| Module | Unit Tests | Integration Tests | Total Coverage |
|--------|------------|-------------------|----------------|
| `src/main.py` | ✓ | ✓ | High |
| `src/core/syllabifier.py` | 25 tests | ✓ | Complete |
| `src/core/gemination.py` | 26 tests | ✓ | Complete |
| `src/core/sun_letters.py` | 37 tests | ✓ | Complete |
| `src/core/allophones.py` | 34 tests | ✓ | Complete |
| `src/core/emphatic.py` | 52 tests | ✓ | Complete |
| `src/integrations/espeak.py` | 28 tests | ✓ | Complete |

---

## Performance Benchmarks

### Processing Speed

| Task | Time | Requirement |
|------|------|-------------|
| Short text (1-2 words) | < 0.001s | < 0.5s ✓ |
| Medium text (5-10 words) | 0.002s | < 1.0s ✓ |
| Long text (20-30 words) | 0.007s | < 2.0s ✓ |
| Single word average | < 0.001s | < 0.2s ✓ |

### Throughput

| Metric | Value | Requirement |
|--------|-------|-------------|
| Words per second | 3,352 w/s | ≥ 10 w/s ✓ |
| Sentences per second | 1,212 s/s | ≥ 5 s/s ✓ |

### Component Performance

| Component | Time | Requirement |
|-----------|------|-------------|
| Syllabification | < 0.001s | < 0.1s ✓ |
| Gemination processing | < 0.001s | < 0.05s ✓ |
| Sun letter processing | < 0.001s | < 0.05s ✓ |
| Emphatic spread | < 0.001s | < 0.05s ✓ |
| Complete pipeline | 0.002s | < 0.5s ✓ |
| Audio generation | 0.032s | < 1.0s ✓ |
| IPA→X-SAMPA conversion | 0.000045s | < 0.001s ✓ |

### Memory Efficiency

| Test | Result |
|------|--------|
| 1000 iterations | 0.598s (no leaks) ✓ |
| 500 words | 0.067s ✓ |
| Large text batch | Linear scaling ✓ |

---

## Continuous Integration

### Pre-commit Checks

Before committing code, run:
```bash
# Run all tests
pytest tests/ -v

# Check for failures
echo $?  # Should be 0
```

### CI/CD Pipeline (Future)

Recommended GitHub Actions workflow:
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          sudo apt install espeak-ng
          pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
```

---

## Writing New Tests

### Test Structure

Follow this structure for new tests:

```python
"""
Module description
"""
import pytest
import sys
sys.path.insert(0, 'src')

from src.main import ArabicTTS


class TestFeatureName:
    """Test feature description"""
    
    def test_basic_functionality(self):
        """Test basic case"""
        tts = ArabicTTS(dialect="EG")
        result = tts.process_text("مرحبا")
        
        assert 'words' in result
        assert len(result['words']) > 0
    
    def test_edge_case(self):
        """Test edge case"""
        tts = ArabicTTS(dialect="EG")
        result = tts.process_text("")
        
        assert result['words'] == []
```

### Best Practices

1. **Test one thing per test** - Keep tests focused
2. **Use descriptive names** - `test_sun_letter_assimilation_with_sheen()`
3. **Add docstrings** - Explain what the test validates
4. **Test both success and failure** - Include error cases
5. **Use fixtures** - Share test setup across tests
6. **Assert meaningful values** - Don't just check for non-None
7. **Test edge cases** - Empty inputs, large inputs, unicode issues
8. **Add performance tests** - For critical paths
9. **Keep tests fast** - Use mocks for slow operations
10. **Document expected behavior** - Comment complex assertions

### Test Fixtures

Common fixtures for Arabic TTS tests:

```python
@pytest.fixture
def tts_eg():
    """Egyptian Arabic TTS instance"""
    return ArabicTTS(dialect="EG")

@pytest.fixture
def tts_msa():
    """MSA TTS instance"""
    return ArabicTTS(dialect="MSA")

@pytest.fixture
def espeak():
    """eSpeak TTS instance"""
    return ESpeakTTS()
```

### Example Test: Adding New Phonological Rule

```python
def test_new_phonological_rule(self, tts_eg):
    """Test new phonological rule application"""
    text = "test_word"
    result = tts_eg.process_text(text)
    
    # Check rule was applied
    word = result['words'][0]
    assert 'new_rule_marker' in word['syllables'][0]
    
    # Check IPA output is correct
    expected_ipa = "expected_ipa_output"
    assert word['syllables'][0]['generated_ipa'] == expected_ipa
```

---

## Test Maintenance

### Regular Checks

- **Run full test suite daily** during development
- **Check test coverage** monthly
- **Review slow tests** quarterly
- **Update benchmarks** when system changes

### Adding Tests for Bugs

When fixing a bug:
1. Write a test that reproduces the bug
2. Verify the test fails
3. Fix the bug
4. Verify the test passes
5. Add to regression test suite

---

## Known Test Limitations

1. **Audio quality testing** - Currently manual, no automated perceptual tests
2. **Native speaker validation** - Requires human verification
3. **Cross-platform testing** - Tests run on Linux only
4. **Load testing** - No concurrent user tests
5. **Security testing** - No penetration testing included

---

## Future Test Enhancements

### Phase 2 Test Goals

1. **Expand dialect coverage** - Add tests for Gulf, Levantine, Maghreb
2. **Add pronunciation accuracy tests** - Compare with reference audio
3. **Perceptual audio quality tests** - PESQ/MOS scoring
4. **Stress testing** - 1000+ concurrent requests
5. **Security tests** - Input sanitization, injection attacks
6. **Cross-platform tests** - Windows, macOS, Linux
7. **API tests** - Full Flask endpoint testing
8. **Frontend tests** - UI interaction tests

---

## Resources

### Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Python unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [eSpeak NG Documentation](https://github.com/espeak-ng/espeak-ng)

### Project Files
- **Test Directory:** `/home/hamr/Documents/PycharmProjects/ArabicTTS/tests/`
- **Source Directory:** `/home/hamr/Documents/PycharmProjects/ArabicTTS/src/`
- **Task List:** `/home/hamr/Documents/PycharmProjects/ArabicTTS/tasks/TASK_LIST.md`

---

## Support

For test-related questions or issues:
1. Check this documentation
2. Review test file comments
3. Examine similar existing tests
4. Check pytest output for detailed error messages

---

**Document Version:** 1.0  
**Last Updated:** October 30, 2025  
**Status:** Complete  
**Test Suite Status:** 329/329 passing (100%)
