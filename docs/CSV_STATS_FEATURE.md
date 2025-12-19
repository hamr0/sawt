# CSV Processing Stats Feature

**Date:** December 18, 2025
**Status:** ✅ Implemented and Tested

## Overview

Added automatic processing statistics as the last row in all generated CSV files. The stats row shows:
- Total words processed
- Success count
- Warning count
- Error count
- Success rate percentage

## Implementation

### Modified Files

1. **app.py** (lines 837-892)
   - Modified `_generate_hierarchical_csv()` function
   - Added stats tracking during row iteration
   - Appends "Processing Stats" row at the end

2. **tasks/llm/test_mishkal_diacritization.py** (lines 121-154)
   - Modified `save_results_csv()` function
   - Added stats tracking for Mishkal test results
   - Appends "Processing Stats" row at the end

### Stats Row Format

**For TTS Matrix CSV (app.py):**

Last two rows of CSV:
```csv
Processing Stats,Total: 353,Success: 342,Warning: 8 diac,Error: 3 diac,syl,ipa,Success Rate: 96.9%,-,-,-,-,-,-,-
Notes,Failed Layer Codes:,diac=Diacritization,syl=Syllabification,ipa=IPA Generation,phon=Phonology Rules,-,-,-,-,-,-,-
```

**Processing Stats Row** - Column mapping:
- Type: "Processing Stats"
- Word: Total count
- Position: Success count
- Original: Warning count + most common failed layer(s)
- Diacritized: Error count + most common failed layer(s)
- Syllable_Pattern: Success rate percentage
- Remaining columns: `-` (placeholders)

**Notes Row** - Column mapping:
- Type: "Notes"
- Word: "Failed Layer Codes:"
- Position: diac explanation
- Original: syl explanation
- Diacritized: ipa explanation
- Syllable_Pattern: phon explanation
- Remaining columns: `-` (placeholders)

**Examples:**
- No errors: `Warning: 0` / `Error: 0`
- With errors: `Warning: 8 diac` / `Error: 3 diac,syl,ipa`

**For Mishkal Test CSV:**

Last two rows of CSV:
```csv
Processing Stats,Total: 353,Success: 200,Error: 153 diac,ipa,Success Rate: 56.7%
Notes,Failed Layer Codes:,diac=Diacritization,ipa=IPA Generation,syl=Syllabification
```

**Processing Stats Row** - Column mapping:
- Original: "Processing Stats"
- Current_Status: Total count
- Current_Failed_Layers: Success count
- Mishkal_Output: Error count + most common failed layer(s)
- Mishkal_Success: Success rate percentage

**Notes Row** - Column mapping:
- Original: "Notes"
- Current_Status: "Failed Layer Codes:"
- Current_Failed_Layers: diac explanation
- Mishkal_Output: ipa explanation
- Mishkal_Success: syl explanation

## Testing

Test script created: `test_csv_stats.py` (can be removed after verification)

**Test Results:**
```
Input: "صباح الخير يا صديقي" (MSA)
Output: 23-line CSV with stats in last 2 rows

Line 22 (Stats): Processing Stats,Total: 4,Success: 4,Warning: 0,Error: 0,Success Rate: 100.0%,-,-,-,-,-,-,-
Line 23 (Notes): Notes,Failed Layer Codes:,diac=Diacritization,syl=Syllabification,ipa=IPA Generation,phon=Phonology Rules,-,-,-,-,-,-,-

Status: ✓ PASSED - Both stats and notes rows present

Note: When warnings/errors occur with failed layers, the format becomes:
Processing Stats,Total: 353,Success: 342,Warning: 8 diac,Error: 3 diac,syl,ipa,Success Rate: 96.9%,-,-,-,-,-,-,-
Notes,Failed Layer Codes:,diac=Diacritization,syl=Syllabification,ipa=IPA Generation,phon=Phonology Rules,-,-,-,-,-,-,-
```

## Usage

No changes needed for users. The stats row is automatically appended to:

1. **Web Interface CSV Downloads**
   - Export from Flask app (`/download/hierarchical/csv`)
   - Stats show in last row of downloaded CSV

2. **Mishkal Test Results**
   ```bash
   python tasks/llm/test_mishkal_diacritization.py input.csv --output results.csv
   ```
   - Stats show in last row of results.csv

## Failed Layer Codes

When warnings or errors occur, the most common failed layer type is shown:

- **diac**: Diacritization failed
- **syl**: Syllabification failed (UNKNOWN patterns)
- **ipa**: IPA generation failed (missing or invalid)
- **phon**: Phonology rules failed

Multiple failures are shown as comma-separated: `diac,syl,ipa`

## Benefits

1. **Quick Overview**: Stats visible at a glance when opening CSV
2. **Failure Insight**: See most common failure type without analyzing full dataset
3. **Self-Documenting**: Notes row explains what each failure code means
4. **Excel/Sheets Friendly**: Last rows are easy to find in spreadsheets
5. **Automated**: No manual calculation or reference lookup needed
6. **Consistent**: Same format across all generated CSVs

## Example

Opening a CSV in Excel will show:
- Rows 1-N: Detailed processing data
- Row N+1: **Processing Stats** with summary
- Row N+2: **Notes** with failed layer code explanations

**Example with 353 words:**
```
Row N+1: Processing Stats | Total: 353 | Success: 342 | Warning: 8 diac | Error: 3 diac,syl,ipa | Success Rate: 96.9%
Row N+2: Notes | Failed Layer Codes: | diac=Diacritization | syl=Syllabification | ipa=IPA Generation | phon=Phonology Rules
```

This allows quick assessment of:
- How many words were processed? (353)
- What's the success rate? (96.9%)
- How many errors/warnings occurred? (8 warnings, 3 errors)
- What's the most common failure? (diacritization issues for warnings, multiple layer failures for errors)
- What do the failure codes mean? (Check the Notes row for explanations)

## Future Enhancements

Potential additions:
- [ ] Processing time/performance metrics
- [x] Breakdown by failure type (most common shown) ✓ COMPLETED
- [ ] Full failure type distribution (show all failure types, not just most common)
- [ ] Comparison with baseline (if baseline provided)

---

*Feature requested and implemented on December 18, 2025*
