# Interactive TTS Demo Page Guide

**Document:** Demo Page Features & User Guide
**Version:** 1.0
**Date:** December 15, 2025

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [User Interface](#user-interface)
4. [Color Legend](#color-legend)
5. [Status Indicators](#status-indicators)
6. [Word Processing Layers](#word-processing-layers)
7. [Data Export](#data-export)

---

## Overview

The Interactive TTS Demo Page provides a visual representation of how the Arabic TTS system processes text at each layer of the pipeline. It allows users to:

- Input Arabic text for processing
- View syllabification results
- See IPA phonetic transcriptions
- Understand processing quality through color-coded status
- Export results in CSV format for analysis

The demo page implements the **Universal Processing Architecture** where:
1. Text is **diacritized** (vowel marks added automatically)
2. Text is **syllabified** (split into syllables with valid patterns)
3. **Phonological rules** are applied (gemination, sun letters, emphatics, position)
4. **IPA conversion** happens with dialect-specific mappings

---

## Features

### 1. **Dialect Selection**
- **Supported Dialects:**
  - Egyptian Arabic (EG) - Default
  - Modern Standard Arabic (MSA)
  - Gulf Arabic
  - Levantine Arabic
  - Maghrebi Arabic
- Switch dialects dynamically to see how pronunciation varies by region

### 2. **Real-Time Processing**
- Input Arabic text in the textarea
- Processing happens immediately upon input
- View all intermediate steps in the output table

### 3. **Multi-Layer Visualization**
The output displays TWO rows per word:

**WORD ROW** - Word-level metadata:
- Original Arabic text
- Processing status (✓ success / ⚠ warning / ✗ error)
- Which processing layers failed
- Full IPA transcription

**CHAR ROW** - Character-level breakdown:
- Diacritized characters with vowel marks
- Syllable boundaries and patterns (CV, CVC, CVV, CVCC, etc.)
- Individual IPA values for each character
- Position information (initial/medial/final)

### 4. **Status Tracking**
Each word is processed through multiple layers:
- **Diacritization (diac)** - Mishkal adds vowel marks
- **Syllabification (syl)** - Words split into syllables with valid patterns
- **IPA Conversion (ipa)** - Characters mapped to phonetic sounds
- **Phonological Rules (phon)** - Gemination, emphatics, sun letters applied

---

## User Interface

### Input Section
```
┌──────────────────────────────────────────┐
│ Dialect Selection: [Dropdown: EG/MSA/...]  │
│                                          │
│ Input Arabic Text:                       │
│ ┌─────────────────────────────────────┐  │
│ │ الحمد لله                             │  │
│ │ مرحبا، كيف حالك؟                      │  │
│ └─────────────────────────────────────┘  │
│                                          │
│ [Process] [Clear] [Download CSV]        │
└──────────────────────────────────────────┘
```

### Output Section
```
┌────────────────────────────────────────────────────────┐
│ Processing Results                                     │
├────────────────────────────────────────────────────────┤
│ WORD     | Status  | Failed Layers | IPA              │
├──────────┼─────────┼───────────────┼──────────────────┤
│ الحمد    | ✓       | -             | [l̪ˤɑ] [ħæ]...   │
├──────────┼─────────┼───────────────┼──────────────────┤
│ CHAR     | Syl#   | Pattern      | IPA | Position   │
├──────────┼────────┼──────────────┼─────┼────────────┤
│ ا       | 1      | CV           | [l̪ˤ] | initial   │
│ ل       | 1      | (cont.)      | (cont.) | medial   │
│ ح       | 2      | CV           | ħ   | medial    │
│ م       | 2      | (cont.)      | (cont.) | medial   │
│ د       | 2      | (cont.)      | d   | final     │
└─────────────────────────────────────────────────────────┘
```

---

## Color Legend

### Word Status Colors

The demo page uses a color-coded system to indicate processing quality:

#### **🟢 Green (Success)**
- **Status:** ✓
- **Meaning:** All processing layers passed successfully
- **IPA Accuracy:** 100% of characters converted to IPA
- **Syllable Patterns:** All valid (CV, CVC, CVV, CVCC, etc.)
- **Example:** الحمد (al-praise)

#### **🟠 Orange (Warning)**
- **Status:** ⚠
- **Meaning:** Best-effort correction applied, may be inaccurate
- **IPA Accuracy:** >95% of characters converted
- **Syllable Patterns:** One or more UNKNOWN patterns detected but resyllabified
- **Failed_Layers:** One or more layers partially failed
- **Example:** وذلك (wa-dhalika) - complex syllable boundaries

#### **🔴 Red (Error)**
- **Status:** ✗
- **Meaning:** Critical failure, accuracy may be poor
- **IPA Accuracy:** <95% of characters converted
- **Syllable Patterns:** Unable to resyllabify invalid patterns
- **Failed_Layers:** Multiple critical failures
- **Example:** (rare - would show untranslatable characters)

### Processing Layer Failure Codes

When a word has a warning or error status, the `Failed_Layers` column shows which layers failed:

| Code   | Layer              | Meaning                                           |
|--------|-------------------|--------------------------------------------------|
| `diac` | Diacritization    | Mishkal couldn't properly add vowel marks         |
| `syl`  | Syllabification   | Word had UNKNOWN syllable patterns (resyllabified) |
| `ipa`  | IPA Conversion    | One or more characters not in masterTTS.json     |
| `phon` | Phonological      | Gemination/emphatic/sun-letter rules failed      |

**Example:**
- Word with `Failed_Layers: "syl,ipa"` had both syllabification issues (UNKNOWN pattern) AND missing characters in the dictionary

---

## Status Indicators

### Character-Level Status

Each character in a word shows:

- **Diacritization Status:** Original character → Diacritized character
  - Example: "كتاب" → "كِتَابٌ" (Added vowel marks)

- **Syllable Information:**
  - Syllable number (which syllable this character belongs to)
  - Pattern (CV, CVC, CVV, CVCC, etc.)
  - Position in word (initial, medial, final)

- **IPA Conversion:**
  - Phonetic symbol (ʔ, æ, ħ, etc.)
  - Individual IPA for character OR full IPA for syllable

---

## Word Processing Layers

### Layer 1: Diacritization (Mishkal)

**Input:** الحمد
**Output:** الْحَمْدُ

- Automatic addition of vowel marks
- Uses Mishkal v0.4.1 library
- Makes syllabification more accurate
- **Success Rate:** ~95% (some complex words may not diacritize perfectly)

### Layer 2: Syllabification

**Input:** الْحَمْدُ
**Output:** [ال] [حَ] [مْدُ]

- Split into syllables with patterns:
  - ال = CC (definite article)
  - حَ = CV
  - مْدُ = CVC

- Valid patterns: CV, CVC, CVCC, CVV, CVVC, CCV, VC, V, C, CC
- **Success Rate:** ~95% (post-resyllabification)

### Layer 3: Phonological Processing

**Input:** Syllables with diacritics
**Output:** Syllables with processing flags

Applies universal rules:
- **Gemination:** Detect shadda (ّ) marks
- **Sun Letters:** Detect ال + sun letter assimilation
- **Position Detection:** Word-initial, word-medial, word-final
- **Emphatic Spread:** Detect emphatic consonants (ص،ض،ط،ظ)

- **Success Rate:** ~98%

### Layer 4: IPA Conversion

**Input:** Processed syllables
**Output:** IPA transcription

- Uses dialect-specific mappings from masterTTS.json
- Applies position-specific pronunciations
- 237 character entries for Egyptian Arabic
- **Success Rate:** ~96% (some rare characters may not be covered)

---

## Data Export

### CSV Download

Click **"Download CSV"** to export results in Excel-compatible format:

```csv
Type,Word,Status,Failed_Layers,Position,Original,Diacritized,Syllable_Pattern,IPA,X_SAMPA
WORD,الحمد,success,,-,الحمد,الْحَمْدُ,CC.CV.CVC,[l̪ˤɑ][ħæ][md],al_ha:md
CHAR,ا,success,-,1,initial,ا,CC,[l̪ˤ],-
CHAR,ل,success,-,1,medial,ل,(cont.),∅,-
CHAR,ح,success,-,2,medial,ح,CV,ħ,X
CHAR,م,success,-,3,medial,م,CVC,m,m
CHAR,د,success,-,3,final,د,(cont.),d,d
```

**Columns:**
- `Type`: WORD or CHAR (word-level or character-level data)
- `Word`: The word being processed
- `Status`: success / warning / error
- `Failed_Layers`: Comma-separated codes (diac, syl, ipa, phon)
- `Position`: initial / medial / final
- `Original`: Original undiacritized text
- `Diacritized`: Text with vowel marks added
- `Syllable_Pattern`: CV, CVC, CVCC, etc.
- `IPA`: International Phonetic Alphabet
- `X_SAMPA`: ASCII-safe representation for eSpeak/Polly

---

## Processing Quality Metrics

The demo page shows aggregate quality metrics:

**Accuracy Percentage:**
- Calculated as: (Characters with IPA / Total Characters) × 100
- Target: >95%
- Red warning: <95%

**UNKNOWN Pattern Percentage:**
- Calculated as: (Syllables with UNKNOWN / Total Syllables) × 100
- Target: <5% (indicates resyllabification handled them)
- Orange warning: >5%

**Coverage Summary:**
- Total words processed
- Words with 100% IPA accuracy (green)
- Words needing resyllabification (orange)
- Words with missing characters (red)

---

## Common Issues & Solutions

### Problem: Orange Status on Common Words

**Cause:** Syllabification produced UNKNOWN patterns, which were then resyllabified automatically

**Solution:** This is normal - the system auto-corrects invalid patterns. Orange status is still acceptable for most uses.

### Problem: Red Status with Missing Characters

**Cause:** Character not in masterTTS.json dictionary for selected dialect

**Solution:**
- Try different dialect (character may be supported in MSA)
- Report the missing character for dictionary update

### Problem: Different IPA from Expected

**Cause:** Dialect-specific pronunciation differences

**Example:**
- "ثلاثة" in Egyptian: [t] (merges ث with ت)
- "ثلاثة" in MSA: [θ] (keeps distinct ث sound)

**Solution:** Select different dialect to see regional variations

---

## Technical Details

### Architecture Alignment

The demo page visualizes the **Universal Processing Architecture**:

```
Input Text
    ↓
[Step 1: Diacritization - Mishkal]
    ↓
[Step 2: Syllabification]
    ↓
[Step 3: Phonological Processing]
    ├─ Gemination Detection
    ├─ Sun Letter Processing
    ├─ Position Detection
    └─ Emphatic Processing
    ↓
[Step 4: IPA Conversion - masterTTS.json]
    ↓
IPA Output (Dialect-Specific)
```

### Processing Order

1. **Diacritization is FIRST** - Mishkal adds vowel marks before syllabification
2. **Syllabification is SECOND** - Operating on diacritized text
3. **Phonological rules are THIRD** - Universal rules applied to all dialects
4. **IPA lookup is LAST** - Dialect-specific mappings applied at the end

This order ensures:
- Maximum accuracy in syllabification
- Consistent phonological processing
- Flexible dialect switching
- Testable, maintainable architecture

---

## Version History

| Version | Date         | Changes |
|---------|------------|---------|
| 1.0     | Dec 15, 2025 | Initial documentation for demo page with status tracking |

---

## Contact & Support

For issues or feature requests:
- GitHub Issues: https://github.com/amrhas82/ArabicTTS/issues
- Questions about the demo page: See ARCHITECTURE.md for system design details

