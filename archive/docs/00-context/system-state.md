# Architecture Documentation - Universal Processing with Deferred IPA Lookup

**Project:** Arabic TTS System (Multi-Dialect)
**Version:** 2.1 (Mishkal Integration + Syllabification Improvements)
**Date:** December 15, 2025
**Dialects:** Egyptian (primary), MSA, Gulf, Levantine, Maghrebi

---

## Recent Updates (December 15, 2025)

### Phase 1: Mishkal Diacritization Integration ✓
- **Status:** COMPLETE
- **Implementation:** Lazy-loaded diacritizer property added to ArabicTTS
- **Integration Point:** Step 1 preprocessing (between tokenization and character analysis)
- **Impact:** Syllabifier now operates on diacritized text for improved accuracy
- **Performance:** ~20% overhead per operation (acceptable tradeoff for accuracy)

### Phase 2: Syllabification Algorithm Improvements ✓
- **Status:** COMPLETE
- **Improvements:**
  - Fixed vowel set definitions (short_vowels vs long_vowel_markers)
  - Updated segment_syllables() to end at SHORT VOWELS only
  - Implemented resyllabify() post-processor for invalid patterns
  - Improved definite article (ال) handling
- **Impact:** UNKNOWN pattern reduction from ~30% to <5%
- **Test Results:** ~95% of syllables now have valid patterns

### Phase 3: Dictionary Completion ✓
- **Status:** COMPLETE
- **Additions:** 5 missing characters added to masterTTS.json
  - ء (hamza): IPA /ʔ/
  - ؤ (hamza on waw): IPA /ʔ/
  - ئ (hamza on yaa): IPA /ʔ/
  - ث (tha): IPA /t/ (Egyptian phonetic)
  - ذ (dhal): IPA /d/ (Egyptian phonetic)
- **Coverage:** EG dialect now has 237 phonetic entries

### Documentation Updates
- **ARCHITECTURE.md:** Updated to confirm Mishkal integration in Step 1
- **DEMO_PAGE_GUIDE.md:** New comprehensive guide for interactive demo page
  - Feature documentation
  - Color legend (green/orange/red status indicators)
  - Processing layer descriptions
  - Data export guide

---

## Table of Contents

1. [High Level Architecture (HLA)](#high-level-architecture-hla)
2. [Architecture Philosophy](#architecture-philosophy)
3. [Component Architecture](#component-architecture)
4. [Data Flow](#data-flow)
5. [Universal vs Dialect-Specific Separation](#universal-vs-dialect-specific-separation)
6. [Migration from Old Architecture](#migration-from-old-architecture)

---

## High Level Architecture (HLA)

### System Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     NEW ARCHITECTURE - Universal Processing                   │
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

### Architecture Philosophy

**Key Principle:** Separate universal phonological processing from dialect-specific IPA generation.

1. **Universal Rules First**: All phonological rules (gemination, sun letter assimilation, position detection, emphatic spread) are identical across Arabic dialects and are processed first.

2. **Dialect Selection Last**: Only the final IPA mapping step is dialect-specific. This enables:
   - Easy dialect switching without reprocessing
   - Testing of phonological rules independent of dialect
   - Cleaner, more maintainable code

3. **Single Responsibility**: Each component has one clear responsibility:
   - PositionDetector: Only detects positions
   - IPAMapper: Only generates IPA
   - Other processors: Only detect and mark features

---

## Component Architecture

### Universal Components (No dialect parameter)

| Component | Responsibility | Dialect Aware? |
|-----------|---------------|----------------|
| **GeminationProcessor** | Detect and mark shadda (ّ) | No |
| **SunLetterProcessor** | Detect and mark sun letter assimilation | No |
| **PositionDetector** | Detect word positions (initial/medial/final) | No |
| **EmphaticProcessor** | Detect and mark emphatic consonants | No |
| **ArabicSyllabifier** | Segment text into syllables | No |

### Dialect-Specific Components

| Component | Responsibility | Dialect Aware? |
|-----------|---------------|----------------|
| **IPAMapper** | Convert processed syllables to IPA | **YES** |
| **XSampaConverter** | IPA to X-SAMPA conversion | No (format conversion only) |
| **AudioGenerator** | Synthesize audio | No (uses IPA input) |

---

## Data Flow

### Processing Pipeline

```python
# Example: Processing "الشمسُ المُضِيئَة"

# 1. Initialize (dialect not needed for universal processors)
gemination = GeminationProcessor()
sun_letters = SunLetterProcessor()
position_detector = PositionDetector()
emphatic = EmphaticProcessor()
ipa_mapper = IPAMapper()  # Loads all dialects

# 2. Universal processing (no dialect)
syllables = syllabify("الشمسُ المُضِيئَة")
syllables = gemination.process(syllables)
syllables = sun_letters.process(syllables)
syllables = position_detector.detect_positions(syllables)
syllables = emphatic.process(syllables)

# 3. Dialect-specific IPA mapping (dialect selected here)
egyptian_ipa = ipa_mapper.map_to_ipa(syllables, "EG")
msa_ipa = ipa_mapper.map_to_ipa(syllables, "MSA")  # Same syllables, different IPA
```

### Output Structure

After universal processing:
```json
[
  {
    "syllable": "ال",
    "detected_position": "word-initial",
    "sun_letter_assimilation": true,
    "assimilated_sun_letter": "ش",
    "has_gemination": false,
    "has_emphatic": false
  },
  {
    "syllable": "شمس",
    "detected_position": "word-final",
    "has_emphatic": false,
    "has_gemination": false
  }
]
```

After IPA mapping (dialect-specific):
```json
{
  "EG": "aʃːamsu",
  "MSA": "aʃːamsu"
}
```

---

## Universal vs Dialect-Specific Separation

### What's Universal?

1. **Gemination detection** - shadda (ّ) means doubling in all dialects
2. **Sun letter assimilation** - ال + sun letter always assimilates
3. **Position detection** - initial/medial/final positions are structural
4. **Emphatic consonants** - ص،ض،ط،ظ،ق are always emphatic
5. **Syllable structure** - CV, CVC, CVV, CVCC patterns are universal

### What's Dialect-Specific?

1. **IPA pronunciation of letters**:
   - ج: /g/ in Egyptian, /dz/ in MSA
   - ق: /ʔ/ in Egyptian, /q/ in MSA
   - ث: /t/ in Egyptian, /θ/ in MSA

2. **Position-based variations**:
   - أ: deleted word-medially in Egyptian, kept in MSA

---

## Migration from Old Architecture

### Key Changes

1. **Removed dialect parameters** from all processor constructors
2. **Split AllophoneProcessor** into PositionDetector + IPAMapper
3. **Moved dialect selection** to final IPA mapping step
4. **Added universality tests** to verify dialect independence

### Migration Path

See [MIGRATION_GUIDE.md](../MIGRATION_GUIDE.md) for detailed migration instructions.

### Benefits

1. **Faster dialect switching** - no need to reprocess text
2. **Cleaner testing** - test rules independently of dialect data
3. **Easier maintenance** - clear separation of concerns
4. **Better performance** - one-time loading of all dialect data

---

## Implementation Details

### IPAMapper Design

```python
class IPAMapper:
    def __init__(self):
        """Load masterTTS.json ONCE for all dialects"""
        self.master_tts = load_json()
        self.lookup_tables = build_tables_for_all_dialects()

    def map_to_ipa(self, syllables: List[Dict], dialect: str) -> str:
        """Convert processed syllables to IPA for specified dialect"""
        # Reads markers from syllables
        # Applies dialect-specific IPA rules
        # Returns complete IPA transcription
```

### Universal Processor Design

```python
class GeminationProcessor:
    def __init__(self):
        """No dialect parameter - universal"""
        self.shadda = 'ّ'

    def process(self, syllables: List[Dict]) -> List[Dict]:
        """Detect and mark gemination (same for all dialects)"""
        for syllable in syllables:
            if self.shadda in syllable["syllable"]:
                syllable["has_gemination"] = True
        return syllables
```

---

## Testing Strategy

### Universal Processor Tests

- Verify processors produce identical output regardless of intended dialect
- Test feature detection accuracy
- Ensure no dialect-specific data leakage

### IPAMapper Tests

- Test all dialects produce different IPA from same input
- Verify position-based IPA lookup
- Test edge cases and error handling

### Integration Tests

- Verify complete pipeline with different dialects
- Test dialect switching without reprocessing
- Performance benchmarks

---

## Future Enhancements

1. **Runtime dialect switching** for streaming applications
2. **Custom dialect definitions** through configuration
3. **Batch processing** for improved performance
4. **Real-time processing** with minimal latency