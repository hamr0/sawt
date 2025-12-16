# Continuation Summary: Diacritization Analysis & Action Plan

**Date**: 2025-12-16
**Last Updated**: 2025-12-16 16:45 (after Phase 3 rollback)
**Context**: Reset point after Phase 3 attempt - ready for targeted fix approach

---

## 🎯 COMPLETED WORK (Session 2025-12-16)

### ✅ Phase 1 & 2: MasterTTS Improvements COMPLETE

**What Was Done**:
1. **MSA Format Fixes (36 entries)**
   - Fixed slash-format IPA notation (`/m/` → `m`)
   - Cleaned linguistic notation from all MSA entries
   - Preserved original attribution (`"user": "amr"`)

2. **MSA Position Mappings (48 NEW entries)**
   - Added missing position-specific IPA mappings
   - Researched from linguistic sources (Watson 2002, Holes 2004, Handbook of IPA)
   - Covered: Hamza variants, high-frequency consonants, all positions
   - All new entries marked with `"user": "llm"`

3. **Extended to All Dialects**:
   - **Gulf**: 29 new position mappings (critical characters)
   - **Levantine**: 26 new position mappings (including missing ت and ع)
   - **Maghreb**: 25 new position mappings (including CRITICAL missing ي character)

**Total Changes**:
- 128 NEW entries added across all dialects
- 36 format fixes in MSA (slash removal)
- Backup created: `masterTTS.json.backup_20251216_154350`
- JSON validated and working

**File Modified**: `/home/hamr/PycharmProjects/ArabicTTS/data/dictionaries/masterTTS.json`

**Expected Impact**:
- MSA: 39.4% → 67-75% success rate (Phase 1 & 2 target)
- All dialects: Improved character coverage and position handling
- Full 95%+ target requires Phases 3-5 (syllabification, diacritization, optimization)

### ✅ Phase 1 & 2 Testing: SUCCESS (69.1% achieved)

**Test Results**: `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/PHASE1_2_RESULTS.md`

- **Baseline**: 39.4% (139/353 words)
- **After Phase 1 & 2**: **69.1%** (244/353 words)
- **Improvement**: +29.7 percentage points ✅
- **Target Met**: Yes! (67-75% goal achieved)

**Breakdown**:
- Success: 244/353 (69.1%)
- Warnings (UNKNOWN patterns): 95/353 (26.9%)
- Errors (diacritization): 14/353 (4.0%)

### ⚠️ Phase 3 Attempt: ROLLBACK (Syllabifier Replacement)

**Attempted**: Replace broken syllabifier in `main.py` with proper syllabifier from `syllabifier.py`

**Result**: ROLLED BACK
- Success rate went DOWN: 69.1% → 64.9% (regression!)
- Created 22 regressions (success → warning)
- UNKNOWN patterns increased: 95 → 124

**Root Cause Analysis**:
1. **Two Different Syllabifiers**:
   - `src/main.py` (simple): "Split at vowels" approach - works for 69.1%
   - `src/core/syllabifier.py` (linguistic): Proper Arabic syllable rules

2. **Why Replacement Failed**:
   - Different philosophies create incompatibilities
   - Proper syllabifier produces standalone V (vowel) patterns after gemination
   - Merging V back into CVV creates invalid CVVV patterns
   - Example: `الرئيسي` → `CC.CV.CVV.UNKNOWN(CVVV)` ← Wrong!

3. **Key Insight**:
   - The "simple" syllabifier isn't broken - it works for 69.1% of cases
   - The 26.9% UNKNOWN patterns are edge cases needing **targeted fixes**
   - Wholesale replacement is too disruptive

**Backup Created**: `src/main.py.backup_phase3_20251216_163052`

**Rollback Completed**: System restored to 69.1% baseline

---

## 📋 CURRENT STATUS: Phase 1 & 2 Complete, Phase 3 Needs New Approach

**Achievement**: 69.1% success rate (up from 39.4%)

**Remaining Issues**:
- 95 words (26.9%) with UNKNOWN syllable patterns
- 14 words (4.0%) with diacritization errors

**Next Immediate Step**: Test MSA improvements with 353-word corpus

**Testing Plan**:
1. Generate new CSV with updated masterTTS.json for MSA dialect
2. Compare against baseline: `/home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv`
3. Measure success rate improvement (expect 67-75% from baseline 39.4%)
4. Identify remaining gaps for Phases 3-5

**Test Corpus**: 353 words (same as baseline)

---

## 🚧 REMAINING PHASES TO REACH 95%+

### Phase 3 (NEW APPROACH): Targeted UNKNOWN Pattern Fixes
**Status**: READY TO START
**Purpose**: Fix 95 words (26.9%) with UNKNOWN syllable patterns
**New Approach**: Add targeted pattern recognition to existing syllabifier (NOT wholesale replacement)
**Impact**: +20-25 percentage points (69.1% → ~90-95%)
**File**: `/home/hamr/PycharmProjects/ArabicTTS/src/main.py` (ArabicSyllabifier class)

**Strategy**:
1. Analyze the 95 UNKNOWN patterns to find common types:
   - CVVV (21 words) - gemination + vowel cases
   - CVCCVV (19 words) - consonant clusters
   - CVVVV (12 words) - very long vowel sequences
   - Others (43 words) - various edge cases

2. Add targeted pattern rules to existing `classify_pattern` method
3. Improve `resyllabify` to handle gemination edge cases
4. Low risk: Changes are additive, don't affect working 69.1%

**Documentation**: See `PHASE3_ALTERNATIVE_PLAN.md`

### Phase 2-Alt: Implement Mishkal → CAMeL Fallback
**Status**: NOT STARTED
**Purpose**: Fix 14 words (4.0%) with diacritization errors
**Impact**: +3-4 percentage points
**File**: `/home/hamr/PycharmProjects/ArabicTTS/src/main.py` (lines 359-406)
**Priority**: LOW (only 14 words affected)

### Phase 4: Exception Dictionary for Brands/Proper Nouns
**Status**: NOT STARTED
**Purpose**: Handle edge cases (1-2% remaining failures)
**Impact**: +1-2 percentage points
**Implementation**: Create new exception dictionary JSON

### Phase 5: LLM Fallback (OPTIONAL)
**Status**: NOT STARTED
**Purpose**: Last resort for remaining failures
**Cost**: User pays (~$5-15/month)
**Implementation**: See `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/llm-fallback-strategy.md`

---

## 📊 ORIGINAL BASELINE (Before Our Work)

## Executive Summary

**Critical Discovery**: The problem is NOT diacritization - it's **IPA mapping for MSA dialect**.
- EG dialect: 69.1% success rate
- MSA dialect: 39.4% success rate
- **Gap: 29.7% is almost entirely IPA mapping failures, not diacritization failures**

## Test Results: Mishkal vs CAMeL

### Installation Complete
- CAMeL Tools installed: `pip install camel-tools`
- Data files downloaded: `camel_data -i defaults` (~1GB)
- Test script: `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/test_diacritization_comparison.py`

### Performance Results (on EG text)

| Tool | Success Rate | Notes |
|------|--------------|-------|
| Mishkal only | 97.1% (270/278) | Fast, free, MSA-based |
| CAMeL only | 96.8% (269/278) | Slower, free, better for proper nouns |
| **Mishkal → CAMeL** | **98.9% (275/278)** | Best combined approach |
| CAMeL → Mishkal | 98.9% (275/278) | Same result |

**Key Findings**:
- Both tools are complementary (catch different failures)
- CAMeL rescued 5 words that Mishkal missed
- Mishkal rescued 6 words that CAMeL missed
- Only 3 words fail with BOTH tools (1.1%)
- **Improvement: 1.8% gain** (97.1% → 98.9%)

**Remaining Failures** (3 words):
1. "الإسكندرية" (Alexandria) - proper noun
2. "ناتجاس" (Natgas) - foreign brand
3. One other

**Recommended Architecture**:
```
Input → Mishkal (fast, catches 97.1%)
         ↓ if fails
      CAMeL (slower, catches 5 more)
         ↓ if fails
      Character fallback (existing)
```

**Cost**: $0/month (both tools are free)

## Critical Finding: MSA vs EG Dialect Analysis

### Test Files Analyzed
- `/home/hamr/Downloads/tts_matrix_20251216_144123-EG.csv` (353 words)
- `/home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv` (353 words)
- **Same words, different dialects**

### Detailed Breakdown

#### Egyptian (EG) - 69.1% Success

| Failed_Layers | Status | Count | % | What It Means |
|---------------|--------|-------|---|---------------|
| - | success | 244 | 69.1% | Everything worked |
| syl | warning | 93 | 26.3% | Syllabification issues (UNKNOWN patterns) |
| diac,syl,ipa | error | 14 | 4.0% | **Diacritization failed** |
| diac,syl | error | 2 | 0.6% | Diacritization failed |

**Total Diacritization Failures: 4.5%** (14+2 = 16 words)

#### MSA - 39.4% Success

| Failed_Layers | Status | Count | % | What It Means |
|---------------|--------|-------|---|---------------|
| - | success | 139 | 39.4% | Everything worked |
| **ipa** | **warning** | **105** | **29.7%** | **Diac ✓, Syllable ✓, IPA ✗** |
| syl | warning | 51 | 14.4% | Syllabification issues |
| syl,ipa | error | 42 | 11.9% | Syllable + IPA issues |
| diac,syl,ipa | error | 16 | 4.5% | **Diacritization failed** |

**Total Diacritization Failures: 4.5%** (16 words)
**IPA-Only Failures: 29.7%** (105 words) ← **THE REAL PROBLEM**

### The Smoking Gun

**Example: `محمد` (Muhammad)**
- **EG Dialect**: SUCCESS ✓
  - Diacritized: `مُحَمَّدٌ`
  - Pattern: CV.CV.CVC
  - IPA: Works (found in masterTTS.json for EG)

- **MSA Dialect**: WARNING (ipa failure)
  - Diacritized: `مُحَمَّدٌ` ✓ (Mishkal worked)
  - Pattern: CV.CV.CVC ✓ (Syllabifier worked)
  - IPA: **FAILED** ✗ (masterTTS.json missing MSA mappings)

**Conclusion**: masterTTS.json is EG-focused, not MSA-complete!

### Why This Matters

The 29.7% gap between EG (69.1%) and MSA (39.4%) is **NOT** because:
- ❌ Mishkal fails more on MSA (both dialects have 4.5% diac failures)
- ❌ MSA words are harder to diacritize (diacritization success is identical)

The gap **IS** because:
- ✅ **masterTTS.json lacks proper MSA character→IPA mappings**
- ✅ When dialect=MSA, IPA mapper looks up MSA entries → finds nothing
- ✅ 105 words (29.7%) have perfect diacritization but fail at IPA lookup

## Recommended Action Plan

### Phase 0: Understand Current State ✅ DONE

**Files Created**:
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/README.md` - Quick reference
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/test_diacritization_comparison.py` - Test script
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/testing-mishkal-camel.md` - Testing plan
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/llm-fallback-strategy.md` - LLM strategy (future)
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/diacritization_comparison_final.csv` - Test results

**Key Insights**:
- Diacritization is 95.5% successful (only 4.5% failures)
- Mishkal → CAMeL improves it to 98.9%
- **But this only helps EG, not MSA's real problem**

### Phase 1: Investigate masterTTS.json MSA Coverage ⭐ URGENT

**Priority**: HIGHEST (fixes 29.7% of MSA failures)

**Tasks**:
1. **Locate masterTTS.json file**
   ```bash
   find /home/hamr/PycharmProjects/ArabicTTS -name "masterTTS.json"
   ```

2. **Analyze MSA vs EG coverage**
   - Count how many characters have MSA mappings
   - Count how many characters have EG mappings
   - Identify missing MSA entries
   - Compare pronunciation differences

3. **Test hypothesis**:
   - Take the 105 IPA-failed words from MSA CSV
   - Check if their characters exist in masterTTS.json for MSA
   - Identify which specific characters are missing

4. **Fix masterTTS.json**:
   - Add missing MSA character→IPA mappings
   - Ensure all common Arabic characters have MSA variants
   - Test: Re-run MSA processing → should jump from 39.4% to ~69%

**Expected Outcome**: MSA success rate improves from 39.4% to ~69% (matching EG)

**Script to create**:
```python
# analyze_mastertts_coverage.py
# Compare MSA vs EG character coverage in masterTTS.json
# Identify missing MSA mappings
```

### Phase 2: Implement Mishkal → CAMeL Fallback

**Priority**: MEDIUM (improves remaining 2.9% after Phase 1)

**Tasks**:
1. **Modify `/home/hamr/PycharmProjects/ArabicTTS/src/main.py`**
   - Current: Uses Mishkal only (lines 359-406)
   - Update: Add CAMeL fallback for Mishkal failures

2. **Implementation**:
   ```python
   # Pseudo-code
   def apply_diacritization(word, mishkal, camel):
       # Try Mishkal first (fast)
       result = mishkal.tashkeel(word)
       if has_diacritics(result):
           return result, "mishkal"

       # Fallback to CAMeL (slower, better for proper nouns)
       result = camel.disambiguate(word)
       if has_diacritics(result):
           return result, "camel"

       # Final fallback: return undiacritized
       return word, "none"
   ```

3. **Add configuration**:
   ```yaml
   # config/diacritization.yaml
   diacritization:
     use_camel_fallback: true  # Enable CAMeL for failed words
   ```

4. **Track which tool succeeded**:
   - Add "diac_source" field to output: "mishkal", "camel", or "none"
   - Include in CSV export for analysis

**Expected Outcome**: Both EG and MSA improve from 98.9% to 99%+ diacritization

### Phase 3: Fix UNKNOWN Syllable Patterns

**Priority**: MEDIUM (improves 26% of EG, 14% of MSA)

**Problem**: Syllabifier marks complex patterns as UNKNOWN
- Example: `الْبَدْرِيُّ` → Pattern: `CC.UNKNOWN(CVCCVVV)`
- Root cause: Syllabifier doesn't handle:
  - Gemination (shadda doubling consonants)
  - Complex clusters (CVCC, CVVC, etc.)
  - Proper Arabic syllable rules

**Tasks**:
1. **Review `/home/hamr/PycharmProjects/ArabicTTS/src/core/syllabifier.py`**
   - Understand current syllable detection logic
   - Identify why valid patterns marked as UNKNOWN

2. **Research Arabic syllable rules**:
   - Valid patterns: CV, CVC, CVV, CVVC, CVCC
   - How shadda affects syllabification
   - Dialectal variations

3. **Fix syllabifier**:
   - Update pattern recognition
   - Handle gemination properly
   - Support all valid Arabic syllable types

**Expected Outcome**: Reduce UNKNOWN patterns from 26% to <5%

### Phase 4: Exception Dictionary for Brands/Proper Nouns

**Priority**: LOW (only affects remaining 1-2%)

**Problem**: Foreign words and proper nouns fail both Mishkal and CAMeL
- "ناتجاس" (Natgas) - English brand
- "الإسكندرية" (Alexandria) - already handled by CAMeL?

**Tasks**:
1. **Create exception dictionary**:
   ```json
   {
     "version": "1.0",
     "entries": {
       "ناتجاس": {
         "diacritized": "نَاتْجَاس",
         "source": "manual",
         "ipa": "nætgæs",
         "notes": "English brand name"
       },
       "الإسكندرية": {
         "diacritized": "الإِسْكَنْدَرِيَّة",
         "source": "manual",
         "ipa": "ʔælʔɪskændæˈɾɪjjæ",
         "notes": "Alexandria (proper noun)"
       }
     }
   }
   ```

2. **Curate 50-100 common entities**:
   - Egyptian cities
   - Common brands
   - Company names
   - Foreign words used in Arabic media

3. **Add lookup before Mishkal**:
   ```python
   # Check exception dict first (instant)
   if word in exception_dict:
       return exception_dict[word]

   # Then try Mishkal → CAMeL
   return apply_diacritization(word)
   ```

**Expected Outcome**: Handles edge cases that no tool can diacritize

### Phase 5: LLM Fallback (OPTIONAL - Last Resort)

**Priority**: LOWEST (user opts in, bears cost)

**When to use**: Only if Phases 1-4 still leave >5% failures

**Implementation**: See `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/llm-fallback-strategy.md`

**Cost**: User pays for API calls (~$5-15/month)

**Flow**:
```
Exception Dict → Mishkal → CAMeL → LLM (optional) → Character fallback
```

## Success Metrics

| Phase | Target | Current | Expected After Fix |
|-------|--------|---------|-------------------|
| Phase 1 (MSA IPA fix) | MSA 69% | MSA 39.4% | **MSA 69%** ✅ |
| Phase 2 (Mishkal→CAMeL) | 99% diac | 95.5% diac | **99% diac** ✅ |
| Phase 3 (Syllable fix) | <5% UNKNOWN | 26% EG, 14% MSA | **<5% UNKNOWN** |
| Phase 4 (Exception dict) | 99.5%+ | 98.9% | **99.5%+** |

**Total Expected**: After all phases, both EG and MSA should achieve **95%+ overall success rate**

## Key Files & Locations

### Test Files
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/test_diacritization_comparison.py` - Comparison test script
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/diacritization_comparison_final.csv` - Test results
- `/home/hamr/Downloads/tts_matrix_20251216_144123-EG.csv` - EG analysis (69.1% success)
- `/home/hamr/Downloads/tts_matrix_20251216_144128-MSA.csv` - MSA analysis (39.4% success)

### Documentation
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/README.md` - Quick start guide
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/testing-mishkal-camel.md` - Testing methodology
- `/home/hamr/PycharmProjects/ArabicTTS/tasks/llm/llm-fallback-strategy.md` - LLM strategy (future)
- `/home/hamr/PycharmProjects/ArabicTTS/CLARIFICATIONS.md` - Overall project clarifications

### Source Code to Modify
- `/home/hamr/PycharmProjects/ArabicTTS/src/main.py` (lines 359-406) - Add CAMeL fallback
- `/home/hamr/PycharmProjects/ArabicTTS/src/core/syllabifier.py` - Fix UNKNOWN patterns
- `/home/hamr/PycharmProjects/ArabicTTS/src/core/ipa_mapper.py` - Uses masterTTS.json
- `masterTTS.json` - **NEEDS MSA MAPPINGS** (location TBD)

### Configuration
- `/home/hamr/PycharmProjects/ArabicTTS/config/` - Add diacritization config

## Next Steps (In Order)

1. **IMMEDIATE**: Locate and analyze masterTTS.json
   ```bash
   find /home/hamr/PycharmProjects/ArabicTTS -name "masterTTS.json"
   # Analyze MSA vs EG coverage
   # Identify missing MSA entries
   ```

2. **Create analysis script**: `analyze_mastertts_coverage.py`
   - Compare MSA vs EG character coverage
   - List missing MSA mappings
   - Suggest IPA values for missing characters

3. **Fix masterTTS.json**: Add missing MSA entries
   - Test on MSA CSV → should improve from 39.4% to ~69%

4. **Implement Mishkal → CAMeL fallback** in src/main.py
   - Test on both EG and MSA → should reach 99% diacritization

5. **Fix syllabifier UNKNOWN patterns** (if time permits)

## Commands to Run

```bash
# Re-test anytime with new CSV exports
cd /home/hamr/PycharmProjects/ArabicTTS/tasks/llm
python3 test_diacritization_comparison.py /path/to/your/csv/file.csv

# Find masterTTS.json
find /home/hamr/PycharmProjects/ArabicTTS -name "masterTTS.json"

# Check CAMeL installation
python3 -c "from camel_tools.disambig.mle import MLEDisambiguator; print('CAMeL OK')"

# Check Mishkal
python3 -c "from mishkal.tashkeel import TashkeelClass; print('Mishkal OK')"
```

## Important Context

### What Works
- ✅ Diacritization: 95.5% success (Mishkal), 98.9% with CAMeL fallback
- ✅ Both Mishkal and CAMeL are free, no LLM needed
- ✅ Character-level fallback already implemented as safety net

### What's Broken
- ❌ **MSA IPA mappings in masterTTS.json** (29.7% of MSA words fail here)
- ❌ Syllabifier marks 26% of patterns as UNKNOWN
- ❌ Proper nouns/brands need exception handling (1-2%)

### Architecture Decision
**Do NOT add empty exception dictionary as Tier 1**
- Empty dict is useless as first check
- Only create exception dict AFTER we have data to populate it
- Priority: Fix root causes (IPA mappings, syllabification) first

### Cost Analysis
- Current solution: **$0/month** (Mishkal + CAMeL both free)
- LLM fallback: **$5-15/month** (optional, user pays)
- Recommendation: Exhaust free tools first (Phases 1-4)

## Questions to Answer Next Session

1. Where is masterTTS.json located?
2. What does MSA vs EG coverage look like in masterTTS.json?
3. Which specific characters are missing MSA mappings?
4. Should we test CAMeL on "الإسكندرية" specifically?
5. Is the syllabifier fix in scope for this iteration?

---

**Remember**: The biggest win (29.7% improvement) comes from fixing masterTTS.json MSA coverage, not from improving diacritization!
