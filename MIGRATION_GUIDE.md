# Migration Guide: Arabic TTS Architecture Refactoring

This guide helps you migrate from the old architecture (where dialect was coupled to processors) to the new universal architecture with deferred IPA lookup.

## Overview of Changes

### Architecture Philosophy

**Old Architecture:**
- Each processor required a dialect parameter at initialization
- IPA lookup happened inside each processor
- Dialect was "baked in" at construction time
- Difficult to switch dialects without recreating instances

**New Architecture:**
- Universal processors (no dialect parameter)
- Position detection separated from IPA mapping
- Dialect selection happens ONLY in IPAMapper at the final step
- Easy dialect switching without recreating processors

## Migration Checklist

### 1. Processor Initialization

#### Before (Old):
```python
# Each processor needed dialect
gemination = GeminationProcessor("EG")
sun_letters = SunLetterProcessor("EG")
emphatic = EmphaticProcessor("EG")
allophones = AllophoneProcessor("EG", master_tts_path)
```

#### After (New):
```python
# All processors are universal (no dialect needed)
gemination = GeminationProcessor()
sun_letters = SunLetterProcessor()
emphatic = EmphaticProcessor()

# Use new components
position_detector = PositionDetector()
ipa_mapper = IPAMapper()  # Loads all dialects at once
```

### 2. Position Detection

#### Before (Old):
```python
# Position detection was part of AllophoneProcessor
processor = AllophoneProcessor("EG")
syllables = processor.process(syllables)
position = syllables[0].get("position")
```

#### After (New):
```python
# Dedicated PositionDetector
detector = PositionDetector()
syllables = detector.detect_positions(syllables)
position = syllables[0].get("detected_position")  # Note: key name changed
```

### 3. IPA Generation

#### Before (Old):
```python
# IPA generated inside processor
processor = AllophoneProcessor("EG")
result = processor.process(syllables)
ipa = result[0]["ipa"]
```

#### After (New):
```python
# Two-step process: detection then mapping
detector = PositionDetector()
mapper = IPAMapper()

# Step 1: Universal processing (no dialect)
syllables = detector.detect_positions(syllables)
# Apply other universal rules (gemination, sun letters, emphatic)
syllables = gemination.process(syllables)
syllables = sun_letters.process(syllables)
syllables = emphatic.process(syllables)

# Step 2: Dialect-specific IPA mapping
ipa = mapper.map_to_ipa(syllables, "EG")  # Dialect specified here
```

### 4. ArabicTTS Class Usage

#### Before (Old):
```python
tts = ArabicTTS("EG")  # Fixed dialect at initialization
result = tts.process_text("السلام عليكم")
# Cannot change dialect without new instance
```

#### After (New):
```python
tts = ArabicTTS("EG")  # Default dialect
result = tts.process_text("السلام عليكم")  # Uses EG

# Or override dialect per call
result = tts.process_text("السلام عليكم", dialect="MSA")  # Uses MSA

# Fast dialect switching
eg_result = tts.process_text("كتاب", dialect="EG")
msa_result = tts.process_text("كتاب", dialect="MSA")
```

## Key API Changes

### ArabicSyllabifier

**Old:**
```python
syllabifier = ArabicSyllabifier("EG")  # Required dialect
syllables = syllabifier.map_to_ipa(word)  # Included IPA
```

**New:**
```python
syllabifier = ArabicSyllabifier()  # No dialect needed
syllables = syllabifier.get_syllable_structure(word)  # No IPA
# Use IPAMapper for IPA generation
```

### AllophoneProcessor

**Status:** DEPRECATED

**Old:**
```python
processor = AllophoneProcessor("EG")
result = processor.process(syllables)
```

**New:**
```python
# Separate concerns
position_detector = PositionDetector()
ipa_mapper = IPAMapper()

# Position detection (universal)
syllables = position_detector.detect_positions(syllables)

# IPA mapping (dialect-specific)
ipa = ipa_mapper.map_to_ipa(syllables, "EG")
```

## Benefits of New Architecture

1. **Clean Separation:** Universal processing rules are separated from dialect-specific IPA mapping
2. **Flexibility:** Easy to switch dialects at runtime
3. **Testability:** Processors can be tested independently of dialect data
4. **Maintainability:** Clearer code with single responsibilities
5. **Performance:** One-time loading of all dialect data

## Backward Compatibility

- AllophoneProcessor is deprecated but still functional (shows deprecation warning)
- ArabicTTS maintains backward compatibility with existing API
- Most existing code will work with minimal changes

## Breaking Changes

1. **ArabicSyllabifier constructor** no longer accepts dialect parameter
2. **AllophoneProcessor** is deprecated (will be removed in future version)
3. Some test files need updating to use new architecture
4. Error handling tests expect old API signatures

## Testing Migration

### Universal Processor Tests
```bash
# Run tests for new universal architecture
pytest tests/unit/test_universal_processors.py -v

# Run tests for new components
pytest tests/unit/test_ipa_mapper.py tests/unit/test_position_detector.py -v
```

### Integration Tests
```bash
# Run integration tests
pytest tests/integration/test_ipa_mapper_position_detector_integration.py -v
```

## Example: Complete Migration

### Before (Old):
```python
from src.core.gemination import GeminationProcessor
from src.core.allophones import AllophoneProcessor

def process_word(word, dialect):
    gemination = GeminationProcessor(dialect)
    allophone = AllophoneProcessor(dialect)

    syllables = allophone.get_syllables(word)
    syllables = gemination.process(syllables)
    result = allophone.process(syllables)

    return result[0]["ipa"]
```

### After (New):
```python
from src.core.gemination import GeminationProcessor
from src.core.sun_letters import SunLetterProcessor
from src.core.emphatic import EmphaticProcessor
from src.core.position_detector import PositionDetector
from src.core.ipa_mapper import IPAMapper

def process_word(word, dialect):
    # Initialize universal processors once
    gemination = GeminationProcessor()
    sun_letters = SunLetterProcessor()
    emphatic = EmphaticProcessor()
    position_detector = PositionDetector()
    ipa_mapper = IPAMapper()

    # Syllabify (universal)
    syllable_data = [{
        'syllable': word,
        'word_index': 0,
        'position_in_word': 0
    }]

    # Apply universal phonological rules
    syllables = position_detector.detect_positions(syllable_data)
    syllables = gemination.process(syllables)
    syllables = sun_letters.process(syllables)
    syllables = emphatic.process(syllables)

    # Generate IPA (dialect-specific)
    ipa = ipa_mapper.map_to_ipa(syllables, dialect)

    return ipa
```

## Troubleshooting

### Common Issues

1. **"dialect parameter unexpected" error**
   - Remove dialect parameter from processor constructors
   - Pass dialect to IPAMapper methods instead

2. **Missing "detected_position" key**
   - Use PositionDetector.detect_positions() to add position markers
   - Key changed from "position" to "detected_position"

3. **IPA not generated**
   - Use IPAMapper.map_to_ipa() after phonological processing
   - AllophoneProcessor no longer generates IPA

4. **Performance concerns**
   - Initialize IPAMapper once and reuse
   - Universal processors are lightweight, no performance impact

### Getting Help

- Check unit tests for examples of new usage
- Look at integration tests for complete pipeline examples
- Refer to inline code comments for architectural decisions

## Future Roadmap

- Next version will remove AllophoneProcessor entirely
- More dialects can be added without code changes
- Planned features: real-time dialect switching, streaming support