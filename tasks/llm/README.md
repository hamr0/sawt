# LLM Tasks: Diacritization Testing & Fallback Strategy

This folder contains testing scripts and plans for improving diacritization accuracy.

## Quick Start

### 1. Test Mishkal vs CAMeL (DO THIS FIRST)

```bash
# Install CAMeL Tools
pip install camel-tools

# Export CSV from demo page, then test it
cd /home/hamr/PycharmProjects/ArabicTTS/tasks/LLM
python test_diacritization_comparison.py /path/to/your/csv/file.csv
```

**Output**:
- Console: Real-time results and recommendations
- CSV: `diacritization_comparison.csv` with side-by-side comparison

### 2. Make Decision

Based on test results, choose:
- **Mishkal → CAMeL**: If CAMeL catches 30%+ of Mishkal failures
- **CAMeL → Mishkal**: If Mishkal catches 30%+ of CAMeL failures
- **Single tool**: If one dominates or they're redundant
- **Add LLM**: If free tools still have high failure rate (user pays)

## Files

### Testing
- **`test_diacritization_comparison.py`**: Main test script
  - Tests Mishkal separately
  - Tests CAMeL separately
  - Compares both on same data
  - Tests 4 fallback sequences
  - Generates comparison CSV

### Documentation
- **`testing-mishkal-camel.md`**: Testing plan and instructions
- **`llm-fallback-strategy.md`**: Complete LLM integration strategy
  - Multi-tier architecture
  - LLM JSON prompts
  - Cost analysis
  - Exception dictionary design (future)

## Architecture (After Testing)

Current plan (to be validated by tests):

```
Tier 1: Mishkal (Fast, Free)
   ↓ (if fails)
Tier 2: CAMeL Tools (Slower, Free) - TODO: Test if worthwhile
   ↓ (if fails)
Tier 3: LLM (Optional, User Pays) - TODO: Implement if needed
   ↓ (if fails)
Tier 4: Character Fallback (Already Implemented)
```

## Important Notes

1. **No Exception Dictionary Yet**: Empty dictionary makes no sense as Tier 1. Will only create AFTER we have data to populate it (from LLM usage or manual curation).

2. **Test First**: Don't implement anything until testing shows what actually works.

3. **Free Tools First**: Exhaust free options (Mishkal + CAMeL) before considering LLM.

4. **User Bears LLM Costs**: If LLM is needed, user opts in and is responsible for API costs.

## Next Steps

1. ✅ Testing plan created
2. ✅ Test script ready
3. ⏳ Run tests on actual CSV data
4. ⏳ Analyze results
5. ⏳ Choose architecture
6. ⏳ Implement best fallback sequence
