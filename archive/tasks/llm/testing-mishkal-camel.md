# Testing Plan: Mishkal vs CAMeL Tools Comparison

## Objective
Test Mishkal and CAMeL Tools separately on actual CSV data to determine:
1. Which tool performs better on real-world data
2. Whether they complement each other (one catches what the other misses)
3. Best fallback sequence: Mishkal→CAMeL, CAMeL→Mishkal, or single tool

## Decision Goal
Based on results, choose architecture:
- If CAMeL catches 50%+ of Mishkal failures → Use Mishkal → CAMeL fallback
- If Mishkal catches 50%+ of CAMeL failures → Use CAMeL → Mishkal fallback
- If one tool dominates (80%+ success) → Use that tool alone
- If both fail similarly → Consider LLM fallback (optional, user pays)

## Test Data Source
Use actual CSV exports from your demo page:
- Extract all WORD-level rows from CSV
- Test on words with `Status=error` or `Failed_Layers` containing "diac"
- Also test on successful words to verify both tools work on easy cases

## Setup

### Install CAMeL Tools
```bash
pip install camel-tools
# Expected: 5 minutes, ~300MB download
```

## Usage

### Step 1: Export CSV from Demo Page
1. Go to demo page and process some Arabic text
2. Click "Download CSV" button
3. Save file (e.g., `tts_matrix_20251216_123456.csv`)

### Step 2: Run Comparison Test
```bash
cd /home/hamr/PycharmProjects/ArabicTTS/tasks/LLM

# Test on your CSV file
python test_diacritization_comparison.py /path/to/your/csv/file.csv

# Example:
python test_diacritization_comparison.py ../../static/audio/tts_matrix_20251216_123456.csv
```

### Step 3: Review Results
The script will:
1. Extract all unique words from your CSV
2. Test Mishkal on each word separately
3. Test CAMeL on each word separately
4. Compare both results side-by-side
5. Test different fallback sequences:
   - Mishkal only
   - CAMeL only
   - Mishkal → CAMeL (use CAMeL if Mishkal fails)
   - CAMeL → Mishkal (use Mishkal if CAMeL fails)
6. Generate comparison CSV: `diacritization_comparison.csv`

## Output Files

### Console Output
Shows:
- Real-time testing progress for both tools
- Success/failure for each word
- Success rate for each tool
- Fallback sequence analysis
- Recommendation

### CSV Output: `diacritization_comparison.csv`
Columns:
- `Original`: The word tested
- `Current_Status`: Status from your current system
- `Current_Failed_Layers`: Failed layers from your current system
- `Mishkal_Output`: Diacritization from Mishkal
- `Mishkal_Success`: YES/NO
- `CAMeL_Output`: Diacritization from CAMeL
- `CAMeL_Success`: YES/NO
- `Best_Result`: BOTH / Mishkal / CAMeL / NEITHER

## Analysis Questions to Answer

After running the test, review the results to answer:

1. **Overall Success Rates**:
   - What is Mishkal's success rate?
   - What is CAMeL's success rate?
   - Which one performs better overall?

2. **Complementary Analysis**:
   - How many words does CAMeL catch that Mishkal misses?
   - How many words does Mishkal catch that CAMeL misses?
   - Are they complementary or redundant?

3. **Fallback Sequence Decision**:
   - Which sequence gives best results?
   - Is the improvement worth the complexity?
   - Should we use both tools or just one?

4. **Performance Considerations**:
   - How long does CAMeL take to load?
   - Is CAMeL fast enough for production use?
   - Will CAMeL slow down the system significantly?

5. **LLM Decision**:
   - What percentage of words still fail after best fallback?
   - Is LLM needed for remaining failures?
   - What would be the estimated LLM cost?

## Next Steps After Testing

Based on results, choose architecture:

### Option 1: Mishkal → CAMeL Fallback
**When**: CAMeL catches 30%+ of Mishkal failures
**Architecture**: Mishkal → CAMeL → Character fallback
**Cost**: $0/month
**Benefit**: Free improvement, no LLM needed

### Option 2: CAMeL → Mishkal Fallback
**When**: Mishkal catches 30%+ of CAMeL failures
**Architecture**: CAMeL → Mishkal → Character fallback
**Cost**: $0/month
**Consideration**: CAMeL loading time (~30-60s on startup)

### Option 3: Single Tool Only
**When**: One tool dominates (80%+ success) or they're redundant
**Architecture**: Best tool → Character fallback
**Cost**: $0/month
**Benefit**: Simpler, faster, easier to maintain

### Option 4: Add LLM Fallback (Optional)
**When**: Still high failure rate after testing free tools
**Architecture**: Best free sequence → LLM (optional) → Character fallback
**Cost**: User pays, estimated $5-15/month
**Note**: User opts in, bears cost
