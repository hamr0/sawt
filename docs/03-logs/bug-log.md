# Bug Log

Track bugs, their root causes, and fixes.

---

## Format

```
## BUG-XXX: Brief Description

**Date Found:** YYYY-MM-DD
**Date Fixed:** YYYY-MM-DD
**Severity:** Critical | High | Medium | Low
**Status:** Open | Fixed | Won't Fix
**Symptoms:** What was observed
**Root Cause:** Why it happened
**Fix:** What was changed
**Files:** Affected files
```

---

## Bugs

### BUG-001: Empty X-SAMPA for Some Inputs

**Date Found:** 2025-11-03
**Date Fixed:** 2025-11-03
**Severity:** Medium
**Status:** Fixed
**Symptoms:** Polly integration failing silently for certain words
**Root Cause:** X-SAMPA conversion returning empty string for edge cases
**Fix:** Fallback to plain Arabic text when X-SAMPA is empty
**Files:** src/integrations/polly.py

### BUG-002: Polly Neural Engine Error

**Date Found:** 2025-11-03
**Date Fixed:** 2025-11-03
**Severity:** High
**Status:** Fixed
**Symptoms:** Polly returning "Engine not supported" error
**Root Cause:** Zeina (Arabic voice) only supports standard engine, not neural
**Fix:** Changed default engine from "neural" to "standard" for Zeina
**Files:** src/integrations/polly.py

### BUG-003: High UNKNOWN Syllable Patterns

**Date Found:** 2025-12-14
**Date Fixed:** 2025-12-15
**Severity:** Medium
**Status:** Fixed
**Symptoms:** ~30% of syllables marked as UNKNOWN pattern
**Root Cause:** Syllabifier ending at long vowel markers instead of short vowels
**Fix:** Updated segment_syllables() to end at SHORT VOWELS only, added resyllabify() post-processor
**Files:** src/core/syllabifier.py

---

## Template for New Bugs

```
### BUG-XXX: Title

**Date Found:**
**Date Fixed:**
**Severity:**
**Status:**
**Symptoms:**
**Root Cause:**
**Fix:**
**Files:**
```
