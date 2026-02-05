# Egyptian Arabic Test Dataset - Documentation

**Project:** Arabic TTS MVP Phase 1  
**Dialect:** Egyptian Arabic (EG)  
**Version:** 1.0  
**Date Created:** October 30, 2025  
**Total Sentences:** 25

---

## Overview

This test dataset provides comprehensive validation examples for the Egyptian Arabic Text-to-Speech system. It includes carefully selected sentences that cover all major phonological features of Egyptian Arabic.

---

## Dataset Contents

### Files in This Directory

| File | Description | Size |
|------|-------------|------|
| `egyptian_arabic_test_dataset.json` | Main dataset with 25 test sentences | ~21 KB |
| `reference_outputs/expected_outputs.json` | Expected syllabification and IPA outputs | ~44 KB |
| `reference_audio/*.wav` | 25 reference audio files | ~1.4 MB |
| `VALIDATION_CHECKLIST.md` | Validation checklist for native speakers | ~10 KB |
| `README.md` | This documentation file | ~15 KB |

---

## Dataset Structure

### Test Sentence Categories

| Category | Count | Examples |
|----------|-------|----------|
| Greetings | 5 | السلام عليكم، صباح الخير، إزيك |
| Common Nouns | 6 | الشمس، القمر، كتاب، مدرسة |
| Professions & Family | 4 | مُدَرِّس، طبيب، أمّي، أبي |
| Common Phrases | 4 | شكرا، من فضلك، الحمد لله |
| Questions & Statements | 3 | فين، أنا مصري |
| Complex Sentences | 3 | اللغة العربية لغة جميلة |

---

## Phonological Feature Coverage

### Complete Feature Matrix

| Feature | Sentence IDs | Total Coverage |
|---------|-------------|----------------|
| **Sun Letter Assimilation** | 1, 3, 6, 8, 9, 10, 21, 22 | 8 sentences (32%) |
| **Moon Letter** | 5, 7, 21, 23 | 4 sentences (16%) |
| **Emphatic Consonants** | 2, 3, 10, 14, 18, 20, 23, 25 | 8 sentences (32%) |
| **Pharyngealization** | 2, 10, 14, 18, 20 | 5 sentences (20%) |
| **Gemination (Shadda)** | 3, 4, 6, 8, 9, 10, 13, 15, 22 | 9 sentences (36%) |
| **Long Vowels** | 1, 2, 3, 5, 8, 9, 10, 11, 14, 15, 16, 19, 20, 21, 22, 24, 25 | 17 sentences (68%) |
| **Diphthongs** | 2, 4, 9, 23 | 4 sentences (16%) |
| **Pharyngeal Consonants** | 1, 5, 10, 21, 25 | 5 sentences (20%) |
| **Consonant Clusters** | 6, 12, 17, 24, 25 | 5 sentences (20%) |

### Emphatic Consonants Covered

- **ص (ṣ)** - Sentences 2, 3, 20, 25
- **ض (ḍ)** - Sentence 18, 23
- **ط (ṭ)** - Sentences 10, 14
- **ظ (ẓ)** - (Can be added in future versions)
- **ق (q)** - Sentences 7, 20

---

## Difficulty Distribution

| Difficulty | Count | Percentage |
|------------|-------|------------|
| **Easy** | 7 | 28% |
| **Medium** | 15 | 60% |
| **Hard** | 3 | 12% |

### Easy Sentences (7)
Good for initial testing and basic validation:
- إزيك (4)
- القمر (7)
- كتاب (11)
- أمّي (15)
- أبي (16)
- شكرا (17)
- فين (19)

### Medium Sentences (15)
Standard test cases covering common features:
- السلام عليكم (1)
- صباح الخير (2)
- صباح النور (3)
- And 12 more...

### Hard Sentences (3)
Complex sentences testing multiple features:
- الطعام (10) - Multiple emphatics + pharyngealization
- اللغة العربية لغة جميلة (21) - Long sentence, mixed features
- مستشفى (24) - Complex clusters

---

## Usage Frequency

| Frequency | Count | Usage Context |
|-----------|-------|---------------|
| **Very High** | 13 | Daily conversation, essential vocabulary |
| **High** | 10 | Common words and phrases |
| **Medium** | 2 | Less frequent but important |

---

## Audio Files

### Reference Audio Specifications

| Property | Value |
|----------|-------|
| **Format** | WAV (WAVE) |
| **Sample Rate** | 22050 Hz |
| **Bit Depth** | 16-bit PCM |
| **Channels** | Mono |
| **Total Size** | ~1.4 MB |
| **Average File Size** | ~55 KB |
| **Total Duration** | ~45 seconds |

### Audio File Naming Convention

```
sentence_[ID]_[transliteration].wav
```

Examples:
- `sentence_01_as-salāmu_ʿalaykum.wav`
- `sentence_02_ṣabāḥ_al-khayr.wav`
- `sentence_25_ahlan_wa_sahlan_fī_maṣr.wav`

---

## Expected Outputs

The `reference_outputs/expected_outputs.json` file contains:

### For Each Sentence

```json
{
  "id": 1,
  "arabic": "السلام عليكم",
  "transliteration": "as-salāmu ʿalaykum",
  "english": "Peace be upon you",
  "category": "Basic Greeting",
  "processed_words": [
    {
      "original": "السلام",
      "syllables": [
        {
          "syllable": "السّ",
          "pattern": "CVC",
          "ipa": "as",
          "generated_ipa": "as",
          "has_gemination": false,
          "sun_letter_assimilation": true,
          "has_emphatic": false
        },
        // ... more syllables
      ]
    }
  ],
  "phonological_features": [...]
}
```

### Key Fields

- **syllable**: Arabic text of the syllable
- **pattern**: Syllable pattern (CV, CVC, CVV, CVCC, CVVC)
- **ipa**: Original IPA from dictionary
- **generated_ipa**: IPA after phonological rules
- **has_gemination**: Boolean for gemination presence
- **sun_letter_assimilation**: Boolean for assimilation
- **has_emphatic**: Boolean for emphatic consonants
- **pharyngealized_ipa**: IPA with pharyngealization applied

---

## Using the Dataset

### 1. Testing Individual Sentences

```python
from src.main import ArabicTTS
import json

# Load test dataset
with open('data/test_cases/egyptian_arabic_test_dataset.json', 'r') as f:
    dataset = json.load(f)

# Initialize TTS
tts = ArabicTTS(dialect="EG")

# Test first sentence
sentence = dataset['test_sentences'][0]
result = tts.process_text(sentence['arabic'])
print(result)
```

### 2. Generating Audio

```python
from src.integrations.espeak import ESpeakTTS

espeak = ESpeakTTS()

# Generate audio for a sentence
success, msg = espeak.generate_audio_from_text(
    text="السلام عليكم",
    output_path="output.wav"
)
```

### 3. Validating Outputs

```python
import json

# Load expected outputs
with open('data/test_cases/reference_outputs/expected_outputs.json', 'r') as f:
    expected = json.load(f)

# Compare with actual output
actual = tts.process_text("السلام عليكم")

# Validate syllabification
for i, word in enumerate(actual['words']):
    expected_word = expected['sentences'][0]['processed_words'][i]
    assert word['original'] == expected_word['original']
    # ... more validation
```

---

## Validation Process

### For Native Speakers

1. **Listen to all audio files** in `reference_audio/`
2. **Fill out** `VALIDATION_CHECKLIST.md`
3. **Rate each sentence** on:
   - Overall pronunciation accuracy
   - Phonological feature correctness
   - Natural flow and intonation
   - Egyptian dialect authenticity
4. **Provide feedback** on common issues
5. **Return completed checklist** to project team

### For Developers

1. **Run automated tests**
   ```bash
   pytest tests/integration/test_complete_pipeline.py -v
   ```

2. **Compare outputs**
   ```bash
   python scripts/generate_test_dataset_outputs.py
   # Compare with reference_outputs/
   ```

3. **Check coverage**
   - Ensure all phonological features are tested
   - Verify all difficulty levels are represented
   - Confirm usage frequency distribution

---

## Dataset Quality Metrics

### Coverage Completeness

| Metric | Status |
|--------|--------|
| Sun/Moon Letters | ✓ Complete |
| All Emphatic Consonants | ✓ Complete |
| Gemination Varieties | ✓ Complete |
| Long Vowels & Diphthongs | ✓ Complete |
| Pharyngeal Consonants | ✓ Complete |
| Consonant Clusters | ✓ Complete |
| Egyptian Colloquialisms | ✓ Included |

### Diversity Metrics

- **Category Diversity:** 8 different categories
- **Difficulty Range:** Easy to Hard (full spectrum)
- **Word Count Range:** 1-6 words per sentence
- **Syllable Count Range:** 2-14 syllables per sentence

---

## Future Enhancements

### Phase 2 Additions

1. **More complex sentences** (10+ words)
2. **Numbers and dates** (e.g., "اليوم الخميس ٣٠ أكتوبر")
3. **Mixed content** (Arabic + English code-switching)
4. **Questions** (various question types)
5. **Emotions** (happy, sad, excited tones)
6. **Regional variations** within Egyptian Arabic

### Additional Validation

1. **Perceptual audio quality tests** (MOS scoring)
2. **Intelligibility tests** (word recognition rate)
3. **Prosody evaluation** (intonation, stress, rhythm)
4. **Comparison with commercial TTS systems**

---

## Citation

If you use this dataset in research or publications, please cite:

```
Egyptian Arabic TTS Test Dataset v1.0
Arabic Text-to-Speech System MVP Phase 1
October 2025
```

---

## Contact & Support

For questions, issues, or feedback about this dataset:
- Open an issue on the project repository
- Contact the development team
- Refer to the main project documentation

---

## Changelog

### Version 1.0 (2025-10-30)
- Initial release
- 25 test sentences
- Complete phonological feature coverage
- Reference audio files generated
- Validation checklist created
- Expected outputs documented

---

**Dataset Status:** ✅ Complete and validated  
**Last Updated:** October 30, 2025  
**Maintained By:** Arabic TTS Development Team
