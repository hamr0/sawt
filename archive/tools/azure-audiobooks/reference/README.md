# Azure Speech Service TTS Testing Framework

Comprehensive testing framework for evaluating Azure Speech Service with X-SAMPA phonetic control vs plain text for Arabic audiobooks.

## Overview

This directory contains tools to answer the critical question: **Does X-SAMPA phonetic control add enough value to justify maintaining the phonological processing pipeline?**

### What's Included

- **Azure Integration** (`azure_integration.py`) - Wrapper for Azure Speech Service
- **Test Orchestrator** (`test_azure_phonetic_control.py`) - Main test suite with 5 comprehensive tests
- **Sample Generator** (`generate_test_samples.py`) - Creates test content from existing datasets
- **Engine Comparison** (`compare_engines.py`) - Compare Azure vs Polly vs eSpeak
- **Hello World Test** (`test_azure_hello_world.py`) - Quick validation that Azure X-SAMPA works

## Prerequisites

### 1. Azure Account Setup

1. Create Azure account: https://azure.microsoft.com/free/
2. Create Speech Service resource:
   - Go to https://portal.azure.com
   - Search for "Speech Services"
   - Click "Create"
   - Select region (recommend: East US)
   - Choose free tier (F0) or standard (S0)
3. Get your subscription key:
   - Go to resource → Keys and Endpoint
   - Copy "Key 1"

### 2. Install Dependencies

```bash
# Install Azure Speech SDK
pip install azure-cognitiveservices-speech

# Set environment variable (Linux/Mac)
export AZURE_SPEECH_KEY='your-key-here'

# Or set environment variable (Windows)
set AZURE_SPEECH_KEY=your-key-here

# Verify installation
python3 -c "import azure.cognitiveservices.speech as speechsdk; print('Azure SDK installed')"
```

### 3. Verify Existing Sawt Setup

```bash
# Make sure you're in the project root
cd /home/hamr/PycharmProjects/Sawt

# Run tests to ensure pipeline works
pytest tests/ -v

# Test the main TTS engine
python3 -c "from src.main import Sawt; tts = Sawt(); print('Sawt ready')"
```

## Quick Start

### Step 1: Hello World Test

Verify Azure X-SAMPA support works:

```bash
cd /home/hamr/PycharmProjects/Sawt
python3 tools/azure_tts/test_azure_hello_world.py
```

This will generate 2 files in `/tmp/`:
- `test_azure_plain.mp3` - Plain Arabic text
- `test_azure_xsampa.mp3` - With X-SAMPA phonetic control

**Listen to both files.** If they sound **different**, X-SAMPA is working! If they sound **identical**, there's an issue.

### Step 2: Generate Test Samples

Create the 5 test samples (~5 minutes each):

```bash
python3 tools/azure_tts/generate_test_samples.py
```

This creates:
- `samples/sample1_phonological.txt` - Phonological features
- `samples/sample2_rare_words.txt` - Rare/ambiguous words
- `samples/sample3_multidialect.txt` - Multi-dialect consistency
- `samples/sample4_dialogue.txt` - Multi-voice character dialogue
- `samples/sample5_chapter.txt` - Long-form audiobook chapter

### Step 3: Run Full Test Suite

Generate all audio files and comparison data:

```bash
python3 tools/azure_tts/test_azure_phonetic_control.py
```

This will:
1. Process each sample through the Arabic TTS pipeline
2. Generate plain text versions (Azure)
3. Generate X-SAMPA versions (Azure)
4. Calculate cost estimates
5. Create summary report

Output:
- `outputs/*.mp3` - 10-15 audio files
- `results/test_run_summary.txt` - Test results

**Estimated time:** 10-15 minutes
**Estimated cost:** $0 (within free tier)

### Step 4: Multi-Engine Comparison (Optional)

Compare Azure vs Polly vs eSpeak:

```bash
python3 tools/azure_tts/compare_engines.py
```

This generates:
- Side-by-side audio files from all 3 engines
- Blind test manifests for objective rating
- Comparison data

## Test Samples Explained

### Sample 1: Phonological Features Showcase
**Purpose:** Test if X-SAMPA improves accuracy for complex phonological features
- Content: Gemination, sun letters, emphatic spread, allophones
- Duration: ~5 minutes
- Expected outcome: X-SAMPA should handle these features more accurately

### Sample 2: Rare/Ambiguous Words
**Purpose:** Test if X-SAMPA helps with words not in Azure's training data
- Content: 20-30 uncommon Arabic words from masterTTS.json
- Duration: ~5 minutes
- Expected outcome: X-SAMPA should improve pronunciation of rare words

### Sample 3: Multi-Dialect Consistency
**Purpose:** Test dialect switching (MSA → Egyptian → Gulf)
- Content: Same passage in 3 dialects with 3 different voices
- Duration: ~5 minutes (3x same passage)
- Expected outcome: X-SAMPA should maintain consistent pronunciation across voices

### Sample 4: Multi-Voice Character Dialogue
**Purpose:** Test character differentiation in audiobooks
- Content: Dialogue between narrator, male character, female character
- Duration: ~5 minutes
- Expected outcome: X-SAMPA should ensure consistent pronunciation when switching voices

### Sample 5: Long-Form Audiobook Chapter
**Purpose:** Test real-world audiobook production scenario
- Content: Full chapter with narrative, dialogue, description
- Duration: ~5 minutes
- Expected outcome: End-to-end quality assessment + cost calculation

## Evaluation Methodology

### Rating Criteria (1-5 scale)

#### 1. Voice Quality
- **5** - Perfectly natural, indistinguishable from human
- **4** - Very good, minor robotic artifacts
- **3** - Acceptable, some unnatural prosody
- **2** - Noticeable issues, listening fatigue
- **1** - Robotic, difficult to understand

#### 2. Pronunciation Accuracy
- **5** - 100% correct, all phonological features accurate
- **4** - 90-95% correct, minor errors
- **3** - 80-90% correct, some mispronunciations
- **2** - 70-80% correct, frequent errors
- **1** - <70% correct, many words wrong

#### 3. Multi-Voice Consistency (Sample 4 only)
- **5** - Perfect consistency across voices
- **4** - Very consistent, 1-2 minor variations
- **3** - Mostly consistent, some variations
- **2** - Inconsistent pronunciation
- **1** - Different pronunciations for same words

### Decision Criteria

**X-SAMPA is worth keeping if:**
- ✅ Azure X-SAMPA scores ≥ 0.5 points higher than plain text in pronunciation accuracy
- ✅ Multi-voice consistency is noticeably better with X-SAMPA
- ✅ Rare words pronounced more accurately with X-SAMPA

**Plain text is sufficient if:**
- ❌ Azure plain text scores within 0.3 points of X-SAMPA
- ❌ Multi-voice works well without X-SAMPA
- ❌ Azure handles rare words correctly without phonetic hints

## Cost Analysis

### Azure Pricing
- **Free Tier:** 5M characters/month for 12 months (first-time users)
- **Standard Tier:** $16 per 1M characters (Neural voices)

### Test Suite Cost
- 5 samples × ~1,000 words each = ~5,000 words
- ~35,000 characters total (Arabic averages 7 chars/word)
- **Cost:** ~$0.56 (well within free tier)

### Production Audiobook Cost
- Average audiobook: 100,000 words
- ~700,000 characters
- **Cost:** ~$11.20 per audiobook

## Troubleshooting

### Error: "Azure subscription key not provided"
**Solution:** Set environment variable:
```bash
export AZURE_SPEECH_KEY='your-key-here'
```

### Error: "Azure Speech SDK is not installed"
**Solution:** Install SDK:
```bash
pip install azure-cognitiveservices-speech
```

### Error: "Arabic TTS pipeline failed"
**Solution:** Check that you're in the project root and dependencies are installed:
```bash
cd /home/hamr/PycharmProjects/Sawt
pip install -r requirements.txt
```

### Empty X-SAMPA output
**Reason:** Some syllables may not generate X-SAMPA
**Solution:** This is handled gracefully - plain text is used as fallback

### Audio sounds identical (plain vs X-SAMPA)
**Possible causes:**
1. Azure may be ignoring phoneme tags for Arabic (similar to Polly issue)
2. X-SAMPA conversion errors
3. SSML formatting issues

**Action:** Run `test_azure_hello_world.py` and check if outputs are actually different

## Project Structure

```
tools/azure_tts/
├── README.md                          # This file
├── azure_integration.py               # Azure Speech Service wrapper (~350 LOC)
├── test_azure_hello_world.py          # Quick validation test (~100 LOC)
├── test_azure_phonetic_control.py     # Main test suite (~450 LOC)
├── generate_test_samples.py           # Sample generator (~300 LOC)
├── compare_engines.py                 # Multi-engine comparison (~300 LOC)
├── samples/                           # Test content files
│   ├── sample1_phonological.txt
│   ├── sample2_rare_words.txt
│   ├── sample3_multidialect.txt
│   ├── sample4_dialogue.txt
│   └── sample5_chapter.txt
├── outputs/                           # Generated audio files
│   ├── sample1_plain.mp3
│   ├── sample1_xsampa.mp3
│   └── ... (10-15 files)
└── results/                           # Analysis reports
    ├── test_run_summary.txt
    ├── quality_comparison.md          # To be filled manually
    ├── cost_analysis.md               # Generated by tests
    └── decision_matrix.md             # Final recommendation
```

## Next Steps After Testing

### If Azure X-SAMPA is the winner:
1. Move `azure_integration.py` to `src/integrations/`
2. Update `app.py` to support Azure as TTS option
3. Add Azure configuration to settings
4. Document Azure setup in `docs/azure/`
5. Update `CLAUDE.md` with Azure as production TTS

### If plain text is sufficient:
1. Consider simplifying pipeline (remove X-SAMPA generation)
2. Keep phonological processors for future use
3. Use Azure with plain text for production
4. Document decision in `STRATEGIC_DECISION_ANALYSIS.md`

### If multi-engine approach is best:
1. Keep X-SAMPA pipeline
2. Support multiple TTS backends (Azure, eSpeak, Festival)
3. Let users choose based on use case
4. Document trade-offs

## References

- **Azure Speech Service Docs:** https://docs.microsoft.com/azure/cognitive-services/speech-service/
- **SSML Phoneme Support:** https://docs.microsoft.com/azure/cognitive-services/speech-service/speech-synthesis-markup
- **Arabic Voice Support:** https://docs.microsoft.com/azure/cognitive-services/speech-service/language-support
- **X-SAMPA Specification:** https://www.phon.ucl.ac.uk/home/sampa/x-sampa.htm

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `TTS_ENGINES_COMPARISON_2025.md` for background
3. Check `STRATEGIC_DECISION_ANALYSIS.md` for strategic context
4. Review `POLLY_REALITY_CHECK.md` for lessons learned from Polly

---

**Version:** 1.0
**Date:** December 18, 2025
**Author:** Sawt Project
**Status:** Ready for testing
