# Amazon Polly TTS Integration - Usage Guide

This guide explains how to use the Amazon Polly integration with your Arabic TTS system.

## Table of Contents

1. [Quick Start](#quick-start)
2. [PollyTTS Class Reference](#pollytts-class-reference)
3. [Voice Options](#voice-options)
4. [Engine Options](#engine-options)
5. [Integration with ArabicTTS Pipeline](#integration-with-arabictts-pipeline)
6. [Running the Test Script](#running-the-test-script)
7. [Code Examples](#code-examples)
8. [Error Handling](#error-handling)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
1. **AWS credentials configured** - See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)
2. **boto3 installed:**
   ```bash
   pip install boto3>=1.28.0
   ```

### Basic Usage

```python
from src.integrations.polly import PollyTTS

# Initialize Polly client
polly = PollyTTS()

# Generate audio
success, message = polly.generate_audio(
    text="مرحبا",
    xsampa="mar.Ha.ban",
    output_path="output.mp3",
    voice_id="Zeina",
    engine="neural"
)

if success:
    print(f"✅ {message}")
else:
    print(f"❌ {message}")
```

---

## PollyTTS Class Reference

### Initialization

```python
from src.integrations.polly import PollyTTS

# Basic initialization (auto-detects credentials)
polly = PollyTTS()

# Specify region explicitly
polly = PollyTTS(region_name="us-west-2")
```

**Default Region:** `us-east-1` (lowest latency for most users)

**Initialization Errors:**
- `ImportError`: boto3 not installed
- `RuntimeError`: AWS credentials not configured

### Methods

#### `generate_audio(text, xsampa, output_path, voice_id='Zeina', engine='neural')`

Generates audio from Arabic text using Polly with X-SAMPA phonetic control.

**Parameters:**
- `text` (str): Original Arabic text
- `xsampa` (str): X-SAMPA phonetic representation (from your IPA engine)
- `output_path` (str): Where to save the MP3 file
- `voice_id` (str, optional): Polly voice name (default: 'Zeina')
- `engine` (str, optional): 'neural' or 'standard' (default: 'neural')

**Returns:**
- Tuple `(success: bool, message: str)`
  - `success=True, message="Audio generated successfully: {path}"`
  - `success=False, message="Error description"`

**Example:**
```python
success, msg = polly.generate_audio(
    text="صباح الخير",
    xsampa="sa.baH.al.xajr",
    output_path="demo_output/morning.mp3"
)
```

#### `xsampa_to_ssml(xsampa, original_text)`

Converts X-SAMPA phonetic notation to Polly SSML format.

**Parameters:**
- `xsampa` (str): X-SAMPA phonetic string
- `original_text` (str): Original Arabic text (for fallback)

**Returns:**
- `str`: SSML document with phoneme tag

**Example:**
```python
ssml = polly.xsampa_to_ssml("mar.Ha.ban", "مرحبا")
print(ssml)
# Output:
# <speak>
#     <phoneme alphabet="x-sampa" ph="mar.Ha.ban">مرحبا</phoneme>
# </speak>
```

**Note:** This method is called internally by `generate_audio()`. You typically don't need to call it directly.

---

## Voice Options

Amazon Polly supports multiple Arabic voices:

### Modern Standard Arabic (MSA)

| Voice | Gender | Engine Support | Best For |
|-------|--------|---------------|----------|
| **Zeina** | Female | Neural, Standard | General use, audiobooks |
| **Hala** | Female | Neural only | Gulf-accented content |

**Recommendation:** Use **Zeina** with **neural** engine for best quality.

### Voice Selection Example

```python
# MSA female (default)
polly.generate_audio(text, xsampa, output_path, voice_id="Zeina")

# Gulf Arabic accent
polly.generate_audio(text, xsampa, output_path, voice_id="Hala")
```

**Note:** Your IPA/X-SAMPA phonetics control pronunciation - voice selection affects prosody and accent, not phoneme accuracy.

---

## Engine Options

Polly offers two synthesis engines:

### Neural Engine (Recommended)

**Advantages:**
- Significantly more natural-sounding
- Better prosody and intonation
- Ideal for audiobooks and long-form content

**Cost:** $16.00 per 1 million characters (after free tier)

**Free Tier:** 5 million characters/month for 12 months

**Usage:**
```python
polly.generate_audio(..., engine="neural")
```

### Standard Engine

**Advantages:**
- Lower cost ($4.00 per 1 million characters)
- Wider voice selection (for some languages)

**Disadvantages:**
- Robotic-sounding compared to neural
- Less natural prosody

**Usage:**
```python
polly.generate_audio(..., engine="standard")
```

### Comparison

| Feature | Neural | Standard |
|---------|--------|----------|
| Quality | Excellent | Good |
| Naturalness | Very high | Moderate |
| Cost (per 1M chars) | $16 | $4 |
| Free tier | 5M/month | 5M/month |
| Arabic voices | Zeina, Hala | Zeina |

**Recommendation:** Use **neural** for production. Standard engine is only beneficial for high-volume, cost-sensitive applications where quality is less critical.

---

## Integration with ArabicTTS Pipeline

The Polly integration preserves your existing IPA-based pipeline:

```
Arabic Text → Buckwalter → IPA → X-SAMPA → Polly SSML → Audio
```

### Complete Pipeline Example

```python
from src.main import ArabicTTS
from src.integrations.polly import PollyTTS

# Step 1: Process text with your IPA engine
tts = ArabicTTS(dialect='MSA')
result = tts.process_text("اللغة العربية لغة جميلة")

# Step 2: Extract X-SAMPA
xsampa = result.get('x_sampa', result.get('ipa', ''))

# Step 3: Generate audio with Polly
polly = PollyTTS()
success, message = polly.generate_audio(
    text="اللغة العربية لغة جميلة",
    xsampa=xsampa,
    output_path="output/arabic_beauty.mp3",
    voice_id="Zeina",
    engine="neural"
)

if success:
    print(f"✅ Audio generated: output/arabic_beauty.mp3")
else:
    print(f"❌ Error: {message}")
```

### Dialect Support

Your IPA engine handles dialect-specific phonetics. Polly just renders the phonemes:

```python
# Egyptian Arabic
tts_eg = ArabicTTS(dialect='EG')
result = tts_eg.process_text("إزيك")
xsampa_eg = result.get('x_sampa', '')

polly.generate_audio(
    text="إزيك",
    xsampa=xsampa_eg,
    output_path="egyptian.mp3",
    voice_id="Zeina"  # MSA voice, but EG phonetics from your engine
)

# Gulf Arabic
tts_gulf = ArabicTTS(dialect='Gulf')
result = tts_gulf.process_text("شلونك")
xsampa_gulf = result.get('x_sampa', '')

polly.generate_audio(
    text="شلونك",
    xsampa=xsampa_gulf,
    output_path="gulf.mp3",
    voice_id="Hala"  # Gulf-accented voice
)
```

---

## Running the Test Script

The POC test script compares Polly and eSpeak quality.

### Execute Test

```bash
cd /path/to/ArabicTTS
python scripts/test_polly_integration.py
```

### Expected Output

**With AWS credentials configured:**
```
✅ Amazon Polly client initialized
✅ eSpeak TTS initialized

[Processes 5 test sentences...]

📊 Test Results:
   Total test cases: 5
   Polly:  5 passed, 0 failed
   eSpeak: 5 passed, 0 failed

📁 Generated Files:
   Polly audio:  5 files, 45.2 KB total
   eSpeak audio: 5 files, 2.1 KB total
   Location: demo_output/polly_test/

💰 Cost Analysis:
   Characters processed: 350
   Cost for this POC: $0.000006 (within free tier)

✅ SUCCESS - Polly Integration Working!
```

**Without AWS credentials:**
```
✅ Amazon Polly client initialized
✅ eSpeak TTS initialized

[Processes 5 test sentences...]

  ❌ Polly failed: AWS credentials not configured

📊 Test Results:
   Polly:  0 passed, 5 failed
   eSpeak: 5 passed, 0 failed

🔧 Troubleshooting:
   1. Install boto3: pip install boto3>=1.28.0
   2. Configure AWS credentials: aws configure
   3. See: docs/polly/AWS_SETUP_GUIDE.md
```

### Interpreting Results

1. **Play audio files:**
   ```bash
   # Polly output
   mpv demo_output/polly_test/test_polly_001_zeina_neural.mp3
   
   # eSpeak comparison
   aplay demo_output/polly_test/test_polly_001_espeak.wav
   ```

2. **Compare quality:**
   - Polly should sound significantly more natural
   - Check pronunciation accuracy for all phonemes
   - Note prosody and intonation improvements

3. **Verify cost:**
   - Check AWS billing dashboard
   - POC usage (~350 chars) should be $0.00 within free tier

---

## Code Examples

### Example 1: Basic Audio Generation

```python
from src.integrations.polly import PollyTTS

polly = PollyTTS()

# Simple sentence
success, msg = polly.generate_audio(
    text="مرحبا بك",
    xsampa="mar.Ha.ban bi.ka",
    output_path="hello.mp3"
)
```

### Example 2: Error Handling

```python
from src.integrations.polly import PollyTTS

try:
    polly = PollyTTS()
except ImportError as e:
    print(f"boto3 not installed: {e}")
    exit(1)
except RuntimeError as e:
    print(f"AWS credentials issue: {e}")
    exit(1)

success, message = polly.generate_audio(
    text="النص العربي",
    xsampa="an.naS.al.3a.ra.bij",
    output_path="output.mp3"
)

if not success:
    print(f"Audio generation failed: {message}")
    # Fallback to eSpeak or log error
```

### Example 3: Batch Processing

```python
from src.main import ArabicTTS
from src.integrations.polly import PollyTTS
import os

# Initialize
tts = ArabicTTS(dialect='MSA')
polly = PollyTTS()

# Process multiple sentences
sentences = [
    "صباح الخير",
    "مساء الخير",
    "كيف حالك؟"
]

os.makedirs("output/batch", exist_ok=True)

for i, text in enumerate(sentences, 1):
    # Get phonetics
    result = tts.process_text(text)
    xsampa = result.get('x_sampa', result.get('ipa', ''))
    
    # Generate audio
    output_path = f"output/batch/sentence_{i:03d}.mp3"
    success, msg = polly.generate_audio(
        text=text,
        xsampa=xsampa,
        output_path=output_path,
        voice_id="Zeina",
        engine="neural"
    )
    
    if success:
        print(f"✅ {i}/{len(sentences)}: {output_path}")
    else:
        print(f"❌ {i}/{len(sentences)}: {msg}")
```

### Example 4: Cost Tracking

```python
from src.integrations.polly import PollyTTS

polly = PollyTTS()

# Track characters processed
total_chars = 0
sentences = ["النص الأول", "النص الثاني", "النص الثالث"]

for text in sentences:
    success, msg = polly.generate_audio(
        text=text,
        xsampa="...",  # From your IPA engine
        output_path=f"output/{text}.mp3"
    )
    
    if success:
        total_chars += len(text)

# Calculate cost
cost_per_million = 16  # Neural engine
estimated_cost = (total_chars / 1_000_000) * cost_per_million

print(f"Characters processed: {total_chars}")
print(f"Estimated cost: ${estimated_cost:.6f}")
print(f"Within free tier: {total_chars < 5_000_000}")
```

---

## Error Handling

The PollyTTS class provides graceful error handling with clear messages.

### Common Error Scenarios

#### 1. boto3 Not Installed

**Error:**
```python
ImportError: boto3 is not installed. Please install it:
pip install boto3>=1.28.0
```

**Solution:**
```bash
pip install boto3>=1.28.0
```

#### 2. AWS Credentials Not Configured

**Error:**
```python
RuntimeError: AWS credentials not configured. See docs/polly/AWS_SETUP_GUIDE.md
```

**Solutions:**
```bash
# Option 1: AWS CLI
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID="your-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# Option 3: Credentials file
# Create ~/.aws/credentials
```

See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) for detailed instructions.

#### 3. Invalid Voice ID

**Error:**
```
ClientError: The voice 'InvalidVoice' is not supported
```

**Solution:**
Use valid Arabic voices: `Zeina` or `Hala`

#### 4. Network/Connectivity Issues

**Error:**
```
EndpointConnectionError: Could not connect to the endpoint URL
```

**Solutions:**
- Check internet connection
- Verify AWS region is correct
- Check firewall/proxy settings

#### 5. Permission Denied

**Error:**
```
ClientError: User is not authorized to perform: polly:SynthesizeSpeech
```

**Solution:**
Add `polly:SynthesizeSpeech` permission to your IAM user. See [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) section 2.4.

#### 6. Invalid SSML

**Error:**
```
ClientError: The SSML is invalid
```

**Cause:** Malformed X-SAMPA or special characters in text

**Solution:**
- Verify X-SAMPA format
- Escape special characters: `&`, `<`, `>`, `"`, `'`

---

## Troubleshooting

### Problem: "AWS credentials not configured"

**Check credentials:**
```bash
aws configure list
```

**Expected output:**
```
      Name                    Value             Type    Location
      ----                    -----             ----    --------
   profile                <not set>             None    None
access_key     ****************ABCD shared-credentials-file    
secret_key     ****************WXYZ shared-credentials-file    
    region                us-east-1      config-file    ~/.aws/config
```

**If blank:**
Follow [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md) to configure credentials.

---

### Problem: Audio quality is poor

**Checklist:**
- [ ] Using `engine="neural"` (not "standard")?
- [ ] X-SAMPA phonetics accurate from your IPA engine?
- [ ] Audio file plays correctly (not corrupted)?

**Test:**
```python
# Verify neural engine
polly.generate_audio(..., engine="neural")  # Not "standard"
```

---

### Problem: Costs are unexpectedly high

**Check usage:**
```bash
# AWS CLI
aws ce get-cost-and-usage \
  --time-period Start=2024-11-01,End=2024-11-30 \
  --granularity MONTHLY \
  --metrics UsageQuantity \
  --filter file://polly-filter.json
```

**Free tier limits:**
- 5 million characters/month for first 12 months
- After 12 months: $16/million characters (neural)

**Cost reduction:**
- Cache generated audio files (don't regenerate)
- Use standard engine for drafts ($4/million vs $16/million)
- Process text in batches

---

### Problem: Polly test passes but no audio plays

**Verify file:**
```bash
# Check file exists
ls -lh demo_output/polly_test/test_polly_001_zeina_neural.mp3

# Check file size (should be >1 KB)
# If 0 bytes → generation failed silently

# Try playing with different player
mpv output.mp3       # VLC-like player
ffplay output.mp3    # ffmpeg player
xdg-open output.mp3  # System default
```

**Verify MP3 format:**
```bash
file output.mp3
# Expected: "Audio file with ID3 version 2.4.0"
```

---

### Problem: Script runs but X-SAMPA is empty

**Cause:** `ArabicTTS.process_text()` may not return `x_sampa` key for all inputs.

**Debug:**
```python
result = tts.process_text("صباح الخير")
print("Keys:", result.keys())
print("IPA:", result.get('ipa'))
print("X-SAMPA:", result.get('x_sampa'))
```

**Fallback:**
```python
xsampa = result.get('x_sampa', result.get('ipa', ''))
```

---

## Next Steps

1. **Run POC test:** `python scripts/test_polly_integration.py`
2. **Listen to audio:** Compare Polly vs eSpeak quality
3. **Document results:** Create `docs/polly/POC_RESULTS.md`
4. **Native speaker validation:** Get feedback on pronunciation accuracy
5. **Make decision:** Go/No-Go/Iterate based on success metrics

---

## References

- **AWS Setup:** [AWS_SETUP_GUIDE.md](AWS_SETUP_GUIDE.md)
- **Test Script:** `scripts/test_polly_integration.py`
- **Output Directory:** [demo_output/polly_test/README.md](../../demo_output/polly_test/README.md)
- **PRD:** `tasks/0001-prd-polly-integration.md`
- **AWS Polly Documentation:** https://docs.aws.amazon.com/polly/
- **Polly Pricing:** https://aws.amazon.com/polly/pricing/
