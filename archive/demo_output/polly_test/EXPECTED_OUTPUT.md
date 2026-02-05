# Expected Output - Polly Integration Test Script

This document describes the expected behavior when running `scripts/test_polly_integration.py`.

## Test Scenarios

### Scenario 1: No AWS Credentials Configured (Graceful Degradation)

**Command:**
```bash
python scripts/test_polly_integration.py
```

**Expected Behavior:**
- ✅ Script runs to completion without crashing
- ✅ Polly initialization succeeds (boto3 client created)
- ❌ Polly audio generation fails with clear error message
- ✅ eSpeak audio generation succeeds as fallback
- ✅ Helpful troubleshooting guidance displayed

**Expected Output:**
```
✅ Amazon Polly client initialized
✅ eSpeak TTS initialized

[For each test case 1-5:]
  ❌ Polly failed: AWS credentials not configured. See docs/polly/AWS_SETUP_GUIDE.md
  ✅ eSpeak: demo_output/polly_test/test_polly_00X_espeak.wav (0.4 KB)

📊 Test Results:
   Total test cases: 5
   Polly:  0 passed, 5 failed
   eSpeak: 5 passed, 0 failed

🔧 Troubleshooting:
   1. Install boto3: pip install boto3>=1.28.0
   2. Configure AWS credentials: aws configure
   3. Verify Polly access in AWS account
   4. See: docs/polly/AWS_SETUP_GUIDE.md

   eSpeak is working - comparison baseline available
```

**Files Generated:**
- 5 eSpeak WAV files only (no Polly MP3 files)
- Total size: ~2 KB

**Exit Code:** 0 (success)

---

### Scenario 2: AWS Credentials Configured (Full POC Test)

**Prerequisites:**
- AWS credentials configured: `aws configure`
- Polly access permissions in IAM

**Command:**
```bash
python scripts/test_polly_integration.py
```

**Expected Behavior:**
- ✅ Polly initialization succeeds
- ✅ eSpeak initialization succeeds
- ✅ All 5 test sentences processed
- ✅ Polly audio generation succeeds (5 MP3 files)
- ✅ eSpeak audio generation succeeds (5 WAV files)
- ✅ Cost analysis displayed
- ✅ Success metrics checklist shown

**Expected Output:**
```
✅ Amazon Polly client initialized
✅ eSpeak TTS initialized

[For each test case 1-5:]
  ✅ Polly: demo_output/polly_test/test_polly_00X_zeina_neural.mp3 (X.X KB)
  ✅ eSpeak: demo_output/polly_test/test_polly_00X_espeak.wav (0.4 KB)

📊 Test Results:
   Total test cases: 5
   Polly:  5 passed, 0 failed
   eSpeak: 5 passed, 0 failed

📁 Generated Files:
   Polly audio:  5 files, XX.X KB total
   eSpeak audio: 5 files, 2.1 KB total
   Location: demo_output/polly_test/

💰 Cost Analysis:
   Characters processed: ~350
   Cost for this POC: $0.000006 (within free tier)
   Free tier usage: 0.007% of 5M chars/month

✅ SUCCESS - Polly Integration Working!

🎯 Next Steps:
   1. Listen to all generated audio files
   2. Compare Polly vs eSpeak quality side-by-side
   3. Native speaker validation (target: ≥90% accuracy)
   4. Document findings in docs/polly/POC_RESULTS.md
   5. Make Go/No-Go decision based on success metrics

📋 Success Metrics Checklist (from PRD):
   [ ] SM-006: Audio quality significantly better than eSpeak
   [ ] SM-007: Native speaker validation ≥90% accuracy
   [ ] SM-008: Native speaker confirms 'acceptable for audiobooks'
   [✓] SM-004: AWS costs $0 (within free tier)
   [✓] SM-001: POC execution time <5 days
```

**Files Generated:**
- 5 Polly MP3 files (~5-50 KB each, depending on sentence length)
- 5 eSpeak WAV files (~0.4 KB each)
- Total: 10 audio files

**Exit Code:** 0 (success)

---

### Scenario 3: boto3 Not Installed

**Command:**
```bash
# After: pip uninstall boto3
python scripts/test_polly_integration.py
```

**Expected Behavior:**
- ❌ Polly initialization fails with ImportError
- ✅ eSpeak initialization succeeds
- ✅ Script continues with eSpeak only
- ✅ Clear installation instructions displayed

**Expected Output:**
```
❌ boto3 is not installed. Please install it:
pip install boto3>=1.28.0
✅ eSpeak TTS initialized

[Tests proceed with eSpeak only]

📊 Test Results:
   Total test cases: 5
   Polly:  0 passed, 5 failed
   eSpeak: 5 passed, 0 failed

🔧 Troubleshooting:
   1. Install boto3: pip install boto3>=1.28.0
   [...]
```

**Files Generated:**
- 5 eSpeak WAV files only

**Exit Code:** 0 (success - graceful degradation)

---

### Scenario 4: eSpeak Not Installed

**Command:**
```bash
# If eSpeak NG not installed
python scripts/test_polly_integration.py
```

**Expected Behavior:**
- ✅ Polly initialization may succeed (if AWS configured)
- ❌ eSpeak initialization fails with RuntimeError
- ✅ Script continues with Polly only
- ✅ Clear installation instructions displayed

**Expected Output:**
```
✅ Amazon Polly client initialized
❌ eSpeak NG is not installed. Please install it:
Ubuntu/Debian: sudo apt install espeak-ng
MacOS: brew install espeak-ng
[...]

[Tests proceed - Polly only if credentials configured, otherwise all fail]
```

**Files Generated:**
- If AWS configured: 5 Polly MP3 files only
- If not configured: No files

**Exit Code:** 0 (success - graceful degradation)

---

### Scenario 5: Neither boto3 nor eSpeak Installed

**Command:**
```bash
python scripts/test_polly_integration.py
```

**Expected Behavior:**
- ❌ Polly initialization fails
- ❌ eSpeak initialization fails
- ✅ Script runs to completion
- ❌ No audio files generated
- ✅ Clear setup instructions for both engines

**Expected Output:**
```
❌ boto3 is not installed. Please install it:
pip install boto3>=1.28.0
❌ eSpeak NG is not installed. Please install it:
Ubuntu/Debian: sudo apt install espeak-ng
[...]

📊 Test Results:
   Total test cases: 5
   Polly:  0 passed, 5 failed
   eSpeak: 0 passed, 5 failed

⚠️  Polly Integration Needs Setup

🔧 Troubleshooting:
   [Both engine setup instructions]
```

**Files Generated:** None

**Exit Code:** 0 (success - graceful degradation)

---

## Error Handling Verification

### ✅ Graceful Degradation
- Script never crashes
- Always exits with code 0
- Continues execution even if one engine fails
- Provides clear, actionable error messages

### ✅ User-Friendly Messages
- Points to documentation (AWS_SETUP_GUIDE.md)
- Includes exact commands to fix issues
- Explains what failed and why

### ✅ Partial Success Handling
- If Polly fails but eSpeak works: Generates eSpeak files, shows troubleshooting
- If eSpeak fails but Polly works: Generates Polly files, notes missing baseline
- If both fail: Shows setup instructions for both

---

## Performance Expectations

### Execution Time
- **With AWS credentials:** ~10-30 seconds (depends on network latency)
- **Without AWS credentials:** ~5-10 seconds (eSpeak only, local processing)

### File Sizes
- **Polly MP3:** 5-15 KB per short sentence, 30-50 KB for long sentence
- **eSpeak WAV:** ~0.4 KB per sentence (very compressed)

### Network Requirements
- **Polly:** Requires internet connection
- **eSpeak:** Works offline

---

## Troubleshooting Common Issues

### "Syllabification: N/A" / "IPA: N/A"
**Cause:** ArabicTTS.process_text() may not include these keys for all inputs

**Impact:** None - X-SAMPA extraction still works via fallback

**Action:** Not a blocker for POC

### Very small eSpeak files (0.4 KB)
**Cause:** Minimal/empty IPA input due to test data processing

**Impact:** eSpeak files may be silent or very short

**Action:** Expected behavior - validates error handling

### Polly costs shown as $0.000000
**Cause:** POC uses ~350 characters, which is negligible

**Impact:** None - demonstrates free tier usage

**Action:** Expected - costs only visible at scale (1000s of characters)

---

## Next Steps After Successful Run

1. **Verify files exist:**
   ```bash
   ls -lh demo_output/polly_test/
   ```

2. **Play audio files:**
   ```bash
   # Polly (if generated)
   mpv demo_output/polly_test/test_polly_001_zeina_neural.mp3
   
   # eSpeak (for comparison)
   aplay demo_output/polly_test/test_polly_001_espeak.wav
   ```

3. **Compare quality:**
   - Listen to both versions of each test
   - Note naturalness, pronunciation, clarity
   - Document findings

4. **Create POC results document:**
   ```bash
   # Template location
   docs/polly/POC_RESULTS.md
   ```

5. **Make Go/No-Go decision:**
   - Review success metrics checklist
   - Get native speaker validation
   - Decide: Go / Iterate / No-Go

---

## References

- **Test Script:** `scripts/test_polly_integration.py`
- **PRD:** `tasks/0001-prd-polly-integration.md`
- **Setup Guide:** `docs/polly/AWS_SETUP_GUIDE.md`
- **Output README:** `demo_output/polly_test/README.md`
