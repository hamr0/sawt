# Technology Stack Documentation - Universal Architecture

**Project:** Arabic TTS System (Multi-Dialect)
**Version:** 2.0 (Architecture Refactored)
**Date:** December 14, 2025
**Dialects:** Egyptian (primary), MSA, Gulf, Levantine, Maghrebi

---

## Table of Contents

1. [Overview](#overview)
2. [Universal Processing Components](#universal-processing-components)
3. [Dialect-Specific Components](#dialect-specific-components)
4. [External Libraries](#external-libraries)
5. [System Dependencies](#system-dependencies)
6. [Technology Decisions](#technology-decisions)
7. [Component Responsibilities Matrix](#component-responsibilities-matrix)

---

## Overview

The Arabic TTS system uses a **universal processing architecture** where phonological rules are separated from dialect-specific IPA generation. This enables clean separation of concerns and flexible dialect switching.

### Architecture Principle

```
Universal Processing (dialect-agnostic)
    ↓
Feature Detection and Marking
    ↓
Dialect-Specific IPA Lookup (selected at runtime)
```

### Technology Split

| Category | Internal | External | Total |
|----------|----------|----------|-------|
| **Core Logic** | 95% | 5% | 100% |
| **Infrastructure** | 10% | 90% | 100% |
| **Testing** | 80% | 20% | 100% |
| **Total LOC** | ~6,000 | ~500 | ~6,500 |

---

## Universal Processing Components

### What We Built from Scratch

#### 1. Position Detector ✅
**File:** `src/core/position_detector.py` (286 lines)

**What it does:**
- Detects word positions (initial, medial, final) for syllables
- Marks positions without generating IPA
- Groups syllables by word boundaries
- Universal across all Arabic dialects

**Why we built it:**
- Position detection is a linguistic universal in Arabic
- Needed separation from IPA generation for clean architecture
- Enables position-based IPA lookup in any dialect

**Key features:**
```python
- Word-initial/medial/final detection
- Multi-word sentence handling
- Single-syllable word support
- O(n) linear time complexity
```

**Test Coverage:** 30 tests, 100% passing

---

#### 2. IPA Mapper ✅
**File:** `src/core/ipa_mapper.py` (380 lines)

**What it does:**
- Converts processed syllables to IPA using dialect-specific data
- Handles position-based IPA lookup
- Applies gemination, assimilation, and emphatic markers
- Only dialect-aware component in the system

**Why we built it:**
- Centralizes all dialect-specific IPA logic
- Enables fast dialect switching without reprocessing
- Provides clean API for IPA generation

**Key features:**
```python
- 5 dialects supported (EG, MSA, Gulf, Levantine, Maghrebi)
- Position-based IPA lookup
- O(1) character lookup with pre-built tables
- Fast dialect switching (< 1ms)
```

**Test Coverage:** 32 tests, 100% passing

---

#### 3. Universal Phonological Processors ✅

##### Gemination Processor
**File:** `src/core/gemination.py` (151 lines)
- Detects shadda (ّ) markers universally
- No dialect parameter needed
- Marks gemination for IPA mapper

##### Sun Letter Processor
**File:** `src/core/sun_letters.py` (250 lines)
- Identifies sun letters for assimilation
- Universal rule: ال + sun letter always assimilates
- Marks assimilation for IPA mapper

##### Emphatic Processor
**File:** `src/core/emphatic.py` (280 lines)
- Detects emphatic consonants (ص،ض،ط،ظ،ق)
- Marks pharyngealization spread
- Universal across all dialects

---

#### 4. Universal Syllabifier ✅
**File:** `src/main.py` (class ArabicSyllabifier) (150 lines)

**What it does:**
- Segments Arabic words into syllables
- Universal syllable patterns (CV, CVC, CVV, CVCC)
- No IPA generation (handled by IPAMapper)

**Key changes from v1.0:**
- Removed dialect parameter
- Removed IPA generation methods
- Focus on pure syllabification

---

## Dialect-Specific Components

### Only IPA Mapper is Dialect-Aware

| Component | Dialect Parameter | Reason |
|-----------|-------------------|---------|
| **IPAMapper** | Yes (in methods) | Generates dialect-specific IPA |
| All others | No | Universal linguistic rules |

### masterTTS.json Structure

```json
{
  "EG": [
    {
      "Arabic letter": "ج",
      "IPA": "g",
      "Position": "word-initial",
      "X-SAMPA": "g"
    }
  ],
  "MSA": [
    {
      "Arabic letter": "ج",
      "IPA": "dz",
      "Position": "word-initial",
      "X-SAMPA": "d_z"
    }
  ]
}
```

---

## External Libraries

### Core Dependencies

| Library | Version | Purpose | Usage |
|---------|---------|---------|-------|
| **pytest** | 8.4.2 | Testing framework | Unit/integration tests |
| **mishkal** | Latest | Diacritization | Optional: add vowels to text |

### Optional Dependencies

| Library | Version | Purpose | Integration |
|---------|---------|---------|-------------|
| **flask** | Latest | Web API | REST endpoints |
| **boto3** | Latest | AWS Polly | Cloud TTS alternative |
| **pyttsx3** | Latest | Local TTS | eSpeak integration |

---

## System Dependencies

### Required
- Python 3.8+
- UTF-8 support (for Arabic text)

### Optional
- eSpeak NG (for local audio synthesis)
- AWS credentials (for Polly)

---

## Technology Decisions

### Why Universal Architecture?

1. **Clean Separation of Concerns**
   - Linguistic rules are universal
   - Only pronunciation varies by dialect

2. **Performance Benefits**
   - Process text once, generate multiple dialect outputs
   - Fast dialect switching without reprocessing

3. **Testability**
   - Test rules independently of dialect data
   - Verify universality with dedicated tests

4. **Maintainability**
   - Add new dialects by extending masterTTS.json
   - No code changes needed for new dialects

### Implementation Choices

1. **Position Detection Separate from IPA**
   - Position is a linguistic feature
   - IPA varies by dialect and position

2. **Feature Marking System**
   - Processors mark features without generating output
   - IPAMapper reads markers to generate correct IPA

3. **Lazy Dialect Loading**
   - IPAMapper loads all dialects at initialization
   - Enables O(1) dialect switching

---

## Component Responsibilities Matrix

### Processing Pipeline

| Step | Component | Input | Output | Dialect? |
|------|-----------|-------|--------|---------|
| 1 | Diacritizer | Arabic text | Diacritized text | No |
| 2 | Tokenizer | Text | Tokens | No |
| 3 | Syllabifier | Tokens | Syllables | No |
| 4 | GeminationProcessor | Syllables | +Gemination markers | No |
| 5 | SunLetterProcessor | Syllables | +Assimilation markers | No |
| 6 | PositionDetector | Syllables | +Position markers | No |
| 7 | EmphaticProcessor | Syllables | +Emphatic markers | No |
| 8 | IPAMapper | Marked syllables | IPA transcription | **YES** |

### Data Structures

### Universal Syllable (after processing, before IPA)
```python
{
    "syllable": "شمس",
    "detected_position": "word-final",
    "has_gemination": false,
    "sun_letter_assimilation": false,
    "has_emphatic": false,
    "pattern": "CVCC"
}
```

### Dialect-Specific Output
```python
# Egyptian Arabic
"ʃams"

# MSA
"ʃams"

# Same input, different handling for other letters:
# EG: جمل → "gamal"
# MSA: جمل → "dʒamal"
```

---

## Performance Characteristics

### Universal Processors
- **Initialization**: < 1ms (no data loading)
- **Processing speed**: > 10,000 syllables/second
- **Memory usage**: Minimal (stateless)

### IPAMapper
- **Initialization**: ~100ms (load all dialects)
- **Lookup speed**: O(1) per character
- **Dialect switching**: < 1ms
- **Memory usage**: ~5MB for all dialects

### Overall Pipeline
- **Text to IPA**: ~3,000 words/second
- **No regression** from v1.0 performance

---

## Future Enhancements

### Planned Features
1. **Streaming Processing**
   - Process text in chunks
   - Maintain state across chunks

2. **Custom Dialects**
   - JSON-based dialect definitions
   - Runtime dialect loading

3. **Advanced Features**
   - Prosody modeling
   - Emotion-based pronunciation

### Extensibility
1. **New Phonological Rules**
   - Add processor to pipeline
   - Universal by design

2. **New Dialects**
   - Add entries to masterTTS.json
   - No code changes needed

3. **New Output Formats**
   - Extend IPAMapper
   - Processors remain unchanged