# Festival vs XTTS: Workflows & GPU Requirements

**Date:** December 18, 2025

---

## 🎯 Your Questions Answered

### Question 1: Does Festival accept XTTS voices?

**NO ❌** - They're separate systems that cannot be mixed directly.

**Why:**
- Festival has its own synthesis engine (HMM-based)
- XTTS is a neural network TTS (completely different architecture)
- They use different voice formats

**Think of it like:** Asking if Microsoft Word can use Adobe Photoshop brushes - they're different programs for different purposes.

---

### Question 2: Generate with Festival then regenerate with XTTS?

**YES ✅** - But you wouldn't do both. You choose one workflow:

**Workflow A: Festival Only**
```
Text → Festival → Audio
```
- No GPU needed
- Fast
- Free
- Limited to 1 voice (with pitch variations)

**Workflow B: XTTS Only**
```
Text → XTTS → Audio
```
- GPU recommended (but not required)
- Slower on CPU
- Free
- Unlimited custom voices

**You pick ONE, not both!**

---

## 🔄 Complete Workflow Comparison

### Option 1: Festival Pipeline (What Your Test Does)

```
Arabic Text
    ↓
[Choose preprocessing]
├─→ Plain text (no processing)
├─→ Mishkal diacritization (recommended)
└─→ X-SAMPA from pipeline (full processing)
    ↓
Festival Synthesis (with voice variations)
├─→ Normal male (baseline)
├─→ Female voice (higher pitch)
├─→ Older male (lower pitch, slower)
└─→ Fast-talking (faster tempo)
    ↓
WAV Audio Output
```

**Hardware:** CPU only (no GPU needed)
**Speed:** Fast (~real-time)
**Cost:** FREE
**Quality:** ⭐⭐⭐
**Voices:** 1 voice, 4 variations

---

### Option 2: XTTS Pipeline (Custom Voices)

```
Arabic Text
    ↓
[Optional: Your pipeline for diacritization]
    ↓
XTTS Synthesis (with custom voice samples)
├─→ Narrator voice (your 10-sec sample)
├─→ Male character (different 10-sec sample)
└─→ Female character (different 10-sec sample)
    ↓
WAV Audio Output
```

**Hardware:** GPU recommended (CPU works but slower)
**Speed:**
- GPU: ~2-5 seconds per minute of audio
- CPU: ~10-30 seconds per minute of audio
**Cost:** FREE
**Quality:** ⭐⭐⭐⭐
**Voices:** Unlimited custom voices

---

## 🖥️ GPU Requirements Explained

### Why XTTS Needs GPU (Festival Doesn't)

**Festival:**
- Traditional synthesis (HMM statistical models)
- CPU computations only
- Fast on any computer
- **No GPU needed**

**XTTS:**
- Neural network TTS (deep learning)
- Matrix multiplications (GPU accelerates this)
- Slow on CPU (but works)
- **GPU recommended but not required**

### XTTS Performance Comparison

| Hardware | Speed | Example |
|----------|-------|---------|
| **CPU only** | 10-30 sec / min audio | 5 min audiobook = 50-150 sec processing |
| **GPU (NVIDIA)** | 2-5 sec / min audio | 5 min audiobook = 10-25 sec processing |

**For audiobooks:**
- 1-hour audiobook on CPU: ~10-30 minutes processing
- 1-hour audiobook on GPU: ~2-5 minutes processing

**Verdict:** CPU is usable for low-volume production, GPU for high-volume.

---

## 📊 Which Workflow Should You Use?

### Scenario 1: Testing if Free TTS is Good Enough

**Use: Festival Pipeline**

```bash
# Quick test (30 minutes)
sudo apt-get install festival
python3 tools/festival_tts/test_festival_variations.py
```

**Output:** 24 audio files
- 2 test sentences
- 3 modes (plain, mishkal, X-SAMPA)
- 4 voice variations each

**Evaluate:**
- Is mishkal better than plain text? (probably yes)
- Can you distinguish characters with voice variations?
- Is quality ≥ ⭐⭐⭐ for audiobooks?

---

### Scenario 2: Want Custom Voices for Branding

**Use: XTTS Pipeline**

```bash
# Setup (2-4 hours first time)
pip install TTS

# Record voice samples (10 seconds each)
# - narrator.wav
# - male_character.wav
# - female_character.wav

python3 tools/xtts/test_xtts_integration.py
```

**Output:** Custom-voiced audiobooks

**Advantage:**
- Your voice or professional narrator
- Natural multi-character (not pitch-shifted)
- Unlimited use after setup

---

### Scenario 3: Need Best Quality NOW

**Use: Azure Multi-Voice (already working)**

```python
# Already set up and tested!
from tools.azure_tts.character_voice_assignment import CharacterVoiceAssigner

assigner = CharacterVoiceAssigner(dialect='EG')
segments, ssml = assigner.analyze_and_assign(story)
azure.generate_audio_from_ssml(ssml, "audiobook.mp3")
```

**Advantage:**
- Best quality (⭐⭐⭐⭐⭐)
- 14+ natural voices
- Works immediately
- No GPU needed (cloud service)

**Cost:** $11/book

---

## 🎤 Multi-Character Voice Comparison

### Festival Multi-Character (Pitch Variations)

**How it works:**
```python
# Same voice, different pitches
narrator = Festival(pitch=100)  # Normal male
female = Festival(pitch=150)    # Higher pitch
older = Festival(pitch=80)      # Lower pitch
```

**Result:**
- ⭐⭐⭐ Obviously the same voice
- Distinguishable but artificial
- Better than monotone

**Example:** Like one person doing different character voices - you can tell it's the same person.

---

### XTTS Multi-Character (Different Voice Samples)

**How it works:**
```python
# Different actual voices
narrator = XTTS(voice_sample="john.wav")   # John's voice
female = XTTS(voice_sample="sarah.wav")    # Sarah's voice
older = XTTS(voice_sample="grandpa.wav")   # Grandpa's voice
```

**Result:**
- ⭐⭐⭐⭐ Natural different voices
- Each character distinct
- Professional quality

**Example:** Like having 3 different voice actors - actually different people.

---

### Azure Multi-Character (14+ Neural Voices)

**How it works:**
```python
# 14+ pre-trained professional voices
narrator = Azure("ar-EG-SalmaNeural")    # Professional female
male = Azure("ar-EG-ShakirNeural")       # Professional male
female2 = Azure("ar-SA-ZariyahNeural")   # Different accent
```

**Result:**
- ⭐⭐⭐⭐⭐ Professional voice actors
- Natural different voices
- Different dialects available

**Example:** Like hiring 14 professional voice actors.

---

## 💡 Recommended Strategy

### Phase 1: Festival Testing (NOW - 30 minutes)

**Purpose:** Determine if free TTS is "good enough"

```bash
sudo apt-get install festival
python3 tools/festival_tts/test_festival_variations.py
```

**Listen to:**
- Plain vs Mishkal vs X-SAMPA (which preprocessing is best?)
- Normal vs Female vs Older vs Fast (can you distinguish characters?)

**Decision:**
- Festival ≥ ⭐⭐⭐? → Could work for production
- Festival < ⭐⭐⭐? → Move to Phase 2

---

### Phase 2: XTTS Testing (THIS WEEK - 2-4 hours)

**If Festival not good enough:**

```bash
pip install TTS

# Record yourself or friends (10 seconds each)
# Test custom voices
python3 tools/xtts/test_xtts_integration.py
```

**Compare:**
- Festival (pitch-shifted) vs XTTS (custom voices)
- CPU speed vs quality trade-off

**Decision:**
- XTTS ≥ ⭐⭐⭐⭐ and speed OK? → Use for production
- XTTS too slow or quality not great? → Use Azure

---

## 🎯 Quick Decision Matrix

| Need | Solution | GPU? | Cost |
|------|----------|------|------|
| **Test free TTS now** | Festival variations | ❌ No | $0 |
| **Custom branded voices** | XTTS | ✅ Recommended | $0 |
| **Best quality now** | Azure (working) | ❌ No | $11/book |
| **Multi-character (natural)** | XTTS or Azure | Depends | $0 or $11 |
| **Multi-character (quick)** | Festival variations | ❌ No | $0 |

---

## 🔧 Implementation Files

### Festival Test (Ready to Run)

**File:** `tools/festival_tts/test_festival_variations.py`

**What it tests:**
- 3 preprocessing modes (plain, mishkal, X-SAMPA)
- 4 voice variations (normal, female, older, fast)
- 2 test sentences
- **Total: 24 audio files**

**Install & run:**
```bash
sudo apt-get install festival
python3 tools/festival_tts/test_festival_variations.py
```

---

### XTTS Test (Ready to Run)

**File:** `tools/xtts/test_xtts_integration.py`

**What it tests:**
- Single voice cloning
- Multi-voice character assignment
- Pipeline integration

**Install & run:**
```bash
pip install TTS
# Record voice samples (10 sec each)
python3 tools/xtts/test_xtts_integration.py
```

---

## ❓ FAQ

### Q: Can I use Festival AND XTTS together?

**A:** Not really. They're alternative approaches. Pick one:
- Festival = Fast, CPU-only, pitch variations
- XTTS = Better quality, GPU recommended, custom voices

### Q: Does XTTS require GPU?

**A:** No, but recommended:
- CPU works, just slower (10-30 sec per min audio)
- GPU is 5-10x faster (2-5 sec per min audio)
- For occasional use, CPU is fine

### Q: Which is better: Festival or XTTS?

**A:** Depends on your needs:

| Factor | Festival | XTTS |
|--------|----------|------|
| Quality | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Speed | Fast | Medium |
| Setup | Easy | Medium |
| Voices | 1 (varied) | Unlimited |
| GPU | Not needed | Recommended |

**General answer:** XTTS is better quality, Festival is easier/faster.

### Q: Should I test Festival first or XTTS?

**A:** Festival first (30 min), then XTTS if needed (2-4 hours):

```
Festival test (30 min)
    ↓
Festival ≥ ⭐⭐⭐?
├─→ YES: Use Festival (done!)
└─→ NO: Test XTTS (2-4 hours)
        ↓
    XTTS ≥ ⭐⭐⭐⭐?
    ├─→ YES: Use XTTS
    └─→ NO: Use Azure
```

---

## 🚀 Next Steps

### 1. Install Festival (5 minutes)
```bash
sudo apt-get update
sudo apt-get install festival
```

### 2. Run Festival Variations Test (30 minutes)
```bash
python3 tools/festival_tts/test_festival_variations.py
```

This generates **24 audio files** to compare:
- 3 preprocessing methods
- 4 voice variations
- 2 test sentences

### 3. Listen & Evaluate

Compare:
- **Modes:** Plain vs Mishkal vs X-SAMPA
- **Voices:** Normal vs Female vs Older vs Fast

Rate:
- Can you distinguish characters?
- Is mishkal better than plain?
- Is quality acceptable for audiobooks?

### 4. Decide Next Step

- Festival good enough? → Done!
- Festival not enough? → Test XTTS next

---

**Bottom Line:**

- ❌ Festival and XTTS are NOT combined - choose one
- ✅ Festival = quick test, no GPU (pitch variations)
- ✅ XTTS = better quality, GPU recommended (custom voices)
- ✅ Test Festival first (30 min) to see if free TTS works
- ✅ If not, XTTS is your "premium free" option

**Both test scripts are ready to run!**
