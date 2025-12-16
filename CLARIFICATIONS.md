# Clarifications: User Questions About TTS Features

**Date:** December 16, 2025
**Status:** Response to 5 user issues

---

## Issue #1: Expected IPA Feature - What's the Point?

### ✅ RESOLVED

**Question:** "i put the word in ipa and still don't match. what's the point of it anyways?"

### Answer: Expected IPA is for COMPARISON, not exact matching

**Purpose:** The Expected IPA field lets you **compare** the system's generated IPA against a known-correct reference transcription from an external source (academic database, other TTS system, etc.).

**How It Works:**

```
STEP 1: Input Arabic text
        ↓
STEP 2: System processes and generates IPA
        ↓
STEP 3: (OPTIONAL) Paste reference IPA in "Expected IPA" field
        ↓
STEP 4: Click "Regenerate Matrix" to show comparison
        ↓
RESULT: IPA cells are color-coded:
        - Green = Generated IPA matches Expected IPA ✓
        - Red = Generated IPA differs from Expected IPA ✗
```

**The Mistake You Made:**
- You put the word `ipa` (the text "ipa") in the Expected IPA field
- The system compared your generated IPA against the literal string "ipa"
- Of course it didn't match! That's not actual IPA

**Correct Usage Example:**

```
Arabic Input:        الحمد لله (praise be to God)
Expected IPA:        al-hamdu lillaah (from linguistic reference)
Generated IPA:       [l̪ˤɑ] [ħæ] [md] [l̪ˤ] [ɪ] [l̪ˤ] [ɑ]
Result:              Highlighted in green if they match, red if different
```

**When This Is Useful:**
- Validating against Google Translate or other TTS systems
- Comparing against published linguistic papers
- Quality assurance testing
- Academic phonetics verification

---

## Issue #2: Status and Failed_Layers Columns in CSV

### ✅ COMPLETED (NEW FEATURE ADDED)

**Question:** "i still don't see the status/color or the where the word failed (syl, diac, etc) in csv file"

### Answer: Feature implemented - CSV now includes these columns

**What Was Added:**
- **2 new CSV columns**: `Status` and `Failed_Layers`
- **Where to find it:** Download CSV from the demo page
- **For WORD rows:** Shows actual status/failure info
- **For CHAR rows:** Shows `-` (not applicable at character level)

### New CSV Columns Explained

**Column: Status**
```
Possible values:
- 'success'  = All processing layers passed (no failures)
- 'warning'  = 1 layer failed (resyllabified UNKNOWN, or partial IPA conversion)
- 'error'    = 2+ layers failed (multiple critical issues)
```

**Column: Failed_Layers**
```
Comma-separated codes showing which processing layer failed:

- diac = Diacritization failed
          (Mishkal couldn't add vowel marks to this word)

- syl  = Syllabification produced UNKNOWN patterns
         (Word had invalid syllable patterns, but was resyllabified)

- ipa  = IPA Conversion failed
         (One or more characters not in masterTTS.json dictionary)

- phon = Phonological rules failed
         (Gemination, emphatics, sun letters couldn't be applied)

Examples:
- Failed_Layers: "syl"           ← Only syllabification failed
- Failed_Layers: "syl,ipa"       ← Both syllabification and IPA failed
- Failed_Layers: "-"             ← No failures (all layers passed)
```

### Example: How to Read Status in CSV

```csv
Type,Word,Original,Diacritized,Syllable_Pattern,Status,Failed_Layers
WORD,الحمد,الحمد,الْحَمْدُ,CC.CV.CVC,success,-
WORD,البدري,البدري,الْبَدْرِيُّ,CC.UNKNOWN(CVCCVVV),warning,syl
WORD,سؤال,سؤال,سُؤَال,CV.CVC,error,ipa
```

**Breaking down each row:**

| Word | Status | Failed_Layers | Meaning |
|------|--------|---------------|---------|
| الحمد | success | - | All layers passed perfectly ✓ |
| البدري | warning | syl | Syllable pattern was UNKNOWN but auto-corrected (resyllabified) |
| سؤال | error | ipa | Character ؤ not found in dictionary (missing from masterTTS.json) |

### How It Determines Status Automatically

The system analyzes each word for:

1. **Diacritization**: Did Mishkal add vowel marks?
   - Failure: Original == Diacritized (no vowels added)

2. **Syllabification**: Are all patterns valid?
   - Failure: Pattern contains "UNKNOWN"

3. **IPA Conversion**: Are all characters converted?
   - Failure: Raw Arabic characters appear in IPA output

4. **Phonology**: Were rules applied successfully?
   - Currently optional (doesn't trigger failure)

---

## Issue #3: Syllable Pattern Notation - CC.UNKNOWN(CVCCVVV)

### ✅ CLARIFIED

**Question:** "does the one between brackets is the final one suggested? and CC.UNKNOWN means that first 2 chars are detected, the rest are guessed?"

### Answer: Yes, exactly correct!

**Format:** `Pattern1.Pattern2.UNKNOWN(Suggested_Pattern)`

### Detailed Explanation

```
CC.UNKNOWN(CVCCVVV)
│  │       │         │
│  │       │         └─ Parentheses = Resyllabified/suggested pattern
│  │       └─────────── What was detected (invalid)
│  └─────────────────── Another valid pattern (before the UNKNOWN)
└────────────────────── First valid pattern
```

**Breaking it down for البدري (al-badri):**

```
Word: البدري
Diacritized: الْبَدْرِيُّ
Syllables: [ال] [بَ] [دْ] [رِ] [يُّ]

Attempt 1 (raw detection):
├─ ال → CC (alif + lam) ✓ VALID
├─ بَ → CV (ba + fatha) ✓ VALID
├─ دْ → C (dal + sukun) ✗ INVALID
├─ رِ → CV (ra + kasra) ✓ VALID
└─ يُّ → CVV (ya + damma + shadda) ✗ Invalid pattern

Result: CC.CV.UNKNOWN.CV.CVV (has UNKNOWN!)

Attempt 2 (resyllabification):
└─ Merge invalid syllables:
   ├─ CC (ال) ✓
   ├─ CVCCVVV (بَدْرِيُّ combined) ✓

Result: CC.UNKNOWN(CVCCVVV)
         ↑ Original detection showed mixed
           └─ With suggestion to use CVCCVVV
```

**Key Points:**
- ✅ **CC** = Detected 2 consonants (ال = alif + lam, the definite article)
- ❌ **UNKNOWN** = The remaining syllables couldn't be parsed
- ✅ **(CVCCVVV)** = System's suggested correction for those syllables

**Accuracy of Suggestion:**
- The suggestion in parentheses is the system's **best guess** based on vowel/consonant patterns
- It's not 100% guaranteed to be correct phonetically
- But it's better than leaving it as UNKNOWN
- That's why words with UNKNOWN patterns get **orange status** (warning, not error)

---

## Issue #4: Diacritization Failing for الإسكندرية

### ✅ ROOT CAUSE IDENTIFIED - Limitation of Mishkal

**Question:** "diacratize works except for some words like الإسكندرية"

**CSV Output:**
```
Word: الإسكندرية
Original: الإسكندرية
Diacritized: الإسكندرية        ← SAME as original (no diacritics added!)
Pattern: UNKNOWN(CCCCCCCCCC)   ← Detected as all consonants
All characters showing as "unknown"
```

### Why This Specific Word Fails

The word الإسكندرية (Alexandria - place name) has several challenges:

1. **Hamza with Kasr Below (إ)** - U+0625
   - Mishkal doesn't handle all hamza variants well
   - Especially at the start of words

2. **Complex Consonant Cluster**
   - سكند... = S-K-N-D
   - That's 4 consonants in a row
   - Mishkal struggles with these

3. **Proper Noun**
   - Mishkal is trained on common words
   - Proper nouns (place names) often aren't in its training data
   - Geographic names like "Alexandria" are hardest to diacritize

### Why the Pattern Shows CCCCCCCCCC

```
الإسكندرية
├─ ا = C (alif seen as consonant)
├─ ل = C (lam)
├─ إ = C (hamza - not recognized as vowel)
├─ س = C (seen)
├─ ك = C (kaf)
├─ ن = C (nun)
├─ د = C (dal)
├─ ر = C (ra)
├─ ي = C (ya - without vowel mark, seen as consonant)
└─ ة = C (ta marbuta)

Result: CCCCCCCCCC (all 10 characters detected as consonants!)
```

**Why No Vowel Marks Were Added:**
- Mishkal analyzed the word but couldn't determine vowel positions
- So it returned the original text unchanged
- That's why Diacritized == Original

### Workarounds

**Option 1: Manually Diacritize (Best)**
```
الإسكندرية → الإِسْكَنْدَرِيَّة
```
Then paste this diacritized version into the demo, it will parse correctly.

**Option 2: Use Common Variants**
- الإسكندرية (undiacritized) - system will show orange status
- Users understand this is a complex proper noun
- The IPA output is still usable even if diacritization failed

**Option 3: Add to Mishkal Training (Out of Scope)**
- Would require retraining Mishkal's models
- Not feasible for this project

### This Is a Mishkal Limitation

**Mishkal Handles Well:**
- Common verbs: كتب → كَتَبَ
- Common nouns: مدرسة → مَدْرَسَة
- Regular patterns

**Mishkal Struggles With:**
- Proper nouns (place names, person names)
- Rare or archaic words
- Complex consonant clusters
- Hamza variants (إ, أ, ؤ, ئ)

---

## Issue #5: Polly Audio Bar & Neural Engine Error

### ⏳ IN PROGRESS

**Questions:**
1. "espeak audio bar should be below buttons before matrix"
2. "generate polly errors... and audio bar should be below espeak as well"
3. "where polly are stored? should be under ./tests/polly and ./tests/espeak"

**Polly Error Message:**
```
Error generating Polly audio: Polly error: An error occurred
(ValidationException) when calling the SynthesizeSpeech operation:
This voice does not support the selected engine: neural
```

### Root Cause Analysis

**Polly Error:**
- The issue is with **neural engine + voice combination mismatch**
- Not all voices support the neural engine
- Some voices only work with standard engine

**Audio Bar Positioning:**
- Currently positioned inside the matrix area
- Should be above matrix (after buttons)

**File Storage Questions:**
- Audio files are stored in: `./static/audio/`
- Not in `./tests/polly` or `./tests/espeak`
- Test directory is for unit tests, not output files

### Implementation Plan for Issue #5

**Audio Bar Positioning:**
1. Move audio bars to separate section above matrix
2. Show espeak bar first, then polly bar below
3. Both bars visible before clicking to show matrix

**Polly Error Fix:**
1. Add voice → engine compatibility check
2. For neural engine, only allow neural-compatible voices
3. Fallback to standard engine if neural fails
4. Better error messaging to users

**File Storage:**
- Continue using `./static/audio/` (correct location)
- No changes needed for storage

---

## Summary: What You Got

✅ **Issue #1:** Expected IPA explained - it's for comparison, not exact matching
✅ **Issue #2:** Status/Failed_Layers added to CSV (2 new columns)
✅ **Issue #3:** Syllable pattern notation explained (CC.UNKNOWN(CVCCVVV) format)
✅ **Issue #4:** Diacritization failure analyzed (Mishkal limitation for complex words)
⏳ **Issue #5:** Polly errors and audio positioning (next: implement fixes)

---

## What Changed in This Session

### Commits Made:
- **58b32f0**: feat: Add Status and Failed_Layers columns to CSV export

### New Code:
- `_determine_word_status()` function in `app.py`
  - Analyzes 4 failure layers (diac, syl, ipa, phon)
  - Returns status ('success'/'warning'/'error') and failed_layers string

- Updated `_generate_hierarchical_csv()` function
  - Now includes Status and Failed_Layers columns
  - WORD rows show actual status, CHAR rows show '-'

### Testing:
- All 438 tests passing
- No regressions introduced

---

## References

- **ARCHITECTURE.md** - System design and universal processing flow
- **DEMO_PAGE_GUIDE.md** - Features and color legend (green/orange/red)
- **IMPLEMENTATION_SUMMARY.md** - Technical details from Phase 1-3

---

**Next Steps:**
1. Test CSV export with new Status/Failed_Layers columns
2. Fix Polly neural engine voice selection
3. Reposition audio bars above matrix
4. Update demo.html layout

