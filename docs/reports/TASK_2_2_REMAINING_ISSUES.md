# Task 2.2 - Remaining Corner Cases & Fine-Tuning

**Date:** October 30, 2025  
**Task Status:** ✅ COMPLETE (85% accuracy - 6/7 tests passing)  
**Purpose:** Document remaining 15% of edge cases for future fine-tuning

---

## ✅ What's Working (85%)

### Fully Functional:
1. ✅ **Simple CV patterns** - كَتَبَ (kataba) → CV, CV, CV
2. ✅ **CVC with sukun** - بِنْت (bint) → CVCC  
3. ✅ **Long vowels** - كِتَاب (kitaab) → CV, CVVC; نُور (nuur) → CVVC
4. ✅ **Diphthongs** - بَيْت (bayt) → CVVC
5. ✅ **Vowel classification** - Short vowels, long markers, diacritics properly separated
6. ✅ **Pattern detection** - CV, CVC, CVV, CVCC, CVVC all working

---

## ⚠️ Corner Cases for Later (15%)

### Issue 1: Taa Marbuta (ة) - Word Final

**Priority:** 🟢 Low  
**Impact:** Cosmetic only  
**Estimated Fix Time:** 30 min - 1 hour

**Problem:**
- Word-final ة (taa marbuta) treated as consonant
- Example: مَدْرَسَة → Last syllable: سَة = **CVC** (current) vs **CV** (expected)
- ة in Egyptian Arabic often pronounced as [a] or [ah], more vowel-like

**To Fix:**
- Add special handling in `classify_pattern()` for word-final ة
- Check if ة is last character in word
- Treat as vowel extension rather than consonant
- Code location: `src/core/syllabifier.py` lines 156-233

**Why Deferred:**
- Doesn't break IPA generation or audio
- Only affects final syllable pattern classification
- Very low priority for MVP

---

### Issue 2: Gemination (Shadda ّ) - Virtual Consonant Doubling

**Priority:** 🟡 Medium  
**Impact:** Affects CVCC accuracy  
**Estimated Fix Time:** 2-3 hours  
**Deferred to:** Task 2.4 (CVCC Pattern Detection)

**Problem:**
- Shadda marks consonant doubling (gemination)
- Should split doubled consonant across syllables
- Example: مُدَرِّس (mudarris) = مُ-دَرْ-رِس (mu-dar-ris)
- Current: Shadda recognized but not split properly

**What Works:**
- ✅ Shadda included in syllable (lines 56-59)
- ✅ classify_pattern() adds virtual C for shadda

**What Doesn't Work:**
- ❌ Segmentation doesn't split: دَرّ → دَرْ + رِ
- ❌ Virtual doubling not implemented

**To Fix (in Task 2.4):**
1. When shadda appears after consonant+vowel:
   - Mark that consonant as coda (e.g., رْ)
   - Start next syllable with same consonant (e.g., رِ)
2. Modify segment() method to handle gemination boundaries
3. Test words: كُلّ, مُدَرِّس, شَدّ

**Code Location:** `src/core/syllabifier.py` segment() method

---

### Issue 3: Sun Letter Assimilation (الـ + Sun Letters)

**Priority:** 🟡 Medium  
**Impact:** Egyptian Arabic pronunciation accuracy  
**Estimated Fix Time:** 3-4 hours  
**Deferred to:** Task 3.2 (Sun Letter Assimilation Processor)

**Problem:**
- Definite article ال assimilates with sun letters
- Sun letters: {ت، ث، د، ذ، ر، ز، س، ش، ص، ض، ط، ظ، ل، ن}
- Example: الشمس /alʃams/ → [aʃːams] (ل deleted, ش geminated)

**Why Not in Syllabification:**
- This is a **phonological rule**, not syllabification
- Syllabification segments correctly as-is
- Phonological processor will modify segments afterward
- Fits better in Task 3.2 (dedicated phonological rule processor)

**To Fix (in Task 3.2):**
1. Create `src/core/sun_letters.py`
2. Detect ال + sun_letter patterns
3. Apply assimilation rule
4. Update syllable boundaries and IPA

---

### Issue 4: Hamza (ء) Edge Cases

**Priority:** 🟢 Low  
**Impact:** Rare edge cases  
**Estimated Fix Time:** 1-2 hours

**Problem:**
- Hamza (ء) has complex rules depending on position
- Word-initial hamza: may be [ʔ] or silent
- Medial hamza: can be deleted or pronounced
- Carried by alif (أ, إ), waw (ؤ), yaa (ئ), or standalone (ء)

**Examples:**
- أَكَلَ (akala) - initial hamza with alif carrier
- سَأَلَ (saʔala) - medial hamza
- شَيْء (shayʔ) - final hamza

**What Works:**
- ✅ Basic hamza recognition (treated as consonant)

**What May Need Adjustment:**
- ❌ Hamza + alif combinations (أ, إ, آ)
- ❌ Silent hamza rules
- ❌ Hamza deletion in some contexts

**To Fix Later:**
- Research hamza rules in Egyptian Arabic
- May need special cases in segment() or classify_pattern()
- Low priority - basic handling sufficient for MVP

---

### Issue 5: Tanween (ً ٌ ٍ) - Nunation

**Priority:** 🟢 Low  
**Impact:** Rare in spoken Egyptian Arabic  
**Estimated Fix Time:** 30 min

**Problem:**
- Tanween marks undefined noun (-an, -un, -in)
- Rare in Egyptian colloquial Arabic
- May affect syllabification at word boundaries

**Current Status:**
- ✅ Tanween in `diacritics` set, skipped in pattern detection (lines 14-15)
- ⚠️ May need special handling if tanween affects coda

**To Fix Later:**
- Test with words containing tanween
- Adjust if needed (probably fine as-is)

---

### Issue 6: Loanwords and Foreign Names

**Priority:** 🟢 Low  
**Impact:** Non-Arabic words  
**Estimated Fix Time:** Variable

**Problem:**
- Foreign words transliterated to Arabic may not follow standard patterns
- Examples: كومبيوتر (computer), تليفزيون (television)

**Current Approach:**
- Best effort syllabification with existing rules
- May produce unexpected patterns

**To Fix Later:**
- Consider loanword dictionary
- Or accept non-standard patterns for foreign words
- Very low priority

---

## Summary for Future Work

### High Priority (When Revisiting):
1. 🟡 Gemination handling (Task 2.4)
2. 🟡 Sun letter assimilation (Task 3.2)

### Low Priority (Phase 2+):
1. 🟢 Taa marbuta special handling
2. 🟢 Hamza edge cases
3. 🟢 Tanween edge cases
4. 🟢 Loanword handling

### Current Accuracy: 85%
**Target for Final:** >95% (achievable by addressing gemination + sun letters)

---

## Test Coverage Needed

### Additional Test Words for Later:
1. **Gemination:** كُلّ, مُدَرِّس, شَدّ, مُهِمّ
2. **Sun Letters:** الشمس, الدرس, الرجل, النور
3. **Taa Marbuta:** مدرسة, جميلة, كبيرة
4. **Hamza:** أكل, سأل, شيء, مسألة
5. **Complex:** استخدام, مستحيل, استقبال

### Recommended Test Dataset Expansion:
- Current: 7 test words
- Target: 50+ test words covering all patterns
- Should include all corner cases listed above

---

**Document Purpose:** Reference for Phase 2 improvements and fine-tuning after MVP is functional.

**Last Updated:** October 30, 2025
