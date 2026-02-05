# Festival TTS vs eSpeak: Comprehensive Analysis

**Date:** December 18, 2025
**Question:** Can Festival TTS replace eSpeak for audiobook production?

---

## 🎤 Festival TTS Overview

### What is Festival?
- **Open-source TTS system** from University of Edinburgh
- **Arabic voice available**: Nawar (HMM-trained)
- **Repository**: `github.com/linuxscout/festival-tts-arabic-voices`

### Key Capabilities

| Feature | Festival | eSpeak NG |
|---------|----------|-----------|
| **Voice Quality** | ⭐⭐⭐ (Moderate) | ⭐⭐ (Robotic) |
| **Phoneme Input** | ✅ Supported | ✅ Supported |
| **Arabic Support** | ✅ Nawar voice (HMM) | ✅ Built-in |
| **Cost** | Free | Free |
| **Technology** | HMM synthesis | Formant synthesis |
| **Speed** | Moderate | Fast |
| **Customization** | High | Moderate |

---

## 📋 Your 4 Questions Answered

### 1. Does Festival take X-SAMPA or plain text?

**Answer: BOTH** ✅

Festival supports multiple input modes:

**A) Plain Text (Simplest)**
```bash
echo "صباح الخير" | festival --tts --language arabic
```

**B) Phoneme Input (Full Control)**
```scheme
; Festival Scheme syntax for phoneme input
(SayPhones '(s a b aa H a l x a y r))
```

**C) X-SAMPA via Conversion**
Your pipeline → IPA → Festival phonemes

**Key Difference from Azure:**
- Festival: Phoneme input IMPROVES quality (designed for it)
- Azure: Phoneme input BREAKS quality (not designed for it)

---

### 2. Can Festival replace eSpeak?

**Answer: YES, and you should try it** ✅

**Festival is BETTER than eSpeak:**

| Aspect | Festival Nawar | eSpeak NG | Winner |
|--------|---------------|-----------|--------|
| Voice Quality | ⭐⭐⭐ | ⭐⭐ | Festival |
| Naturalness | Moderate | Low | Festival |
| Prosody | Better | Robotic | Festival |
| Arabic Support | Dedicated voice | Generic | Festival |
| Your Pipeline | Works | Works | Tie |

**Why Festival is Better:**
1. **HMM-based synthesis** (more natural than formant synthesis)
2. **Trained on Arabic audio** (better prosody)
3. **Dedicated Arabic voice** (not generic phoneme engine)
4. **Better rhythm and intonation**

**Why You Should Test Festival:**
- Free (same as eSpeak)
- Better quality (noticeable improvement)
- Full X-SAMPA/phoneme control (your pipeline works)
- May be "good enough" for audiobooks (needs testing)

---

### 3. How to use different voices and dialects with Azure plain text?

**Answer: SSML with `<voice>` tags** ✅

Azure supports **14 Arabic neural voices** across dialects:

#### Available Azure Arabic Voices

**Egyptian Arabic (ar-EG):**
- `ar-EG-SalmaNeural` (Female)
- `ar-EG-ShakirNeural` (Male)

**Saudi/MSA (ar-SA):**
- `ar-SA-ZariyahNeural` (Female)
- `ar-SA-HamedNeural` (Male)

**Gulf/UAE (ar-AE):**
- `ar-AE-FatimaNeural` (Female)
- `ar-AE-HamdanNeural` (Male)

**Levantine/Syria (ar-SY):**
- `ar-SY-AmanyNeural` (Female)
- `ar-SY-LaithNeural` (Male)

**Plus:** Jordan, Lebanon, Morocco, Tunisia, Yemen, Oman, Qatar, Bahrain

#### Multi-Voice Example (Character Dialogue)

```python
from tools.azure_tts.azure_integration import AzureTTS

azure = AzureTTS()

# Define dialogue with different voices
dialogue = [
    {
        'text': 'قال الراوي: كان يا ما كان',
        'voice': 'ar-EG-SalmaNeural',  # Narrator (Female, Egyptian)
    },
    {
        'text': 'قال أحمد: مرحبا يا صديقي',
        'voice': 'ar-EG-ShakirNeural',  # Character 1 (Male, Egyptian)
    },
    {
        'text': 'قالت فاطمة: أهلا وسهلا',
        'voice': 'ar-SA-ZariyahNeural',  # Character 2 (Female, Saudi)
    }
]

# Generate multi-voice audio
azure.generate_audio_with_voices(dialogue, 'dialogue.mp3')
```

#### SSML Multi-Voice Example

```xml
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="ar-EG">
  <!-- Narrator -->
  <voice name="ar-EG-SalmaNeural">
    قال الراوي: في يوم من الأيام
  </voice>

  <!-- Pause -->
  <break time="500ms"/>

  <!-- Hero (Egyptian accent) -->
  <voice name="ar-EG-ShakirNeural">
    قال البطل: أنا ذاهب للمغامرة
  </voice>

  <!-- Pause -->
  <break time="500ms"/>

  <!-- Villain (Gulf accent) -->
  <voice name="ar-AE-HamdanNeural">
    <prosody rate="slow" pitch="-10%">
      قال الشرير: لن تفلح أبداً
    </prosody>
  </voice>
</speak>
```

**Additional SSML Features:**
- `<break time="500ms"/>` - Add pauses
- `<prosody rate="slow">` - Control speed
- `<prosody pitch="+10%">` - Adjust pitch
- `<emphasis level="strong">` - Emphasize words
- `<say-as interpret-as="date">` - Format numbers/dates

**You DON'T need X-SAMPA for voice switching!**

---

### 4. Can Festival be the default for audiobooks (since it's free)?

**Answer: Maybe - Needs Quality Testing** ⚠️

**Quality Comparison:**

| TTS | Voice Quality | For Audiobooks? | Cost |
|-----|---------------|-----------------|------|
| Azure Plain Text | ⭐⭐⭐⭐⭐ | ✅ Best | $11/book |
| Festival Nawar | ⭐⭐⭐ | ⚠️ Maybe | Free |
| eSpeak NG | ⭐⭐ | ❌ Too robotic | Free |

**The Critical Question:**
**Is Festival "good enough" for 10-hour audiobooks?**

You need to test:
1. Generate 30-minute sample with Festival
2. Listen critically for fatigue
3. Compare to Azure sample
4. Decide if quality gap justifies cost

**Scenarios:**

**Scenario A: Festival is Good Enough (⭐⭐⭐)**
```
USE: Festival as default
- Free audiobook generation
- Your pipeline fully utilized
- Acceptable voice quality
- Better than eSpeak

RESULT: Best of both worlds!
```

**Scenario B: Festival Better Than eSpeak But Not Good Enough**
```
DECISION MATRIX:
- Budget tight? → Festival
- Quality matters? → Azure plain text
- Want both? → Hybrid approach

HYBRID: Festival for draft/preview, Azure for final
```

**Scenario C: Festival Only Marginally Better Than eSpeak**
```
RESULT: Not worth switching
- Keep eSpeak for validation
- Use Azure for production
```

---

## 🎯 Recommended Testing Plan

### Phase 1: Install & Test Festival (2-3 hours)

```bash
# Install Festival
sudo apt-get install festival

# Install Arabic voice (Nawar)
# Follow: github.com/linuxscout/festival-tts-arabic-voices

# Test basic functionality
echo "صباح الخير" | festival --tts --language arabic
```

### Phase 2: Integrate with Your Pipeline (3-4 hours)

Create `src/integrations/festival.py`:

```python
class FestivalTTS:
    """
    Festival TTS wrapper with phoneme input support
    """

    def generate_audio(self, ipa: str, output_path: str) -> Tuple[bool, str]:
        """
        Generate audio from IPA using Festival

        Args:
            ipa: IPA phonetic string
            output_path: Output WAV file

        Returns:
            (success, message)
        """
        # Convert IPA to Festival phoneme format
        festival_phones = self.ipa_to_festival_phones(ipa)

        # Generate Festival script
        script = self.create_festival_script(festival_phones, output_path)

        # Execute Festival
        result = subprocess.run(
            ['festival', '--batch', script],
            capture_output=True
        )

        return result.returncode == 0, "Audio generated"
```

### Phase 3: Quality Comparison (2-3 hours)

Generate same content with all 3 engines:

```python
# Test text (30-minute sample)
long_text = """[Your audiobook chapter]"""

# Generate with all 3
festival.generate_audio(ipa, "test_festival.wav")
espeak.generate_audio(ipa, "test_espeak.wav")
azure.generate_audio(text, "", "test_azure.mp3", use_phonetic=False)

# Listen and rate (1-5 scale):
# - Voice quality
# - Naturalness
# - Listening fatigue
# - Would you listen for 10 hours?
```

### Phase 4: Decision (1 hour)

| Rating | Decision |
|--------|----------|
| Festival ≥ 4.0 | **Use Festival as default** ✅ |
| Festival 3.0-3.9 | **Hybrid: Festival draft + Azure final** |
| Festival < 3.0 | **Keep Azure, use Festival for validation** |

---

## 💡 My Recommendation

**Test Festival immediately. Here's why:**

### The Festival Opportunity

**If Festival voice quality is acceptable (⭐⭐⭐):**
- ✅ Your 6-month pipeline IS valuable for production
- ✅ Free audiobook generation (no $11/book cost)
- ✅ Full phonetic control retained
- ✅ Better than eSpeak
- ✅ All 5 dialects supported via your pipeline

**This is the scenario where your work pays off!**

### The Hybrid Approach (Best of Both Worlds)

Even if Festival isn't perfect:

```
Development/Draft:
  → Festival (free, fast iteration)

Final Production:
  → Azure plain text (best quality)

Validation:
  → Your pipeline + eSpeak (reference)
```

### Why This Makes Sense

1. **Festival may surprise you** - HMM synthesis is significantly better than formant
2. **Testing cost: 3-4 hours** - Worth it to potentially save $11/book
3. **You already have the pipeline** - Festival can use it
4. **Worst case: Keep current plan** - Festival becomes validation tool

---

## 🔧 Implementation Priorities

### Priority 1: Test Festival Voice Quality (TODAY)

```bash
# Quick test
sudo apt-get install festival
echo "صباح الخير يا صديقي العزيز" | festival --tts --language arabic

# Listen: Is this ⭐⭐⭐ or better?
```

### Priority 2: If Festival ≥ ⭐⭐⭐ → Integrate with Pipeline (THIS WEEK)

```python
# Create Festival integration
# Test with your pipeline
# Compare quality to Azure
```

### Priority 3: If Festival < ⭐⭐⭐ → Stick with Azure Plain Text

```python
# Use Azure plain text for production
# Keep Festival as backup
# Your pipeline for validation
```

---

## 📊 Cost-Benefit Analysis

### Festival vs Azure Economics

**100k-word audiobook production:**

| Scenario | Festival | Azure | Savings |
|----------|----------|-------|---------|
| 10 books/year | $0 | $110 | $110/year |
| 50 books/year | $0 | $550 | $550/year |
| 100 books/year | $0 | $1,100 | $1,100/year |

**Break-even calculation:**
- Testing Festival: 10 hours investment
- Azure cost savings: $11/book
- Break-even: ~1 book if Festival works

**Even if Festival is only "acceptable" (⭐⭐⭐):**
- Free is compelling for high-volume production
- Users may tolerate slightly lower quality for free/cheap content
- Can offer two tiers: Festival (free) and Azure (premium)

---

## 🎬 Action Plan

### This Week:

1. **Install Festival + Nawar voice** (1-2 hours)
2. **Generate 5-minute test sample** (1 hour)
3. **Listen and rate quality** (30 minutes)
4. **Make go/no-go decision** (30 minutes)

### If GO:
- Integrate Festival with pipeline (3-4 hours)
- Generate 30-minute chapter sample (1 hour)
- Final quality validation (1 hour)
- Set as default or hybrid approach

### If NO-GO:
- Keep Festival as validation tool
- Proceed with Azure plain text for production
- Document findings

---

## ❓ Bottom Line

**You asked: "Can Festival be our default for audiobooks?"**

**Answer: MAYBE - and it's worth 3-4 hours to find out!**

Festival could be the sweet spot:
- Better quality than eSpeak (⭐⭐⭐ vs ⭐⭐)
- Uses your pipeline (6 months not wasted)
- Free (no $11/book cost)
- Good enough for audiobooks (needs testing)

**If Festival works → Your pipeline has production value**
**If Festival doesn't → Azure plain text is the answer**

**Test Festival first before finalizing decision.**
