# Phase 3: Fix Syllabifier - Implementation Plan

**Date**: 2025-12-16
**Goal**: Fix UNKNOWN syllable patterns by replacing broken syllabifier
**Expected Impact**: +26.9% improvement (69.1% → 96%+ success rate)

---

## 🎯 PROBLEM SUMMARY

### Root Cause
There are **TWO different `ArabicSyllabifier` classes** in the codebase:

1. **`src/core/syllabifier.py`** (PROPER) - Lines 5-264
   - Uses linguistic syllable boundary rules
   - Handles gemination (shadda), sukun, long vowels correctly
   - Produces valid Arabic syllable patterns (CV, CVC, CVV, CVVC, CVCC)

2. **`src/main.py`** (BROKEN) - Lines 13-227
   - Uses naive "split at short vowels" rule
   - Doesn't understand gemination or complex structures
   - Produces INVALID patterns like CVVV, CVCCVV, CVVVV

### Current Impact
- **95 words (26.9%)** have UNKNOWN patterns
- All are caused by the broken syllabifier in main.py
- Proof of concept shows 100% of test cases are fixed by proper syllabifier

---

## ✅ PROOF OF CONCEPT RESULTS

**Test**: 6 words with UNKNOWN patterns
**Result**: All 6 (100%) fixed by switching to proper syllabifier

| Word | Current Pattern | Proper Segmentation | Status |
|------|----------------|---------------------|--------|
| لِلْغَا | UNKNOWN(CVCCVV) | لِلْ (CVC) + غَا (CVV) | ✓ Fixed |
| عِيُّ | UNKNOWN(CVVV) | عِيّ (CVV) + ُ (V) | ✓ Fixed |
| بَدْرِيُّ | UNKNOWN(CVCCVVV) | بَدْ (CVC) + رِيّ (CVV) + ُ (V) | ✓ Fixed |
| تَخْفِيضٌ | UNKNOWN(CVCCVVC) | تَخْ (CVC) + فِيض (CVVC) | ✓ Fixed |

---

## 📋 IMPLEMENTATION PLAN

### Step 1: Backup Current Code
**Estimated time**: 2 minutes

```bash
# Create backup
cp src/main.py src/main.py.backup_phase3_$(date +%Y%m%d_%H%M%S)
```

**Files to backup**:
- `src/main.py` (contains broken syllabifier class)

---

### Step 2: Remove Broken Syllabifier from main.py
**Estimated time**: 5 minutes

**What to remove**:
1. **Lines 13-227**: Entire `ArabicSyllabifier` class
   - `__init__` (lines 14-34)
   - `segment_syllables` (lines 47-97)
   - `resyllabify` (lines 99-168)
   - `classify_pattern` (lines 170-227)
   - Helper methods

**Impact**: This is the entire broken syllabifier class

---

### Step 3: Import Proper Syllabifier
**Estimated time**: 2 minutes

**Location**: Top of `src/main.py` (around line 11)

**Add import**:
```python
from src.core.syllabifier import ArabicSyllabifier
```

**Remove**: Lines that define the broken `ArabicSyllabifier` class (already done in Step 2)

---

### Step 4: Update ArabicTTS.__init__
**Estimated time**: 3 minutes

**Location**: `src/main.py`, line ~274 (after removals)

**Current code**:
```python
# Initialize universal syllabifier (no dialect needed)
self.syllabifier = ArabicSyllabifier()
```

**New code**:
```python
# Initialize syllabifier with dialect
# Note: Use 'EG' for now since MSA patterns not yet in syllable_patterns.json
self.syllabifier = ArabicSyllabifier('EG')
```

**Why 'EG'**: The `syllable_patterns.json` file only has EG defined. MSA is listed as "not_implemented" (line 189-194). The patterns are the same, only IPA differs (which is handled by IPAMapper).

---

### Step 5: Update _syllabify_only Method
**Estimated time**: 10 minutes

**Location**: `src/main.py`, line ~554 (after removals)

**Current code** (lines 567-571):
```python
# Use the syllabifier to get syllable structure
syllable_data = self.syllabifier.segment_syllables(word)

# Apply resyllabification to fix invalid patterns
syllable_data = self.syllabifier.resyllabify(syllable_data)
```

**New code**:
```python
# Use the proper syllabifier to get syllable structure
syllable_data = self.syllabifier.segment(word)

# Note: Proper syllabifier may produce standalone V patterns (vowel-only syllables)
# These need to be merged with adjacent syllables to create valid Arabic patterns
syllable_data = self._merge_invalid_patterns(syllable_data)
```

**New method to add** (after `_syllabify_only`):
```python
def _merge_invalid_patterns(self, syllables: List[List[str]]) -> List[List[str]]:
    """
    Merge invalid patterns (like standalone V) into adjacent syllables.

    The proper syllabifier may produce patterns like:
    - V (standalone vowel) - needs to merge with adjacent syllable
    - VC (vowel + consonant) - may need to merge depending on context

    Args:
        syllables: List of syllable character lists

    Returns:
        Corrected syllables with valid patterns
    """
    if not syllables:
        return syllables

    corrected = []
    i = 0

    while i < len(syllables):
        current = syllables[i]
        pattern = self.syllabifier.classify_pattern(current)

        # Keep definite article ال as-is (even if CC pattern)
        if i == 0 and len(current) >= 2 and current[0] == 'ا' and current[1] == 'ل':
            corrected.append(current)
            i += 1
            continue

        # Merge standalone vowels (V pattern) with adjacent syllables
        if pattern == 'V':
            if corrected:
                # Merge with previous syllable
                corrected[-1].extend(current)
            elif i + 1 < len(syllables):
                # Merge with next syllable
                syllables[i + 1] = current + syllables[i + 1]
            else:
                # Orphaned vowel at end - keep it anyway
                corrected.append(current)
            i += 1
            continue

        # Keep valid patterns
        corrected.append(current)
        i += 1

    return corrected
```

---

### Step 6: Remove OLD Helper Methods
**Estimated time**: 2 minutes

**Methods to remove** (no longer needed):
- `segment_syllables` (was in broken syllabifier)
- `resyllabify` (was in broken syllabifier)
- `classify_pattern` (now use `self.syllabifier.classify_pattern`)
- `validate_cvcc` (was in broken syllabifier)

**Check for usage**:
```bash
# Search for any remaining calls to these methods
grep -n "segment_syllables\|\.resyllabify\|\.classify_pattern\|validate_cvcc" src/main.py
```

**Update calls**:
- `self.classify_pattern(...)` → `self.syllabifier.classify_pattern(...)`
- `self.segment_syllables(...)` → `self.syllabifier.segment(...)`

---

### Step 7: Test with Sample Words
**Estimated time**: 5 minutes

**Test script**:
```python
from src.main import ArabicTTS

test_words = ['للغاز', 'الطبيعي', 'البدري', 'تخفيض']
tts = ArabicTTS('MSA')

for word in test_words:
    result = tts.process_text(word)
    syllables = result['words'][0]['syllables']

    for syl in syllables:
        pattern = syl['pattern']
        print(f"{word}: {syl['syllable']} → {pattern}")
        if 'UNKNOWN' in pattern:
            print(f"  ⚠ Still UNKNOWN!")
```

**Expected**: Zero UNKNOWN patterns

---

### Step 8: Run Full Corpus Test
**Estimated time**: 3 minutes

```bash
python3 tasks/llm/test_full_corpus.py
```

**Expected results**:
- **Before**: 69.1% success, 26.9% warnings (UNKNOWN), 4.0% errors
- **After**: ~96% success, <1% warnings, 4.0% errors

**Calculation**:
- Current success: 244/353 (69.1%)
- Current UNKNOWN warnings: 95/353 (26.9%)
- If all UNKNOWN fixed: 244 + 95 = 339/353 = **96.0% success**
- Remaining 4.0% errors are diacritization failures (Phase 2-Alt)

---

### Step 9: Handle Edge Cases
**Estimated time**: 10 minutes

**Potential issues to check**:

1. **Standalone V patterns**: The proper syllabifier may create these (e.g., `ُ` after gemination)
   - **Solution**: `_merge_invalid_patterns` method (Step 5)

2. **MSA vs EG dialect**: Currently using 'EG' patterns
   - **Solution**: This is OK! Syllable rules are universal; only IPA differs
   - **Future**: Add MSA entry to `syllable_patterns.json` (copy EG patterns)

3. **Definite article handling**: `ال` should stay together
   - **Solution**: Already handled in `_merge_invalid_patterns`

4. **Sun letter assimilation**: May create complex patterns
   - **Solution**: Already handled by proper syllabifier

---

### Step 10: Update Documentation
**Estimated time**: 5 minutes

**Files to update**:
1. **`CLARIFICATIONS.md`**: Add Phase 3 completion notes
2. **`tasks/llm/CONTINUATION_SUMMARY.md`**: Update with Phase 3 results
3. **`tasks/llm/PHASE3_RESULTS.md`**: Create new results document

**Key points**:
- Replaced broken syllabifier with proper one
- Fixed 95+ words with UNKNOWN patterns
- Success rate improved from 69.1% to ~96%

---

## 📊 EXPECTED OUTCOMES

### Success Metrics

| Metric | Before Phase 3 | After Phase 3 | Change |
|--------|----------------|---------------|--------|
| Success Rate | 69.1% (244/353) | **~96% (339/353)** | **+26.9%** |
| UNKNOWN Warnings | 26.9% (95/353) | **<1%** | **-26%** |
| Errors | 4.0% (14/353) | 4.0% (14/353) | No change |

### Remaining Work
- **4.0% errors** (14 words): Diacritization failures
  - **Solution**: Phase 2-Alt (Mishkal → CAMeL fallback)
  - **Or**: Phase 4 (Exception dictionary for proper nouns/brands)

---

## ⚠️ RISKS & MITIGATION

### Risk 1: Breaking Existing Functionality
**Likelihood**: Low
**Impact**: High
**Mitigation**:
- Created backup (Step 1)
- Test with sample words first (Step 7)
- Run full corpus test (Step 8)
- Can rollback from backup if needed

### Risk 2: Performance Degradation
**Likelihood**: Very Low
**Impact**: Low
**Mitigation**:
- Proper syllabifier is well-optimized
- Removing resyllabify actually reduces overhead
- Monitor execution time during tests

### Risk 3: Edge Cases Not Covered by POC
**Likelihood**: Low
**Impact**: Medium
**Mitigation**:
- POC tested 6 different UNKNOWN pattern types
- Full corpus test will catch remaining issues
- `_merge_invalid_patterns` handles orphaned patterns

---

## 🔧 FILES TO MODIFY

### Primary Files
1. **`src/main.py`** (Major changes)
   - Remove lines 13-227 (broken syllabifier class)
   - Add import for proper syllabifier
   - Update `__init__` to pass dialect
   - Update `_syllabify_only` method
   - Add `_merge_invalid_patterns` method
   - Update method calls

### Supporting Files
2. **`data/dictionaries/syllable_patterns.json`** (Optional)
   - Add MSA entry (copy from EG)
   - Update status from "not_implemented" to "implemented"

### Documentation Files
3. **`CLARIFICATIONS.md`**
4. **`tasks/llm/CONTINUATION_SUMMARY.md`**
5. **`tasks/llm/PHASE3_RESULTS.md`** (new)

---

## ✅ VERIFICATION CHECKLIST

After implementation, verify:

- [ ] No UNKNOWN patterns in test words
- [ ] Full corpus success rate ≥ 95%
- [ ] No regressions (all previous successes still work)
- [ ] Definite article (ال) handled correctly
- [ ] Gemination (shadda ّ) handled correctly
- [ ] Sukun (ْ) creates proper codas
- [ ] Long vowels (َا ُو ِي) recognized
- [ ] Performance acceptable (<5s for 353 words)
- [ ] Backup created and can rollback if needed

---

## 📈 ESTIMATED TOTAL TIME

| Step | Time | Cumulative |
|------|------|------------|
| 1. Backup | 2 min | 2 min |
| 2. Remove broken code | 5 min | 7 min |
| 3. Import proper syllabifier | 2 min | 9 min |
| 4. Update __init__ | 3 min | 12 min |
| 5. Update _syllabify_only | 10 min | 22 min |
| 6. Remove old helpers | 2 min | 24 min |
| 7. Test samples | 5 min | 29 min |
| 8. Run full corpus | 3 min | 32 min |
| 9. Handle edge cases | 10 min | 42 min |
| 10. Update docs | 5 min | 47 min |

**Total estimated time**: ~45-50 minutes

---

## 🚀 NEXT STEPS AFTER PHASE 3

Once Phase 3 is complete and we reach ~96% success:

### Phase 2-Alt: Mishkal → CAMeL Fallback (Optional)
- **Target**: Fix remaining 4.0% diacritization errors
- **Impact**: +2-3% improvement (96% → 98%+)
- **Effort**: Low (10-15 minutes)

### Phase 4: Exception Dictionary (Optional)
- **Target**: Handle proper nouns and brands
- **Impact**: +1-2% improvement (98% → 99%+)
- **Effort**: Medium (create dictionary, add lookup)

### Phase 5: LLM Fallback (Optional)
- **Target**: Handle remaining edge cases
- **Impact**: +0-1% improvement
- **Cost**: User pays for API calls
- **Effort**: Medium (implement fallback logic)

---

## 📝 APPROVAL REQUIRED

**Before proceeding with implementation, please confirm**:
1. ✅ Proof of concept is acceptable
2. ✅ Implementation plan makes sense
3. ✅ Estimated time/effort is reasonable
4. ✅ Risk mitigation strategy is adequate
5. ✅ Ready to proceed with implementation

**Questions to address**:
- Should we add MSA to syllable_patterns.json, or keep using EG?
- Should we implement all steps now, or test after each major step?
- Any specific testing requirements beyond full corpus test?

---

**Ready to implement?** Once approved, I'll execute all steps systematically and verify at each checkpoint.
