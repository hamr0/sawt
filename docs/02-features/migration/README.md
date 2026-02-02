# Migration Guide: Dialect Architecture Refactor

**Version:** 2.0
**Date:** December 14, 2025
**Description:** Migration guide for the universal processing architecture refactor

---

## Overview

The Arabic TTS system has been refactored to separate universal phonological processing from dialect-specific IPA lookup. This guide helps you migrate from the old architecture to the new one.

## Key Changes

### 1. Removed Dialect Parameters from Universal Processors

**Old API (deprecated):**
```python
# These constructors no longer accept dialect parameter
processor = GeminationProcessor(dialect="EG")  # ❌ No longer accepts dialect
processor = SunLetterProcessor(dialect="EG")   # ❌ No longer accepts dialect
processor = EmphaticProcessor(dialect="EG")    # ❌ No longer accepts dialect
processor = AllophoneProcessor(dialect="EG")  # ❌ Deprecated - use PositionDetector + IPAMapper
```

**New API:**
```python
# Universal processors - no dialect needed
processor = GeminationProcessor()      # ✅ Universal
processor = SunLetterProcessor()      # ✅ Universal
processor = EmphaticProcessor()       # ✅ Universal

# For position detection and IPA mapping
from src.core.position_detector import PositionDetector
from src.core.ipa_mapper import IPAMapper

position_detector = PositionDetector()  # ✅ Universal
ipa_mapper = IPAMapper()                # ✅ Loads all dialects, selects at call time
```

### 2. AllophoneProcessor is Deprecated

**Old:**
```python
from src.core.allophones import AllophoneProcessor

processor = AllophoneProcessor(dialect="EG")
result = processor.process(syllables)
```

**New:**
```python
from src.core.position_detector import PositionDetector
from src.core.ipa_mapper import IPAMapper

# Step 1: Detect positions (universal)
position_detector = PositionDetector()
syllables = position_detector.detect_positions(syllables)

# Step 2: Map to IPA (dialect-specific)
ipa_mapper = IPAMapper()
ipa = ipa_mapper.map_to_ipa(syllables, dialect="EG")
```

### 3. ArabicSyllabifier No Longer Accepts Dialect

**Old:**
```python
syllabifier = ArabicSyllabifier(dialect="EG")  # ❌ No longer accepts dialect
```

**New:**
```python
syllabifier = ArabicSyllabifier()  # ✅ Universal patterns
```

### 4. IPAMapper Handles All Dialect-Specific Lookups

The new IPAMapper component is the ONLY component that handles dialect-specific IPA generation:

```python
from src.core.ipa_mapper import IPAMapper

# Initialize once (loads all dialects)
ipa_mapper = IPAMapper()

# Use for any dialect
eg_ipa = ipa_mapper.map_to_ipa(syllables, "EG")
msa_ipa = ipa_mapper.map_to_ipa(syllables, "MSA")
gulf_ipa = ipa_mapper.map_to_ipa(syllables, "Gulf")

# Fast dialect switching without reinitialization
```

### 5. ArabicTTS Usage Remains Mostly Compatible

The main ArabicTTS class maintains backward compatibility:

```python
# Still works as before
tts = ArabicTTS(dialect="EG")
result = tts.process_text("السلام عليكم")

# Can also override dialect per call
result = tts.process_text("السلام عليكم", dialect="MSA")
```

## Migration Steps

### For Library Users

1. **Update processor initialization:**
   - Remove dialect parameters from GeminationProcessor, SunLetterProcessor, EmphaticProcessor
   - Replace AllophoneProcessor with PositionDetector + IPAMapper

2. **Update syllabifier initialization:**
   - Remove dialect parameter from ArabicSyllabifier

3. **Use IPAMapper for dialect-specific IPA:**
   - Initialize IPAMapper once
   - Pass dialect to map_to_ipa() method calls

### For Developers Extending the System

1. **New phonological rules should be universal:**
   - Do not add dialect parameters to new processors
   - Focus on detecting and marking features
   - Let IPAMapper handle dialect-specific output

2. **For dialect-specific behavior:**
   - Add data to masterTTS.json
   - Extend IPAMapper to use new data
   - Keep phonological processors universal

## Code Examples

### Processing Word with New Architecture

```python
from src.main import ArabicTTS

# Simple usage (backward compatible)
tts = ArabicTTS(dialect="EG")
result = tts.process_text("صباح الخير")
print(result["ipa"])  # Full IPA transcription

# Access individual components
from src.core.position_detector import PositionDetector
from src.core.ipa_mapper import IPAMapper
from src.main import ArabicSyllabifier

# Universal processing (dialect-independent)
syllabifier = ArabicSyllabifier()
gemination = GeminationProcessor()
sun_letters = SunLetterProcessor()
emphatic = EmphaticProcessor()
position_detector = PositionDetector()

# Process word
word = "صباح"
syllables = syllabifier.get_syllable_structure(word)
syllables = gemination.process(syllables)
syllables = sun_letters.process(syllables)
syllables = position_detector.detect_positions(syllables)
syllables = emphatic.process(syllables)

# Generate IPA for different dialects
ipa_mapper = IPAMapper()
eg_ipa = ipa_mapper.map_to_ipa(syllables, "EG")
msa_ipa = ipa_mapper.map_to_ipa(syllables, "MSA")

print(f"Egyptian: {eg_ipa}")
print(f"MSA: {msa_ipa}")
```

### Testing Universal Processors

```python
# Processors produce same output regardless of target dialect
gemination = GeminationProcessor()
sun_letters = SunLetterProcessor()
emphatic = EmphaticProcessor()

# These produce identical results for all dialects
processed = gemination.process(syllables)  # Same for EG, MSA, etc.
processed = sun_letters.process(processed)  # Same for EG, MSA, etc.
processed = emphatic.process(processed)    # Same for EG, MSA, etc.

# Only IPA mapping differs by dialect
ipa_mapper = IPAMapper()
eg_ipa = ipa_mapper.map_to_ipa(processed, "EG")
msa_ipa = ipa_mapper.map_to_ipa(processed, "MSA")
```

## Benefits of New Architecture

1. **Cleaner Separation of Concerns**
   - Universal rules are truly universal
   - Dialect differences are isolated to IPA data

2. **Better Performance**
   - Initialize processors once
   - Fast dialect switching without reprocessing

3. **Easier Testing**
   - Test phonological rules independently of dialects
   - Clearer test responsibilities

4. **Simpler Extension**
   - Add new dialects by adding data only
   - New phonological rules apply to all dialects

## Breaking Changes Summary

| Component | Old API | New API | Impact |
|-----------|---------|---------|--------|
| GeminationProcessor | `__init__(dialect)` | `__init__()` | Low |
| SunLetterProcessor | `__init__(dialect)` | `__init__()` | Low |
| EmphaticProcessor | `__init__(dialect)` | `__init__()` | Low |
| AllophoneProcessor | Full processor | Deprecated | Medium |
| ArabicSyllabifier | `__init__(dialect)` | `__init__()` | Low |
| IPAMapper | N/A | New component | N/A |

## Deprecation Timeline

- **Current Release (v2.0):** AllophoneProcessor deprecated but functional
- **Next Major Release (v3.0):** AllophoneProcessor will be removed
- **Migration Period:** 6 months for complete migration

## Support

For questions about migration:
1. Check the new architecture documentation
2. Review test examples in `tests/unit/test_universal_processors.py`
3. Check integration examples in `tests/integration/test_ipa_mapper_position_detector_integration.py`

---

**Note:** This migration enables future features like runtime dialect switching, better performance, and easier addition of new dialects.