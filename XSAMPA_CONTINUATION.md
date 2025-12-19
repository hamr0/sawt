# X-SAMPA Comprehensive Fix - Continuation Document

**Date:** December 18, 2025
**Status:** In Progress - Session Paused
**Priority:** HIGH - Needed for Polly Integration

---

## 🎯 Executive Summary

**Problem:** Polly works for SOME words but not ALL because X-SAMPA conversion is incomplete and masterTTS.json has errors.

**Root Causes Found:**
1. ✅ **FIXED:** `hierarchical_processor.py` had incomplete X-SAMPA converter (20 mappings) - Now has 50+ comprehensive mappings
2. ❌ **TODO:** `main.py` doesn't generate X-SAMPA for syllables (only hierarchical_processor does for CSV export)
3. ❌ **TODO:** `masterTTS.json` has 10+ errors in `*X-SAMPA` field (wrong mappings like 'd' → 'ˈ', 'n' → 'ew~ow')

**Goal:** Make X-SAMPA the single source of truth for ALL TTS engines (Polly, Google, Azure, future engines)

---

## 📊 What Was Done (Completed)

### ✅ 1. Updated hierarchical_processor.py with Comprehensive X-SAMPA Converter

**File:** `/home/hamr/PycharmProjects/ArabicTTS/src/core/hierarchical_processor.py`
**Lines:** 569-685
**Status:** COMPLETED

**Changes Made:**
- Replaced incomplete 20-mapping converter with comprehensive 50+ mapping converter
- Added all Arabic phonemes: consonants, emphatics (tˁ, sˁ, dˁ, ðˁ), pharyngeals (ʕ, ħ), vowels, long vowels, diphthongs
- Added length-based sorting to handle multi-character sequences correctly (e.g., 'aː' matched before 'a')
- Added Arabic diacritic stripping (َ ُ ِ ْ ٌ ّ etc.)
- Added square bracket removal ([ʔ] → ʔ)

**New Mappings Include:**
```python
# Emphatics (were missing)
'tˁ': 't_?',  # Emphatic t - ط
'sˁ': 's_?',  # Emphatic s - ص
'dˁ': 'd_?',  # Emphatic d - ض
'ðˁ': 'D_?',  # Emphatic dh - ظ

# Pharyngeals (were missing)
'ʕ': '?\\',   # Voiced pharyngeal - ع
'ħ': 'X\\',   # Voiceless pharyngeal - ح

# Others (were missing)
'ʔ': '?',     # Glottal stop - ء
'q': 'q',     # Qaf - ق
'ɣ': 'G',     # Ghain - غ
'x': 'x',     # Kha - خ
```

**Test Results:**
- ✅ Syntax valid
- ❌ X-SAMPA output still empty (because main.py doesn't call the converter for syllables)

---

## 🔴 Critical Issues Found in masterTTS.json

### Errors in `*X-SAMPA` Field

**File:** `/home/hamr/PycharmProjects/ArabicTTS/data/dictionaries/masterTTS.json`

**Structure Issue:**
```json
{
  "Arabic letter": "أ",
  "IPA": "ʔ",
  "X-SAMPA": "ʔ",      // ← WRONG (still IPA, not ASCII)
  "*X-SAMPA": "?"      // ← CORRECT (ASCII X-SAMPA)
}
```

**Confirmed Errors (10 entries):**

| Char | IPA | Wrong *X-SAMPA | Correct *X-SAMPA |
|------|-----|----------------|------------------|
| د | n | ew~ow | n |
| د | d | ˈ | d |
| ب | m | k | m |
| ي | ɪ | I~e[4] | I |
| ي | e | I~e[4] | e |
| و | ʊ | U~o[5] | U |
| و | o | U~o[5] | o |
| و | u | ew~ow | u |

**Accuracy:** 95.8% (227/237 correct in EG dialect)

**Issue:** The `*X-SAMPA` field appears to have copy-paste errors or was populated incorrectly.

---

## 📋 What Needs to Be Done (TODO)

### Priority 1: Add X-SAMPA to main.py (IMMEDIATE - 30 min)

**Goal:** Make ALL syllables in TTS results have `xsampa` field automatically

**File to Modify:** `/home/hamr/PycharmProjects/ArabicTTS/src/main.py`

**Where to Add:** In the `syllabify_and_map()` method around line 905-950

**What to Add:**

```python
# After IPA mapping, add X-SAMPA for each syllable
from src.core.hierarchical_processor import HierarchicalProcessor

hierarchical_processor = HierarchicalProcessor()

for syllable in syllables:
    ipa = syllable.get('ipa', '')
    xsampa = hierarchical_processor._convert_to_xsampa(ipa)
    syllable['xsampa'] = xsampa
```

**Why This Matters:**
- Currently X-SAMPA only exists in CSV exports (hierarchical_processor)
- Standard TTS result has no `xsampa` field in syllables
- Polly integration needs X-SAMPA from syllables directly

**Test After Implementation:**
```bash
python3 test_comprehensive_xsampa.py
# Should show filled X-SAMPA values, not empty strings
```

---

### Priority 2: Research & Fix masterTTS.json X-SAMPA (1-2 hours)

**Goal:** Correct all 1,030 entries in masterTTS.json to have accurate `*X-SAMPA` values

**Authoritative Sources to Consult:**

1. **X-SAMPA Official Specification**
   - URL: https://www.phon.ucl.ac.uk/home/sampa/x-sampa.htm
   - Primary reference for IPA → X-SAMPA mappings

2. **IPA Chart (International Phonetic Association)**
   - URL: https://www.internationalphoneticassociation.org/content/ipa-chart
   - Verify IPA symbols are correct first

3. **Arabic Phonology References**
   - Watson, Janet C.E. (2002). "The Phonology and Morphology of Arabic"
   - Holes, Clive (2004). "Modern Arabic: Structures, Functions, and Varieties"

4. **X-SAMPA for Arabic (Academic Papers)**
   - Search: "X-SAMPA Arabic phonemes"
   - Verify dialect-specific allophones

**Methodology:**

**Step 1: Create Authoritative Mapping Table**
```python
# Generate from research
AUTHORITATIVE_IPA_TO_XSAMPA = {
    # Consonants
    'b': 'b',
    't': 't',
    'tˁ': 't_?',  # Verify with sources
    # ... (all Arabic phonemes)
}
```

**Step 2: Validate Current masterTTS.json**
```python
# Script to check all entries
import json

with open('data/dictionaries/masterTTS.json') as f:
    data = json.load(f)

errors = []
for dialect in data:
    for entry in data[dialect]:
        ipa = entry.get('IPA', '')
        current_xsampa = entry.get('*X-SAMPA', '')
        correct_xsampa = AUTHORITATIVE_IPA_TO_XSAMPA.get(ipa)

        if correct_xsampa and current_xsampa != correct_xsampa:
            errors.append({
                'dialect': dialect,
                'char': entry.get('Arabic letter'),
                'ipa': ipa,
                'current': current_xsampa,
                'correct': correct_xsampa
            })

print(f"Found {len(errors)} errors to fix")
```

**Step 3: Auto-Fix masterTTS.json**
```python
# Update all *X-SAMPA fields
for dialect in data:
    for entry in data[dialect]:
        ipa = entry.get('IPA', '')
        if ipa in AUTHORITATIVE_IPA_TO_XSAMPA:
            entry['*X-SAMPA'] = AUTHORITATIVE_IPA_TO_XSAMPA[ipa]

# Save corrected version
with open('data/dictionaries/masterTTS.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
```

**Step 4: Validate Against Multiple Sources**
- Cross-check with X-SAMPA official spec
- Verify with Arabic phonology textbooks
- Test sample words with corrected mappings

---

### Priority 3: Make masterTTS.json the Single Source of Truth (1 hour)

**Goal:** Extract X-SAMPA directly from masterTTS.json instead of using hardcoded converter

**File to Modify:** `/home/hamr/PycharmProjects/ArabicTTS/src/core/ipa_mapper.py`

**Current Behavior (Line 173):**
```python
ipa = entry.get("IPA", "")  # Only extracts IPA
```

**New Behavior:**
```python
# Build lookup table with both IPA and X-SAMPA
ipa = entry.get("IPA", "")
xsampa = entry.get("*X-SAMPA", "")  # Extract X-SAMPA too

# Store in lookup table
lookup[char][position] = {
    'ipa': ipa,
    'xsampa': xsampa  # New field
}
```

**Modify `map_to_ipa()` Method:**
```python
def map_to_ipa(self, syllables, dialect):
    """Returns both IPA and X-SAMPA"""

    for syllable in syllables:
        for char in syllable:
            mapping = self._lookup(char, position, dialect)
            char['ipa'] = mapping['ipa']
            char['xsampa'] = mapping['xsampa']  # NEW

    return syllables
```

**Fallback Strategy:**
If `*X-SAMPA` is missing or empty, use the comprehensive converter from `hierarchical_processor` as fallback:

```python
xsampa = entry.get("*X-SAMPA", "")
if not xsampa:
    # Fallback to conversion
    from src.core.hierarchical_processor import HierarchicalProcessor
    converter = HierarchicalProcessor()
    xsampa = converter._convert_to_xsampa(ipa)
```

---

## 🧪 Testing Plan

### Test 1: Verify X-SAMPA Output

**Script:** `test_comprehensive_xsampa.py` (already created)

**Run:**
```bash
python3 test_comprehensive_xsampa.py
```

**Expected Output:**
```
Word: صباح (morning - emphatic s + pharyngeal)
  FULL IPA:     sˁɑbɑːħ
  FULL X-SAMPA: s_?Aba:X\     ← Should be filled, not empty
  ✅ X-SAMPA is ASCII-safe
```

**Success Criteria:**
- All X-SAMPA fields have values (not empty)
- All X-SAMPA is ASCII-safe (no Unicode IPA characters)
- Emphatics convert correctly (sˁ → s_?, tˁ → t_?, etc.)
- Pharyngeals convert correctly (ħ → X\\, ʕ → ?\\)

### Test 2: Polly Integration Test

**Location:** HTML page at `/templates/demo.html`

**Steps:**
1. Start Flask server: `python3 app.py`
2. Open http://localhost:5000
3. Enter test words: صباح، طعام، ضرب، ظهر، قلب، عين
4. Click "Process Text"
5. Download CSV and check last 2 rows for X-SAMPA
6. Click "Generate with Polly"
7. Listen to audio quality

**Success Criteria:**
- CSV shows X-SAMPA values in all rows
- Polly pronunciation is accurate for emphatics and pharyngeals
- No Arabic characters in X-SAMPA field (all ASCII)

### Test 3: Validate masterTTS.json Corrections

**After fixing X-SAMPA in masterTTS.json:**

```bash
# Validate all entries
python3 << 'EOF'
import json

with open('data/dictionaries/masterTTS.json') as f:
    data = json.load(f)

total = 0
valid = 0

for dialect in data:
    for entry in data[dialect]:
        ipa = entry.get('IPA', '')
        xsampa = entry.get('*X-SAMPA', '')

        if not ipa or not xsampa:
            continue

        total += 1

        # X-SAMPA should be ASCII (with allowed chars)
        allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:_?\\@~[]')
        if all(c in allowed or c == '∅' for c in xsampa):
            valid += 1
        else:
            print(f"Invalid X-SAMPA: {entry.get('Arabic letter')} | IPA: {ipa} | X-SAMPA: {xsampa}")

print(f"\nValidation: {valid}/{total} entries valid ({valid/total*100:.1f}%)")
EOF
```

---

## 📁 File Locations Reference

### Modified Files (Already Changed)
- `/home/hamr/PycharmProjects/ArabicTTS/src/core/hierarchical_processor.py` (lines 569-685) ✅

### Files to Modify (TODO)
- `/home/hamr/PycharmProjects/ArabicTTS/src/main.py` (around line 905-950) ❌
- `/home/hamr/PycharmProjects/ArabicTTS/data/dictionaries/masterTTS.json` (all 1,030 entries) ❌
- `/home/hamr/PycharmProjects/ArabicTTS/src/core/ipa_mapper.py` (lines 173, 185+) ❌

### Test Files
- `/home/hamr/PycharmProjects/ArabicTTS/test_comprehensive_xsampa.py` ✅ (created)
- `/home/hamr/PycharmProjects/ArabicTTS/templates/demo.html` (for manual testing)

### Reference Files
- `/home/hamr/PycharmProjects/ArabicTTS/src/integrations/espeak.py` (lines 46-129) - Has comprehensive converter as reference
- `/home/hamr/PycharmProjects/ArabicTTS/src/integrations/polly.py` - Polly integration

---

## 🔗 Key Insights from Investigation

### Why X-SAMPA Was Empty/Incomplete

1. **Pipeline Architecture Issue:**
   - `main.py` generates IPA for syllables
   - `hierarchical_processor.py` converts IPA → X-SAMPA for CSV export only
   - Standard TTS result has NO X-SAMPA in syllables
   - Result: Polly couldn't use X-SAMPA because it wasn't in the data structure

2. **Incomplete Converter Issue:**
   - Original converter had only 20 mappings
   - Missing: emphatics (tˁ, sˁ, dˁ, ðˁ), pharyngeals (ʕ, ħ), qaf (q), hamza (ʔ), etc.
   - Words with these phonemes had unconverted IPA in X-SAMPA field
   - Polly received mixed IPA/X-SAMPA and couldn't process it correctly

3. **masterTTS.json Data Quality Issue:**
   - `*X-SAMPA` field has 10+ confirmed errors
   - Appears to be copy-paste or auto-generation errors
   - Some entries have completely wrong mappings (d → ˈ, n → ew~ow)
   - Can't be used as source of truth until corrected

### Why This Matters for Polly

**Polly expects:**
- Pure X-SAMPA (ASCII-safe phonetic notation)
- SSML format: `<phoneme alphabet="x-sampa" ph="...">text</phoneme>`

**What happens with incomplete X-SAMPA:**
- Polly receives mixed IPA/X-SAMPA (Unicode + ASCII)
- Doesn't recognize unconverted IPA characters
- Falls back to built-in MSA pronunciation
- **Ignores your dialect-specific phonological processing**

**With complete X-SAMPA:**
- Polly receives pure ASCII phonetic notation
- Recognizes all phonemes
- Uses your linguistic work (gemination, sun letters, emphatic spread, allophones)
- **Produces dialect-accurate pronunciation**

---

## 🎯 Success Criteria (How to Know It's Fixed)

### Immediate Success (After Priority 1)
- [ ] `test_comprehensive_xsampa.py` shows filled X-SAMPA values
- [ ] All X-SAMPA is ASCII-safe (no Unicode IPA characters)
- [ ] CSV downloads from HTML page show X-SAMPA in all rows
- [ ] Polly pronunciation improves for emphatic words (صباح، طعام، ضرب، ظهر)

### Complete Success (After All Priorities)
- [ ] masterTTS.json has 100% accurate `*X-SAMPA` fields
- [ ] IPAMapper extracts X-SAMPA directly from masterTTS.json
- [ ] All 329 tests still pass
- [ ] Polly works for ALL words (not just some)
- [ ] X-SAMPA is single source of truth for all TTS engines

---

## 📞 Next Steps (Resuming Work)

### Step 1: Add X-SAMPA to main.py (30 min)
```bash
# Open the file
nano /home/hamr/PycharmProjects/ArabicTTS/src/main.py

# Find syllabify_and_map() method (line ~905)
# Add X-SAMPA generation after IPA mapping
# Save and test with test_comprehensive_xsampa.py
```

### Step 2: Test via HTML Page (User will do)
```bash
# Start server
python3 app.py

# Test words via browser at http://localhost:5000
# Generate Polly audio and compare quality
```

### Step 3: Research X-SAMPA Mappings (1-2 hours)
- Consult X-SAMPA official spec
- Cross-reference with Arabic phonology sources
- Create authoritative mapping table
- Document sources used

### Step 4: Fix masterTTS.json (30 min)
- Create validation script
- Auto-correct `*X-SAMPA` fields
- Verify with multiple sources
- Commit changes

### Step 5: Update IPAMapper (30 min)
- Extract X-SAMPA from masterTTS.json
- Add fallback to converter if missing
- Test with full pipeline

### Step 6: Validate Complete System (30 min)
- Run all 329 tests
- Test Polly with 20+ sample words
- Verify CSV exports
- Commit and document

---

## 💡 Additional Context

### Why Comprehensive X-SAMPA Matters

**Your Vision:** Use X-SAMPA for ANY TTS engine + add prosody features

**Future Enhancements Enabled:**
```xml
<!-- Pauses -->
<break time="500ms"/>

<!-- Emphasis -->
<emphasis level="strong">word</emphasis>

<!-- Speed -->
<prosody rate="slow">slower speech</prosody>

<!-- Pitch -->
<prosody pitch="+10%">higher pitch</prosody>

<!-- Volume -->
<prosody volume="loud">louder</prosody>
```

**With comprehensive X-SAMPA:**
- Works with Polly (Amazon)
- Works with Google Cloud TTS
- Works with Azure TTS
- Works with any SSML-compatible engine
- Preserves your linguistic work (1,030 entries, 4 phonological processors)

---

## 📚 References

### Authoritative Sources to Consult

1. **X-SAMPA Official**
   - URL: https://www.phon.ucl.ac.uk/home/sampa/x-sampa.htm
   - Definitive IPA → X-SAMPA mappings

2. **Wikipedia X-SAMPA**
   - URL: https://en.wikipedia.org/wiki/X-SAMPA
   - Quick reference with examples

3. **IPA Chart**
   - URL: https://www.internationalphoneticassociation.org/IPAcharts/IPA_chart_orig/pdfs/IPA_Kiel_2020_full.pdf
   - Verify IPA symbols

4. **Arabic Phonology (Academic)**
   - Watson (2002): Arabic phoneme inventory
   - Holes (2004): Dialectal variations
   - Behnstedt & Woidich (2005-2014): Arabic dialectology

### Code References

1. **eSpeak NG X-SAMPA**
   - Repository: https://github.com/espeak-ng/espeak-ng
   - File: `phsource/phonemes` (X-SAMPA definitions)

2. **Festival TTS**
   - X-SAMPA phoneme definitions
   - Arabic voice implementations

---

## ⚠️ Known Issues & Gotchas

### Issue 1: Arabic Diacritics in IPA String
**Problem:** IPA strings contain Arabic diacritics (َ ُ ِ ْ ٌ ّ)
**Solution:** Strip them before X-SAMPA conversion (already implemented in hierarchical_processor)

### Issue 2: Square Brackets in IPA
**Problem:** IPA has positional markers like [ʔ], [b]
**Solution:** Remove brackets before conversion (already implemented)

### Issue 3: Multi-Character Sequences
**Problem:** 'aː' matched as 'a' + 'ː' instead of single unit
**Solution:** Sort mappings by length (longest first) before replacement (already implemented)

### Issue 4: Missing Phonemes
**Problem:** Some IPA phonemes not in mapping table
**Solution:** Leave unconverted, log warning, use fallback pronunciation

### Issue 5: Dialect-Specific Allophones
**Problem:** Same phoneme may have different X-SAMPA in different dialects
**Solution:** Use `*X-SAMPA` from masterTTS.json which has dialect-specific entries

---

## 🔄 Version History

**v1.0 - 2025-12-18 (Current)**
- Identified root causes of X-SAMPA issues
- Fixed hierarchical_processor.py with comprehensive converter
- Created continuation document
- Status: Ready for Priority 1 implementation

---

## 📝 Notes for Next Session

1. **Start with Priority 1** - Add X-SAMPA to main.py first (quickest win)
2. **User will test via HTML** - They'll process words through web interface
3. **Research can happen in parallel** - While user tests, research X-SAMPA
4. **masterTTS.json has 1,030 entries** - Budget 1-2 hours for complete fix
5. **Keep tests passing** - Run `pytest tests/ -v` after each change

---

**END OF CONTINUATION DOCUMENT**

Resume work by starting with Priority 1: Add X-SAMPA to main.py
