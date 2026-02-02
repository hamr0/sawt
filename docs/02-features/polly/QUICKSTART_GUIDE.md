# Amazon Polly Integration - Quick Start Guide

This guide shows you **exactly** how to run the Polly POC test yourself and evaluate the results.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites Check

```bash
# 1. Check Python version (need 3.8+)
python3 --version
# Should show: Python 3.10.12 or higher

# 2. Check boto3 installed
python3 -c "import boto3; print(f'boto3 {boto3.__version__}')"
# Should show: boto3 1.40.64 or similar

# 3. Check eSpeak installed
espeak-ng --version
# Should show version info

# 4. Navigate to project
cd /home/hamr/PycharmProjects/ArabicTTS
```

### Step 1: Verify AWS Credentials

Your AWS credentials are already configured in `.env` file. Verify they work:

```bash
# Load credentials and test connection
export AWS_ACCESS_KEY_ID=AKIAZT4LJJX2UI72WWGW
export AWS_SECRET_ACCESS_KEY="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"
export AWS_DEFAULT_REGION=us-east-1

# Test connection
python3 -c "
import boto3
client = boto3.client('polly', region_name='us-east-1')
response = client.describe_voices(LanguageCode='arb')
print('✅ AWS Connection Successful!')
print(f\"Available voices: {[v['Id'] for v in response['Voices']]}\")
"
```

**Expected output:**
```
✅ AWS Connection Successful!
Available voices: ['Zeina']
```

---

## 📝 Step 2: Run the POC Test

### Option A: Using Environment Variables (Recommended)

```bash
cd /home/hamr/PycharmProjects/ArabicTTS

# Set credentials
export AWS_ACCESS_KEY_ID=AKIAZT4LJJX2UI72WWGW
export AWS_SECRET_ACCESS_KEY="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"
export AWS_DEFAULT_REGION=us-east-1

# Run test
python3 scripts/test_polly_integration.py
```

### Option B: Using .env File (Automatic)

The script will automatically read from `.env` if you've set it up. Just run:

```bash
cd /home/hamr/PycharmProjects/ArabicTTS
python3 scripts/test_polly_integration.py
```

**Note:** If you see "AWS credentials not configured", use Option A.

---

## 📊 Step 3: Understand the Output

### What You'll See

The script will:
1. ✅ Initialize Polly and eSpeak clients
2. 📝 Process 5 test sentences
3. 🎵 Generate 10 audio files (5 Polly + 5 eSpeak)
4. 📈 Show summary report

### Sample Output

```
╔════════════════════════════════════════════════════════════════╗
║     Amazon Polly Integration Test for Arabic TTS              ║
╚════════════════════════════════════════════════════════════════╝

✅ Amazon Polly client initialized
✅ eSpeak TTS initialized

############################################################
Test Case 1/5: Good morning
Pattern: Simple sentence with common words
############################################################

Testing: صباح الخير

Step 1: Processing with your IPA engine...
Step 2: Generating audio with Amazon Polly...
  ✅ Polly: demo_output/polly_test/test_polly_001_zeina_standard.mp3 (0.5 KB)
Step 3: Generating audio with eSpeak (for comparison)...
  ✅ eSpeak: demo_output/polly_test/test_polly_001_espeak.wav (0.4 KB)

[... 4 more tests ...]

============================================================
POC TEST SUMMARY REPORT
============================================================

📊 Test Results:
   Total test cases: 5
   Polly:  5 passed, 0 failed
   eSpeak: 5 passed, 0 failed

📁 Generated Files:
   Polly audio:  5 files, 2.5 KB total
   eSpeak audio: 5 files, 2.1 KB total
   Location: demo_output/polly_test/

💰 Cost Analysis:
   Characters processed: 105
   Cost for this POC: $0.001680 (within free tier)
   Free tier usage: 0.002% of 5M chars/month
   
   Production estimates (after free tier):
   • 100k word audiobook (~600k chars): $9.60
   • 10 audiobooks/month (~6M chars):  $96.00

✅ SUCCESS - Polly Integration Working!
```

---

## 🎧 Step 4: Listen to Audio Files

### 4.1 Check Files Generated

```bash
cd /home/hamr/PycharmProjects/ArabicTTS/demo_output/polly_test

# List all files
ls -lh

# Expected output:
# test_polly_001_zeina_standard.mp3
# test_polly_001_espeak.wav
# test_polly_002_zeina_standard.mp3
# test_polly_002_espeak.wav
# ... (10 files total)
```

### 4.2 Play Audio Files

**Method 1: mpv (Media Player)**
```bash
# Play Polly audio
mpv test_polly_001_zeina_standard.mp3

# Play eSpeak audio
mpv test_polly_001_espeak.wav
```

**Method 2: aplay (ALSA Player - WAV only)**
```bash
# eSpeak files
aplay test_polly_001_espeak.wav
```

**Method 3: VLC (GUI)**
```bash
vlc test_polly_001_zeina_standard.mp3
```

**Method 4: File Manager**
- Navigate to `/home/hamr/PycharmProjects/ArabicTTS/demo_output/polly_test/`
- Double-click any audio file to play with default player

### 4.3 Compare Side-by-Side

For each test case (001-005), compare Polly vs eSpeak:

```bash
cd /home/hamr/PycharmProjects/ArabicTTS/demo_output/polly_test

# Test 1: صباح الخير (Good morning)
echo "=== Test 1: Simple sentence ==="
echo "Playing Polly..."
mpv test_polly_001_zeina_standard.mp3
echo "Playing eSpeak..."
mpv test_polly_001_espeak.wav

# Test 2: المدرسة الجديدة (The new school)
echo "=== Test 2: Consonant clusters ==="
mpv test_polly_002_zeina_standard.mp3
mpv test_polly_002_espeak.wav

# Test 3: كتابٌ جديدٌ (A new book)
echo "=== Test 3: Tanween ==="
mpv test_polly_003_zeina_standard.mp3
mpv test_polly_003_espeak.wav

# Test 4: Long sentence
echo "=== Test 4: Long sentence ==="
mpv test_polly_004_zeina_standard.mp3
mpv test_polly_004_espeak.wav

# Test 5: Challenging phonemes
echo "=== Test 5: Challenging phonemes ==="
mpv test_polly_005_zeina_standard.mp3
mpv test_polly_005_espeak.wav
```

---

## 📋 Step 5: Evaluate Quality

### What to Listen For

For each audio file, rate on a scale of 1-10:

**1. Naturalness**
- Does it sound like a human or a robot?
- Is the speech flow natural?

**2. Clarity**
- Can you understand every word clearly?
- Is the audio quality good?

**3. Pronunciation**
- Are the Arabic phonemes correct?
- Are diacritics (harakat) pronounced properly?
- Sun letters vs moon letters correct?

**4. Prosody/Intonation**
- Does it have natural rhythm?
- Are pauses in the right places?

**5. Overall**
- Would you listen to a full audiobook in this quality?

### Evaluation Template

```markdown
## Test 001: صباح الخير (Good morning)

### Polly
- Naturalness: [1-10]
- Clarity: [1-10]
- Pronunciation: [1-10]
- Prosody: [1-10]
- Overall: [1-10]
- Notes: [Your observations]

### eSpeak
- Naturalness: [1-10]
- Clarity: [1-10]
- Pronunciation: [1-10]
- Prosody: [1-10]
- Overall: [1-10]
- Notes: [Your observations]

### Winner: [Polly / eSpeak / Tie]
### Reason: [Why?]

---

[Repeat for tests 002-005]
```

---

## 💰 Step 6: Check AWS Costs

### Method 1: Command Line (Cost Explorer API)

```bash
# Check usage for current month
export AWS_ACCESS_KEY_ID=AKIAZT4LJJX2UI72WWGW
export AWS_SECRET_ACCESS_KEY="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"
export AWS_DEFAULT_REGION=us-east-1

python3 -c "
import boto3
from datetime import datetime, timedelta

# Get cost for last 7 days
ce = boto3.client('ce', region_name='us-east-1')
end = datetime.now().date()
start = end - timedelta(days=7)

response = ce.get_cost_and_usage(
    TimePeriod={'Start': str(start), 'End': str(end)},
    Granularity='DAILY',
    Metrics=['UnblendedCost'],
    Filter={
        'Dimensions': {
            'Key': 'SERVICE',
            'Values': ['Amazon Polly']
        }
    }
)

total = sum(float(day['Total']['UnblendedCost']['Amount']) for day in response['ResultsByTime'])
print(f'Polly costs (last 7 days): \${total:.6f}')
"
```

### Method 2: AWS Console (Web Interface)

1. Go to: https://console.aws.amazon.com/billing/
2. Click "Bills" in left sidebar
3. Look for "Amazon Polly" service
4. Should show $0.00 (within free tier)

### Expected Costs

**For this POC:**
- Characters: 105
- Cost: $0.001680
- Free tier covers: 5,000,000 characters/month
- Usage: 0.002% of free tier

**You should see:** $0.00 charged (covered by free tier)

---

## 📝 Step 7: Fill Out POC Results

### 7.1 Copy the Template

```bash
cd /home/hamr/PycharmProjects/ArabicTTS/docs/polly

# Copy template to create your results
cp POC_RESULTS_TEMPLATE.md POC_RESULTS.md
```

### 7.2 Edit the Results File

```bash
# Open in your favorite editor
nano POC_RESULTS.md
# or
vim POC_RESULTS.md
# or
code POC_RESULTS.md  # VS Code
```

### 7.3 What to Fill In

**Required sections:**
1. **Executive Summary**
   - Your GO/NO-GO/ITERATE decision
   - 1-line summary
   - Key findings

2. **Success Metrics Evaluation**
   - Section 2: Fill in the comparison table
   - Your listening observations for each test
   - Rating: Polly vs eSpeak (1-10 scale)

3. **Cost Analysis**
   - Confirm the costs shown in test output
   - Your assessment: is this reasonable?

4. **Final Decision**
   - Your recommendation with justification

**Optional but recommended:**
5. Native speaker validation (if you have access)
6. Open questions for future work
7. Next steps based on decision

---

## 🔄 Complete Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│ Step 1: Prerequisites                                   │
│ - Python 3.8+, boto3, eSpeak installed                 │
│ - AWS credentials configured                            │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 2: Run Test Script                                 │
│ $ python3 scripts/test_polly_integration.py            │
│                                                          │
│ Generates:                                               │
│ - 5 Polly MP3 files                                     │
│ - 5 eSpeak WAV files                                    │
│ - Cost analysis report                                  │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 3: Listen & Compare                                │
│ $ mpv test_polly_001_zeina_standard.mp3                │
│ $ mpv test_polly_001_espeak.wav                         │
│                                                          │
│ Evaluate:                                                │
│ - Naturalness, clarity, pronunciation                   │
│ - Rate 1-10 for each criterion                         │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 4: Check Costs                                     │
│ - AWS Console or CLI                                    │
│ - Should be $0.00 (within free tier)                   │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 5: Document Results                                │
│ $ cp POC_RESULTS_TEMPLATE.md POC_RESULTS.md            │
│ $ nano POC_RESULTS.md                                   │
│                                                          │
│ Fill in:                                                 │
│ - Your listening evaluation                             │
│ - Quality comparison                                    │
│ - GO/NO-GO decision                                     │
└────────────────┬────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────┐
│ Step 6: Make Decision                                   │
│ ✅ GO      → Proceed to production                      │
│ 🔄 ITERATE → Improve and re-test                        │
│ ❌ NO-GO   → Evaluate alternatives                       │
└─────────────────────────────────────────────────────────┘
```

---

## 🆘 Troubleshooting

### Problem: "AWS credentials not configured"

**Solution:**
```bash
# Set credentials manually
export AWS_ACCESS_KEY_ID=AKIAZT4LJJX2UI72WWGW
export AWS_SECRET_ACCESS_KEY="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"
export AWS_DEFAULT_REGION=us-east-1

# Then run test again
python3 scripts/test_polly_integration.py
```

### Problem: "Polly failed: This voice does not support the selected engine: neural"

**Solution:**  
This is already fixed! Zeina only supports `standard` engine (not `neural`). The script now uses `standard`.

### Problem: No audio when playing files

**Check file size:**
```bash
ls -lh demo_output/polly_test/*.mp3
# Should be ~514 bytes each
```

**If 0 bytes:** Generation failed. Check AWS credentials.

**Try different player:**
```bash
# Try all these
mpv test_polly_001_zeina_standard.mp3
vlc test_polly_001_zeina_standard.mp3
ffplay test_polly_001_zeina_standard.mp3
```

### Problem: "boto3 not installed"

```bash
pip install boto3>=1.28.0
```

### Problem: "eSpeak not installed"

```bash
# Ubuntu/Debian
sudo apt install espeak-ng

# Verify
espeak-ng --version
```

---

## 📚 Reference Files

| File | Purpose |
|------|---------|
| `scripts/test_polly_integration.py` | Main test script |
| `docs/polly/AWS_SETUP_GUIDE.md` | AWS credentials setup |
| `docs/polly/POLLY_USAGE_GUIDE.md` | API reference & examples |
| `docs/polly/POC_RESULTS_TEMPLATE.md` | Template for your evaluation |
| `demo_output/polly_test/README.md` | Output directory guide |
| `demo_output/polly_test/EXPECTED_OUTPUT.md` | What to expect |

---

## ⏱️ Time Estimate

- **Prerequisites check:** 2 minutes
- **Run test script:** 1 minute
- **Listen to audio (all 10 files):** 5 minutes
- **Fill POC results:** 10-20 minutes
- **Total:** ~20-30 minutes

---

## 🎯 Next Steps After Evaluation

### If Quality is Good (GO Decision):
1. Test with longer content (full chapter)
2. Schedule native speaker validation
3. Plan production deployment
4. Monitor costs for first month

### If Quality Needs Work (ITERATE):
1. Improve X-SAMPA phonetic mapping
2. Test with different voices/regions
3. Re-run POC after improvements

### If Quality is Poor (NO-GO):
1. Evaluate alternatives (Google Cloud TTS, Azure)
2. Improve eSpeak quality instead
3. Document findings for future reference

---

## 💡 Tips for Best Results

1. **Listen with headphones** for accurate quality assessment
2. **Compare side-by-side** (Polly vs eSpeak for same sentence)
3. **Share with native speaker** if possible
4. **Test on different devices** (phone, laptop, speakers)
5. **Document specific issues** you hear (not just ratings)

---

**Questions?** Check:
- `docs/polly/POLLY_USAGE_GUIDE.md` - Complete usage guide
- `docs/polly/AWS_SETUP_GUIDE.md` - Credential setup help
- `demo_output/polly_test/README.md` - Output file details

**Ready to start?** Run:
```bash
cd /home/hamr/PycharmProjects/ArabicTTS
python3 scripts/test_polly_integration.py
```

Good luck! 🚀
