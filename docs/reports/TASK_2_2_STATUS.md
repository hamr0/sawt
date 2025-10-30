# Task 2.2 Status: Implement Improved CV Pattern Detection

**Date:** October 30, 2025  
**Status:** ⚠️ INCOMPLETE (40% complete)  
**Time Spent:** ~2 hours  
**Estimated Remaining:** 4-6 hours

---

## What Was Accomplished (40%)

### ✅ Phase 1: Fixed Vowel/Diacritic Classification (COMPLETE)

**Problem:** Original code treated sukun (ْ), shadda (ّ), and long vowel markers (ا و ي) as vowels, causing incorrect syllable breaks.

**Solution Implemented:**
```python
# OLD (broken):
self.vowels = {'َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ا', 'ي', 'و'}

# NEW (fixed):
self.short_vowels = {'َ', 'ُ', 'ِ'}  # fatha, damma, kasra
self.long_vowel_markers = {'ا', 'و', 'ي'}  # alif, waw, yaa
self.sukun = 'ْ'  # marks no vowel (coda consonant)
self.shadda = 'ّ'  # gemination marker
self.diacritics = {'ْ', 'ّ', 'ً', 'ٌ', 'ٍ', 'ٓ'}  # all diacritical marks
```

**Result:** ✅ Proper classification of Arabic characters

---

### ✅ Phase 2: Rewrote classify_pattern() Method (COMPLETE)

**Changes:**
- Added proper handling of short vowels (َ ُ ِ) as V
- Added handling of long vowel markers after vowels as V
- Sukun now correctly skipped (not counted in pattern)
- Shadda handling added (marks gemination)
- Added support for additional patterns: V, VC, CCV, CC, C
- Returns detailed UNKNOWN(pattern) for debugging

**Code Location:** `src/core/syllabifier.py` lines 123-200

**Result:** ✅ Pattern classification logic improved

---

### ⚠️ Phase 3: Rewrote segment() Method (PARTIAL - 40% complete)

**Changes Made:**
- Implemented onset-nucleus-coda analysis framework
- Added lookahead logic for determining syllable boundaries
- Added long vowel detection (fatha+alif, etc.)
- Added diphthong detection framework (fatha+yaa+sukun)
- Added sukun handling for coda consonants
- Added shadda handling for gemination

**Current Status:**
- ✅ Simple CV syllables work: كَتَبَ → ['كَ', 'تَ', 'بَ'] = CV, CV, CV ✓
- ✅ Single syllable works: مَ → ['مَ'] = CV ✓
- ⚠️ CVC with sukun partially works: مَدْرَسَة → ['مَد', 'ْرَ', 'سَة'] = CVC, CV, CVC (should be CVC, CV, CV)
- ❌ Long vowels not working: كِتَاب → ['كِ', 'تَ', 'اب'] (should be ['كِ', 'تَاب'])
- ❌ Diphthongs not working: بَيْت → ['بَ', 'ي', 'ْت'] (should be ['بَيْت'])
- ❌ Gemination not working: مُدَرِّس → ['مُ', 'دَ', 'رِ', 'ّس'] (should be ['مُ', 'دَرْ', 'رِس'])

**Code Location:** `src/core/syllabifier.py` lines 29-117

**Result:** ⚠️ Basic cases work, complex cases still broken

---

## What Needs to Be Done (60%)

### 🔍 Investigation Needed

#### Issue 1: Sukun Placement in Segmentation
**Problem:** Sukun (ْ) is being included as a separate syllable element or in wrong position.

**Example:**
- Input: مَدْرَسَة (madrasa)
- Current: ['مَد', 'ْرَ', 'سَة'] → sukun attached to next syllable
- Expected: ['مَدْ', 'رَ', 'سَة'] → sukun should stay with previous consonant

**Research Needed:**
1. When does sukun mark coda vs. onset?
2. How to handle sukun in lookahead logic?
3. Should sukun always attach to previous consonant?

**Proposed Solution:**
- Modify segment() line 74-83 (sukun handling block)
- Change logic: when sukun encountered, it marks the *previous* consonant as coda
- Need to look *backward* not forward

**Estimated Time:** 2-3 hours

---

#### Issue 2: Long Vowel Detection Not Working
**Problem:** Long vowel markers (ا و ي) not being combined with preceding short vowels.

**Example:**
- Input: كِتَاب (kitaab)
- Current: ['كِ', 'تَ', 'اب'] → alif splits syllable
- Expected: ['كِ', 'تَاب'] → alif should combine with fatha

**Research Needed:**
1. When is ا/و/ي a long vowel vs. consonant?
2. How to detect long vowel *during* segmentation (not after)?
3. What about diphthongs (ay, aw)?

**Current Code Issue:**
```python
# Lines 56-70: Long vowel detection happens AFTER vowel added
# But segmentation logic already moved to next syllable
if word[i] in self.long_vowel_markers:
    current_syl.append(word[i])
    i += 1
```

**Problem:** This only works if we're still in the same syllable, but segment() may have already started next syllable.

**Proposed Solution:**
- Need to look ahead *before* closing syllable
- Check if next character is long vowel marker
- If yes, include it before ending nucleus phase

**Estimated Time:** 2-3 hours

---

#### Issue 3: Gemination (Shadda) Handling Incomplete
**Problem:** Shadda (ّ) creates isolated syllables or incorrect boundaries.

**Example:**
- Input: مُدَرِّس (mudarris)  
- Current: ['مُ', 'دَ', 'رِ', 'ّس'] → shadda creates isolated syllable
- Expected: ['مُ', 'دَرْ', 'رِس'] → shadda doubles the ر

**Research Needed:**
1. How does gemination affect syllable boundaries?
2. Should shadda create CVCC pattern or split into CVC + CVC?
3. Linguistic rule: does doubled consonant belong to previous or next syllable?

**Linguistic Background (needs verification):**
- Gemination: CaCːiC → Ca-CːiC (doubled consonant splits)
- First C is coda of previous syllable
- Second C is onset of next syllable
- Example: مُدَرّس = مُ-دَرْ-رِس (mu-dar-ris)

**Proposed Solution:**
- When shadda encountered (line 85-90):
  - Mark previous consonant as coda (add virtual sukun?)
  - Start new syllable with same consonant
  - Virtual doubling: 'رِّ' → 'رْ' (coda) + 'رِ' (onset+nucleus)

**Estimated Time:** 2-3 hours

---

#### Issue 4: Diphthong Detection Not Working
**Problem:** Diphthongs (ay=َيْ, aw=َوْ) split into separate syllables.

**Example:**
- Input: بَيْت (bayt - house)
- Current: ['بَ', 'ي', 'ْت'] → splits into 3 syllables
- Expected: ['بَيْت'] → single CVVC syllable

**Research Needed:**
1. Diphthong pattern: short vowel + yaa/waw + sukun + consonant
2. How to detect this sequence during segmentation?
3. Should diphthongs be CVV or CVVC pattern?

**Current Code Issue:**
```python
# Lines 63-70: Diphthong detection added but not triggering
if i < len(word) and word[i] == self.sukun:
    current_syl.append(word[i])
    i += 1
    if i < len(word) and not self._is_vowel(word[i]):
        current_syl.append(word[i])
        i += 1
```

**Problem:** This code assumes we're already processing a long vowel, but we may not be.

**Proposed Solution:**
- After processing short vowel (line 51-54):
- Check for pattern: next = long_vowel_marker, next+1 = sukun, next+2 = consonant
- If pattern matches, consume all 3 characters as part of nucleus+coda
- Mark as diphthong (special case of CVVC)

**Estimated Time:** 1-2 hours

---

### 🔧 Implementation Roadmap

#### Step 1: Fix Sukun Handling (Priority: 🔴 HIGH)
**Time:** 2-3 hours
1. Research how sukun marks syllable boundaries in Arabic linguistics
2. Modify segment() to look backward when sukun encountered
3. Test on: مَدْرَسَة, بِنْت, الشَّمْس
4. Verify CVC pattern detection improves

#### Step 2: Fix Long Vowel Detection (Priority: 🔴 HIGH)
**Time:** 2-3 hours
1. Add lookahead check after short vowel processing
2. If next char is matching long vowel marker, include it
3. Rules: fatha+alif=aa, kasra+yaa=ii, damma+waw=uu
4. Test on: كِتَاب, نُور
5. Verify CVV and CVVC patterns work

#### Step 3: Fix Gemination Handling (Priority: 🟡 MEDIUM)
**Time:** 2-3 hours
1. Research gemination syllabification rules
2. Implement virtual consonant doubling
3. Split into coda + onset
4. Test on: مُدَرِّس, كُلّ
5. Verify CVCC pattern detection for gemination

#### Step 4: Fix Diphthong Detection (Priority: 🟢 LOW)
**Time:** 1-2 hours
1. Add pattern matching for fatha+yaa/waw+sukun+consonant
2. Consume entire sequence as one syllable
3. Test on: بَيْت, مَوْت
4. Verify CVVC pattern for diphthongs

#### Step 5: Integration Testing (Priority: 🔴 HIGH)
**Time:** 1-2 hours
1. Run on all 10 test examples
2. Aim for >50% pass rate (currently 20%)
3. Document remaining failures
4. Create comprehensive test suite

---

## Testing Strategy

### Current Test Results (2/10 passing = 20%)
```
✓ كَتَبَ (kataba) - CV, CV, CV - SIMPLE CV ONLY
✓ مَ (ma) - CV - SINGLE SYLLABLE
✗ مَدْرَسَة (madrasa) - CVC with sukun
✗ الشَّمْس (ash-shams) - Sun letters + shadda
✗ كِتَاب (kitaab) - Long vowels
✗ بَيْت (bayt) - Diphthongs
✗ مُدَرِّس (mudarris) - Gemination
✗ بِنْت (bint) - CVCC cluster
✗ كُلّ (kull) - Gemination word-final
✗ نُور (nuur) - Long vowels
```

### Target After Fixes (aim for 8/10 = 80%)
```
✓ Simple CV patterns (already working)
✓ CVC with sukun (after Step 1)
✓ Long vowels CVV/CVVC (after Step 2)
✓ Gemination CVCC (after Step 3)
✓ Diphthongs CVVC (after Step 4)
? Sun letter assimilation (may need separate task)
```

---

## Code Files Modified

### src/core/syllabifier.py
**Lines Changed:**
- Lines 8-20: ✅ Fixed vowel/diacritic classification (COMPLETE)
- Lines 22-27: ✅ Fixed load_resources() path (COMPLETE)
- Lines 29-117: ⚠️ Rewrote segment() method (PARTIAL)
- Lines 119-121: ✅ Added _is_vowel() helper (COMPLETE)
- Lines 123-200: ✅ Rewrote classify_pattern() (COMPLETE)

**Total Lines Modified:** ~180 lines
**Completion:** 40% functional

---

## Resources Needed

### Linguistic Research
1. **Arabic Syllable Structure Rules**
   - Onset-nucleus-coda constraints
   - Gemination syllabification
   - Diphthong treatment

2. **Diacritization Rules**
   - Sukun placement patterns
   - When long vowel markers are consonants vs. vowels

3. **Reference Implementations**
   - Check existing Arabic NLP libraries (e.g., CAMeL Tools, Farasa)
   - Academic papers on Arabic syllabification

### Testing Resources
1. Expand test dataset to 50+ examples
2. Get native speaker validation
3. Compare with known-good implementations

---

## Recommendations

### Option A: Complete Task 2.2 Now (4-6 hours)
**Pros:**
- Finishes critical foundation
- Unblocks Tasks 2.3-2.7 and all downstream work
- Achieves >80% accuracy target

**Cons:**
- Significant time investment
- Complex algorithmic work
- May discover more edge cases

### Option B: Pause and Continue Later
**Pros:**
- Save current progress
- Work on easier tasks (Task 1 follow-ups, testing, docs)
- Come back with fresh perspective

**Cons:**
- Task 2.0 remains blocked
- Tasks 3-7 cannot proceed
- May lose context

### Option C: Simplify Approach
**Pros:**
- Accept 60-70% accuracy for MVP
- Focus on common cases only
- Defer edge cases to Phase 2

**Cons:**
- May not meet PRD >95% accuracy requirement
- Reduces quality of demo
- Technical debt accumulates

---

## Recommendation: Option A

**Rationale:**
- Syllabification is foundation of entire system
- 40% complete means we're past the hardest part (architecture redesign)
- Remaining work is incremental fixes
- 4-6 hours is reasonable to achieve 80%+ accuracy
- Critical for Phase 1 success

---

## Next Steps

1. ✅ Document current status (this file)
2. ⏭️ User decision: continue Task 2.2 or pause?
3. If continue: Start with Step 1 (Fix Sukun Handling)
4. If pause: Mark task incomplete, proceed to other tasks

---

**Status Report Generated:** October 30, 2025  
**File:** `/docs/reports/TASK_2_2_STATUS.md`
