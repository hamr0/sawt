# LLM Tasks: Diacritization Testing & Documentation

This folder contains testing scripts and historical documentation for diacritization strategy.

## Quick Start

### Test Mishkal Diacritization

```bash
# Export CSV from demo page, then test it
cd /home/hamr/PycharmProjects/ArabicTTS/tasks/llm
python test_mishkal_diacritization.py /path/to/your/csv/file.csv
```

**Output**:
- Console: Real-time results and success statistics
- CSV: `mishkal_test_results.csv` with detailed results

## Files

### Testing
- **`test_mishkal_diacritization.py`**: Mishkal test script
  - Tests Mishkal on CSV words
  - Generates success statistics
  - Outputs detailed results CSV

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
