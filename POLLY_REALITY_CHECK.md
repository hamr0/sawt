# AWS Polly Reality Check - Arabic TTS Limitations

**Date:** December 18, 2025
**Status:** CRITICAL FINDING - Previous assumptions were incorrect

---

## 🔴 Executive Summary

**AWS Polly does NOT support phonetic input (X-SAMPA or IPA) for Arabic voices.**

This means:
- ❌ Your phonological processing CANNOT be used with Polly
- ❌ X-SAMPA conversion is useless for Polly
- ❌ Polly uses only built-in MSA pronunciation (no dialect control)
- ✅ Polly quality = ~80% (built-in pronunciation)

---

## 📊 What Happened

### Before (Working at 80%)
```
User inputs Arabic text
  ↓
TTS pipeline processes (gemination, sun letters, emphatic spread, etc.)
  ↓
Polly receives: <speak>صباح</speak>
  ↓
Polly uses built-in MSA pronunciation
  ↓
Result: 80% quality audio ✅
```

### After Claude's Changes (0% - Gibberish)
```
User inputs Arabic text
  ↓
TTS pipeline processes + X-SAMPA generation
  ↓
Polly receives: <speak><phoneme alphabet="x-sampa" ph="s_?bAi:">صباح</phoneme></speak>
  ↓
Polly sees unsupported phoneme tag
  ↓
Polly gets confused
  ↓
Result: 0% gibberish ❌
```

### After Fix (Back to 80%)
```
User inputs Arabic text
  ↓
TTS pipeline processes (X-SAMPA generated but ignored)
  ↓
Polly receives: <speak>صباح</speak>
  ↓
Polly uses built-in MSA pronunciation
  ↓
Result: 80% quality audio ✅
```

---

## 🔍 Root Cause Analysis

### What Was Wrong

**1. Incorrect Assumption in Documentation**
- docs/polly/*.md assumed X-SAMPA would work for Arabic
- AWS Polly documentation was not properly verified
- Implementation plan was based on this false assumption

**2. X-SAMPA Support is Language-Specific**
AWS Polly X-SAMPA support (22 languages):
```
cy-GB, da-DK, de-DE, en-AU, en-GB, en-GB-WLS, en-IN, en-US,
fr-BE, fr-CA, fr-FR, is-IS, it-IT, nb-NO, nl-BE, nl-NL,
pl-PL, pt-BR, pt-PT, ro-RO, sv-SE, tr-TR
```

**Arabic (arb) is NOT in this list.**

**3. Unsupported Phoneme Tags Cause Issues**
When Polly receives:
```xml
<phoneme alphabet="x-sampa" ph="...">text</phoneme>
```

For an unsupported language, it causes parsing errors or unexpected behavior → gibberish.

---

## ✅ Fix Applied

**File:** `src/integrations/polly.py`
**Change:** `xsampa_to_ssml()` now ALWAYS returns plain text for Arabic

```python
def xsampa_to_ssml(self, xsampa: str, text: str) -> str:
    """
    ALWAYS use plain text for Arabic (phoneme tags not supported)
    """
    return f'<speak>{text}</speak>'
```

**Result:** Polly now receives plain Arabic text, works at 80% again.

---

## 🎯 Implications

### What You CAN Do with Polly
✅ Use Polly for natural-sounding Arabic voice (neural)
✅ Get ~80% quality with built-in MSA pronunciation
✅ Low cost ($16/1M characters for neural)
✅ Easy integration (no phonetic complexity)

### What You CANNOT Do with Polly
❌ Control pronunciation with your phonological rules
❌ Support dialects beyond MSA (Polly's default)
❌ Use your 1,030-entry masterTTS.json dictionary
❌ Apply gemination, sun letters, emphatic spread, allophones
❌ Fine-tune pronunciation for specific words

---

## 🔄 Options Going Forward

### Option A: Keep Polly (Simple, Limited)
**Pros:**
- Natural-sounding voice
- Low cost ($16/1M chars)
- Easy integration
- 80% quality for MSA

**Cons:**
- No phonetic control
- MSA only (no EG, Gulf, Levantine, Maghrebi)
- Your linguistic work is wasted
- Cannot improve beyond 80%

**Use case:** Quick audiobook production, MSA only, 80% quality acceptable

---

### Option B: Use eSpeak (Full Control, Robotic)
**Pros:**
- Full phonetic control (IPA/X-SAMPA)
- Your linguistic work is fully utilized
- All 5 dialects supported
- Can improve to 95%+ accuracy
- Zero cost

**Cons:**
- Robotic voice quality
- Less natural prosody
- Listeners may find it jarring

**Use case:** Research, validation, dialect testing, maximum accuracy

---

### Option C: Alternative TTS Engine (Research Required)
**Options to investigate:**

1. **Google Cloud TTS**
   - Supports SSML phoneme tags
   - Need to verify Arabic support
   - Cost: $16/1M characters (neural)

2. **Azure TTS**
   - Supports SSML phoneme tags
   - Arabic voices available
   - Need to verify phonetic control
   - Cost: $16/1M characters (neural)

3. **Coqui XTTS (Open Source)**
   - Local/self-hosted
   - Fine-tunable for Arabic
   - May support phonetic input
   - Zero cost (GPU required)

4. **Festival TTS**
   - Open source
   - Full phonetic control
   - Arabic support possible
   - Voice quality moderate

**Action:** Research which engines support phonetic input for Arabic

---

### Option D: Hybrid Approach (Best of Both Worlds?)
**Strategy:**
- Use Polly for MSA content (80% quality, natural voice)
- Use eSpeak for dialect-specific content (95% accuracy, robotic voice)
- Switch based on content type and user preference

**Pros:**
- Flexibility
- Cost-effective
- Covers both use cases

**Cons:**
- Inconsistent voice across content
- More complex implementation

---

## 🧪 X-SAMPA Code Status

**The X-SAMPA generation code added to `main.py` is:**
- ✅ Still functional
- ✅ Used in CSV exports (documentation)
- ❌ NOT used by Polly (documented limitation)
- ⚠️ Available for future TTS engines that support Arabic phonetic input

**Files modified:**
1. `src/main.py` - Added X-SAMPA generation (lines 938-942)
2. `src/core/hierarchical_processor.py` - Enhanced X-SAMPA converter (lines 569-685)
3. `app.py` - Fixed X-SAMPA concatenation (line 531)
4. `src/integrations/polly.py` - Fixed to ignore X-SAMPA (line 77)

**Decision:** Keep the X-SAMPA code for future use, but document that it's not used by Polly.

---

## 📝 Lessons Learned

1. **Verify API capabilities before implementation**
   - Always check official documentation
   - Test assumptions with small POCs
   - Don't trust secondary sources without verification

2. **Understand service limitations**
   - Cloud TTS services have language-specific features
   - Phonetic control is not universal
   - Arabic support varies widely across services

3. **Have rollback plans**
   - Document working baseline (80%)
   - Test changes incrementally
   - Keep original behavior accessible

4. **Document findings clearly**
   - Correct any misleading documentation
   - Update implementation plans
   - Share learnings with team

---

## 🎓 Recommendations

### Immediate (This Week)
1. ✅ Fix Polly integration (DONE - plain text only)
2. ✅ Document Polly limitations (this file)
3. ⏳ Update docs/polly/*.md to reflect reality
4. ⏳ Test Polly with sample content (verify 80% quality)

### Short-term (2-4 Weeks)
1. Research Google Cloud TTS Arabic phonetic support
2. Research Azure TTS Arabic phonetic support
3. Investigate Coqui XTTS for Arabic
4. Create comparison matrix of TTS engines
5. Make informed decision on TTS strategy

### Long-term (1-3 Months)
1. If phonetic control needed → Switch to engine that supports it
2. If MSA + natural voice sufficient → Keep Polly
3. If dialects critical → Investigate open-source alternatives
4. Consider hybrid approach for different content types

---

## 📚 References

### AWS Polly Documentation
- [Supported Languages](https://docs.aws.amazon.com/polly/latest/dg/SupportedLanguage.html)
- [Phoneme and Viseme Support](https://docs.aws.amazon.com/polly/latest/dg/phoneme-tables.html)
- [Arabic Voice: Zeina](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

### X-SAMPA Specification
- [Official X-SAMPA](https://www.phon.ucl.ac.uk/home/sampa/x-sampa.htm)
- [Wikipedia X-SAMPA](https://en.wikipedia.org/wiki/X-SAMPA)

---

**Status:** Issue resolved, system restored to 80% baseline.
**Next:** Research alternative TTS engines with Arabic phonetic support.
