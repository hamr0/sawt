# Festival TTS & XTTS Voice Cloning - Complete Analysis

**Date:** December 18, 2025

---

## 🎯 Your Questions

1. ✅ Can we test Festival both ways: plain text + mishkal + X-SAMPA?
2. ❓ Does Festival offer multiple characters/voices?
3. ❓ Can Festival be used with XTTS to add custom voices?

---

## 📋 Quick Answers

| Question | Answer | Details |
|----------|--------|---------|
| Festival plain/mishkal/X-SAMPA test? | ✅ YES | Test script ready, needs installation |
| Festival multiple voices? | ⚠️ LIMITED | 1 Arabic voice (Nawar), but can be pitched/styled |
| Festival + XTTS integration? | ✅ YES | Possible and interesting - see below |

---

## 1. Festival Testing (Plain + Mishkal + X-SAMPA)

### Test Script Status: ✅ READY

**File:** `tools/festival_tts/test_festival_comparison.py`

**Three Test Modes:**

#### Mode 1: Plain Text (Festival Native)
```scheme
; Festival processes Arabic text directly
(set! text "صباح الخير")
(utt.synth (eval (list 'Utterance 'Text text)))
```

**Advantages:**
- Simplest approach
- Festival's built-in Arabic processing
- No preprocessing needed

**Expected Quality:** ⭐⭐ (robotic, limited Arabic understanding)

#### Mode 2: Mishkal Diacritized Text
```scheme
; Our pipeline adds diacritics first
text = "صَبَاحُ الخَيْر"  # From mishkal
(utt.synth (eval (list 'Utterance 'Text text)))
```

**Advantages:**
- Improved pronunciation accuracy
- Proper vowel lengths
- Better syllable boundaries
- **This is what Festival documentation recommends**

**Expected Quality:** ⭐⭐⭐ (noticeable improvement)

#### Mode 3: X-SAMPA Phoneme Input
```scheme
; Full phonetic control via our pipeline
phonemes = "s a b a: H a l x a j r"
(SayPhones '(s a b a: H a l x a j r))
```

**Advantages:**
- Complete phonetic control
- Bypasses Festival's text-to-phoneme rules
- Uses our entire 6-month pipeline
- Your phonological processors applied

**Expected Quality:** ⭐⭐⭐⭐ (best pronunciation accuracy)

### Installation Required

```bash
# Install Festival
sudo apt-get update
sudo apt-get install festival

# Install Arabic voice (Nawar)
cd /tmp
git clone https://github.com/linuxscout/festival-tts-arabic-voices.git
cd festival-tts-arabic-voices
sudo ./install.sh

# Test installation
echo "مرحبا" | festival --tts --language arabic
```

### Run All Three Tests

```bash
python3 tools/festival_tts/test_festival_comparison.py
```

**Expected Output:** 9 WAV files (3 modes × 3 test sentences)

---

## 2. Festival Multiple Voices/Characters

### Short Answer: LIMITED ⚠️

Festival has **1 Arabic voice** (Nawar), but you can manipulate it for multi-character effects.

### Available Arabic Voice

**Nawar Voice:**
- Type: HMM-based synthesis
- Gender: Male
- Dialect: MSA (Modern Standard Arabic)
- Quality: ⭐⭐⭐ (moderate)
- Creator: Taha Zerrouki (same as mishkal)

### Multi-Character Workarounds

#### Option 1: Pitch Shifting (Built-in Festival)

```scheme
; Higher pitch for female characters
(set! duffint_params '((start 100) (end 100)))  ; Normal (male)
(set! duffint_params '((start 150) (end 150)))  ; Higher (female)
(set! duffint_params '((start 80) (end 80)))    ; Lower (older male)
```

**Effect:** Same voice, different pitches
**Quality:** ⭐⭐ (obvious pitch-shifting, robotic)
**Use case:** Better than monotone, worse than different voices

#### Option 2: Speed/Rate Variation

```scheme
; Fast-talking character
(Parameter.set 'Duration_Stretch 0.8)  ; 20% faster

; Slow, deliberate character
(Parameter.set 'Duration_Stretch 1.3)  ; 30% slower
```

**Effect:** Same voice, different speaking rates
**Quality:** ⭐⭐⭐ (more natural than pitch-shifting)
**Use case:** Differentiate characters by tempo

#### Option 3: Prosody Manipulation

```scheme
; Excited character (higher pitch + faster)
(set! duffint_params '((start 120) (end 140)))
(Parameter.set 'Duration_Stretch 0.9)

; Sad character (lower pitch + slower)
(set! duffint_params '((start 90) (end 80)))
(Parameter.set 'Duration_Stretch 1.2)
```

**Effect:** Combined pitch + tempo variation
**Quality:** ⭐⭐⭐ (best Festival-native option)
**Use case:** 3-4 character differentiation

### Festival Multi-Voice Limitations

**Compared to Azure:**

| Feature | Azure | Festival |
|---------|-------|----------|
| Arabic voices | 14+ | 1 |
| Male voices | 7+ | 1 |
| Female voices | 7+ | 0 (pitch-shifted only) |
| Dialects | 7+ | MSA only |
| Voice quality | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Character differentiation | Natural | Artificial |

**Verdict:** Festival multi-voice is possible but LIMITED compared to Azure.

---

## 3. Festival + XTTS Integration 🔥

### This is the MOST INTERESTING Option!

**XTTS (Coqui XTTS)** is a voice cloning system that can create custom voices from short audio samples.

### What is XTTS?

**Coqui XTTS v2:**
- Open-source voice cloning
- Requires only 6-10 seconds of voice sample
- Supports 17+ languages (including Arabic)
- Can clone ANY voice (you, professional narrator, etc.)
- FREE and runs locally

**Official:** https://github.com/coqui-ai/TTS

### How Festival + XTTS Integration Works

#### Architecture

```
Your Text Pipeline (mishkal + phonological processing)
    ↓
Festival Festival generates phoneme timing
    ↓
XTTS takes phonemes + voice sample
    ↓
Custom voice output (your voice or professional narrator)
```

#### Why This is Powerful

**Problem with Festival:** Limited to 1 Arabic voice (Nawar)
**Problem with Azure:** Costs $11/book, voices not customizable

**Solution: Festival + XTTS:**
1. Festival handles Arabic phoneme generation (FREE)
2. XTTS clones custom voices (FREE)
3. You get professional-quality custom voices at zero cost

### XTTS Multi-Voice Capabilities

**Record 3 people (10 seconds each):**
- Narrator voice (warm female)
- Male character voice
- Female character voice

**Result:** 3 custom voices for audiobooks, all free, unlimited use

### Integration Approaches

#### Approach 1: Replace Festival Voice (Simple)

```python
from TTS.api import TTS

# Initialize XTTS
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Your pipeline generates text
processed_text = pipeline.process_text("صباح الخير", dialect='EG')

# XTTS synthesizes with custom voice
tts.tts_to_file(
    text="صباح الخير",
    speaker_wav="narrator_voice_sample.wav",  # Your 10-sec sample
    language="ar",
    file_path="output.wav"
)
```

**Pros:**
- ✅ Bypasses Festival entirely
- ✅ Custom voice from any sample
- ✅ Good quality (⭐⭐⭐⭐)
- ✅ Free

**Cons:**
- ⚠️ Slower than Festival (GPU recommended)
- ⚠️ Doesn't use your phonological pipeline directly

#### Approach 2: Pipeline → Festival Phonemes → XTTS (Advanced)

```python
# Your pipeline generates IPA/X-SAMPA
ipa = pipeline.process_text(text)['ipa']

# Festival converts to Festival phonemes
festival_phonemes = ipa_to_festival_phones(ipa)

# XTTS synthesizes from phonemes with custom voice
tts.tts_with_phonemes(
    phonemes=festival_phonemes,
    speaker_wav="voice_sample.wav",
    file_path="output.wav"
)
```

**Pros:**
- ✅ Uses your entire 6-month pipeline
- ✅ Full phonetic control
- ✅ Custom voice
- ✅ Free

**Cons:**
- ⚠️ More complex integration
- ⚠️ Requires phoneme format conversion

#### Approach 3: XTTS Multi-Voice (Your Original Question!)

```python
# Define characters with voice samples
characters = {
    'narrator': 'samples/narrator.wav',
    'أحمد': 'samples/male_character.wav',
    'فاطمة': 'samples/female_character.wav',
}

# Your multi-voice system assigns characters
segments = assigner.split_into_segments(story)

# Generate audio for each segment with matching voice
for segment in segments:
    voice_sample = characters[segment.character.name]

    tts.tts_to_file(
        text=segment.text,
        speaker_wav=voice_sample,
        language="ar",
        file_path=f"segment_{i}.wav"
    )

# Concatenate all segments
combine_audio_files(segments, "full_audiobook.mp3")
```

**This gives you:**
- ✅ Multiple distinct voices (as many as you have samples)
- ✅ Custom voices (record yourself, hire voice actors once)
- ✅ Free unlimited use
- ✅ Full control over voice quality

---

## 🎯 Strategic Recommendations

### Option 1: Festival (Plain/Mishkal/X-SAMPA) ⭐⭐⭐
**Best for:** Testing if free TTS is "good enough"

**Pros:**
- Free
- Your pipeline valuable (especially mishkal + X-SAMPA)
- Better than eSpeak

**Cons:**
- Only 1 Arabic voice
- Multi-character via pitch-shifting (limited)
- Quality: ⭐⭐⭐ (acceptable, not great)

**Test Time:** 30 minutes
**Cost:** $0

### Option 2: Azure Multi-Voice (Current) ⭐⭐⭐⭐⭐
**Best for:** Professional audiobooks, need it now

**Pros:**
- ✅ Best quality
- ✅ 14+ voices (real multi-character)
- ✅ Works now (tested, proven)
- ✅ No GPU/setup required

**Cons:**
- ❌ Costs $11/book
- ❌ Your pipeline not useful (plain text is best)

**Setup Time:** 0 (already working)
**Cost:** $11/book

### Option 3: XTTS Voice Cloning 🔥⭐⭐⭐⭐
**Best for:** Long-term, custom voices, high volume

**Pros:**
- ✅ FREE unlimited use
- ✅ Custom voices (yours or professional)
- ✅ Multiple characters (record different people)
- ✅ Good quality (⭐⭐⭐⭐)
- ✅ Your pipeline potentially valuable

**Cons:**
- ⚠️ Setup time (2-4 hours)
- ⚠️ GPU recommended (CPU is slow)
- ⚠️ Need voice samples (10 sec each)

**Setup Time:** 2-4 hours
**Cost:** $0/book

### Option 4: Hybrid (My Recommendation) 🏆

**Phase 1 (Now):** Test Festival
- 30 minutes testing
- Determines if free TTS acceptable
- Tests mishkal integration

**Phase 2 (Next Week):** Test XTTS
- Set up XTTS locally
- Record 3 voice samples (narrator + 2 characters)
- Generate test audiobook chapter

**Phase 3 (Next Month):** Choose Production Stack

**If XTTS quality ≥ ⭐⭐⭐⭐:**
- Use XTTS for production (FREE + custom voices)
- Keep Azure for premium tier

**If XTTS < ⭐⭐⭐⭐:**
- Use Azure multi-voice (proven quality)
- Keep Festival/XTTS for validation

---

## 📊 Comparison Matrix

| Feature | Festival | Azure | XTTS |
|---------|----------|-------|------|
| Cost | FREE | $11/book | FREE |
| Arabic voices | 1 | 14+ | Unlimited custom |
| Voice quality | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Multi-character | Pitch-shift only | Natural 14+ voices | Natural unlimited |
| Pipeline value | ✅ High | ❌ Low | ✅ High |
| Setup time | 30 min | 0 (done) | 2-4 hours |
| Hardware needs | CPU | Cloud | GPU recommended |
| Speed | Fast | Fast | Medium |
| Customization | Low | None | High |

---

## 🛠️ Immediate Next Steps

### 1. Install Festival (5 minutes)

```bash
sudo apt-get update
sudo apt-get install festival

# Install Arabic voice
git clone https://github.com/linuxscout/festival-tts-arabic-voices.git
cd festival-tts-arabic-voices
sudo ./install.sh
```

### 2. Test Festival (30 minutes)

```bash
python3 tools/festival_tts/test_festival_comparison.py
```

Listen to 9 files:
- 3 plain text
- 3 mishkal diacritized
- 3 X-SAMPA phoneme input

**Rate quality:** Which mode sounds best?

### 3. If Festival Quality ≥ ⭐⭐⭐

**Proceed to XTTS testing:**

```bash
# Install XTTS
pip install TTS

# Test with simple example
tts --text "صباح الخير" --model_name "tts_models/multilingual/multi-dataset/xtts_v2" --speaker_wav sample.wav --language_idx ar --out_path output.wav
```

### 4. If Festival Quality < ⭐⭐⭐

**Stick with Azure multi-voice** (what you have working now)

---

## 💡 My Honest Recommendation

**Test in this order:**

1. **Festival (30 min)** → Determines if free TTS acceptable
2. **XTTS (2-4 hours)** → If Festival not good enough, but you want free solution
3. **Decide:**
   - XTTS good? → Use XTTS with custom voices (FREE, unlimited)
   - XTTS not good enough? → Azure multi-voice (proven, $11/book)

**Most likely outcome:**
- Festival: ⭐⭐⭐ (acceptable but not great)
- XTTS: ⭐⭐⭐⭐ (very good with custom voices)
- Azure: ⭐⭐⭐⭐⭐ (best quality)

**Best long-term solution:** XTTS with custom voices
- Record professional narrator once ($50-100)
- Unlimited audiobooks with that voice (FREE)
- Full multi-character support
- Your pipeline valuable

---

## 🎤 XTTS Voice Cloning Demo

Want to test XTTS? Here's a minimal example:

```python
from TTS.api import TTS

# Initialize (downloads model first time)
tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")

# Record 10 seconds of someone speaking Arabic
# Save as 'narrator.wav'

# Generate audiobook with that voice
tts.tts_to_file(
    text="كان يا ما كان في قديم الزمان",
    speaker_wav="narrator.wav",
    language="ar",
    file_path="output.wav"
)
```

**Result:** Your text in narrator's voice, unlimited use, free.

---

**Bottom Line:**
- ✅ Festival testing: Ready now (30 min)
- ✅ Festival multi-voice: Limited (pitch-shifting only)
- ✅ XTTS integration: Possible and POWERFUL (2-4 hours setup)
- 🏆 **XTTS is the "hidden gem" solution** - free, custom voices, unlimited

**My bet:** XTTS will be your production solution.
