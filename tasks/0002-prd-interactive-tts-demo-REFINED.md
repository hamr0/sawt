# PRD: Interactive TTS Demo - FINALIZED
## Matrix-Based Debugging & Validation Tool for Pronunciation Enhancements

**Project:** Arabic TTS Interactive Demo
**Phase:** MVP (Refined from initial PRD)
**Version:** 3.0 (Finalized)
**Date:** December 14, 2025
**Owner:** Development Team
**Status:** FINALIZED - Ready for Implementation

---

## Executive Summary

**FINALIZED SCOPE**: This PRD has been finalized based on user elicitation. The implementation follows **Option B: BALANCED MVP (1-2 weeks)** with specific design decisions for CSV format, Polly integration, and processing progress UI.

### Finalized Decisions Summary

| Decision Area | Finalized Choice |
|--------------|------------------|
| **CSV Format** | Single Hierarchical CSV (Option A) |
| **MVP Scope** | Option B: BALANCED MVP (1-2 weeks) |
| **Audio Engines** | eSpeak (default) + Polly (on-demand with warning) |
| **Matrix View** | Excel-filterable by Type (WORD/CHAR) |
| **Processing Progress** | Real-time step & rule progress display |

### Original vs. Refined Scope

| Aspect | Original PRD | Finalized PRD |
|--------|-------------|--------------|
| **Primary Use Case** | Comparison table + pretty UI | Debugging tool for pronunciation errors |
| **Target User** | Native speakers + developers | Primarily developers, secondary native speakers |
| **Key Feature** | Word-by-word comparison | Matrix visualization of processing layers |
| **Output Format** | JSON/CSV comparison | Hierarchical CSV (WORD + CHAR rows) |
| **Timeline** | 4 weeks (4 phases) | 1-2 weeks MVP (balanced, effective) |
| **UI/Design** | High polish | Lightweight, functional, effective |
| **Audio Engine** | eSpeak only | eSpeak (always) + Polly toggle (on-demand) |

---

## 1. Introduction / Overview

### Problem Statement

You've built a sophisticated Arabic TTS system with 6 processing layers (Diacritization → Syllabification → Phonological Processors → IPA → X-SAMPA → Audio). The last 15% of pronunciation enhancements require debugging WHERE errors occur in this pipeline. The current demo page shows final results but doesn't show the journey through each layer.

**Example error scenario:**
- Input: "صباح" (sbah/morning)
- Expected: [sˁɑbɑːħ] (emphatic, backed vowel)
- Actual: [sɑbɑːħ] (no emphasis)
- Question: Where did it fail? Diacritization? Emphatic processor? IPA mapping?

### Solution

A **matrix-based debugging tool** that shows:
1. How each word/letter progresses through each processing layer
2. What happened at each layer (syllabification result, applied rules, IPA generated, etc.)
3. Where errors occurred (comparison to expected outputs)
4. Hierarchical CSV export with both WORD and CHAR level data for analysis

### High-Level Goal

Enable developers and native speakers to validate and debug pronunciation by seeing the complete processing pathway for each word, identify error sources, and iteratively fix the remaining 15% of pronunciation challenges.

---

## 2. Goals

### Primary Goals (MVP - Must Have)

1. **Processing Layer Visibility** - Show each word/letter's transformation through ALL 6 processing layers
2. **Matrix-Based Debugging** - Display results in matrix format (word/letter × processing layers) for easy error identification
3. **Hierarchical CSV Export** - Single CSV with WORD and CHAR rows, filterable in Excel
4. **Dual Audio Engines** - Support eSpeak (default/always) + Polly toggle (on-demand/costs)
5. **Expected IPA Comparison** - Highlight differences between expected and actual IPA
6. **Processing Progress UI** - Show which step and phonological rule is being applied in real-time
7. **Lightweight & Effective** - Runs on localhost, no fancy UI, focused on functionality

### Secondary Goals (Phase 2 - Should Have)

1. Confidence scores showing certainty of processing results
2. Batch validation of multiple texts
3. localStorage history of validated texts
4. Per-layer download buttons

### What We're NOT Doing (Out of Scope for MVP)

- ❌ Fancy UI/design (keep it functional)
- ❌ Progress bars with detailed timing
- ❌ Sample text library
- ❌ Email reports or integrations
- ❌ Production deployment
- ❌ Confidence scores (deferred to Phase 2)
- ❌ Batch validation (deferred to Phase 2)

---

## 3. User Stories

**As a developer**, I want to see each word's transformation through all 6 processing layers so that I can identify where pronunciation errors occur.

**As a developer**, I want to export the processing matrix as a hierarchical CSV so that I can filter by Type (WORD/CHAR) in Excel and analyze patterns across multiple words and texts.

**As a native speaker validator**, I want to compare the expected pronunciation (IPA) with actual output so that I can validate whether the system is working correctly.

**As a system debugger**, I want to see what diacritization was applied, what syllabification happened, and what IPA was generated so that I can pinpoint which rule or processor is causing errors.

**As a researcher**, I want to test different dialects and toggle between eSpeak and Polly so that I can evaluate which engine produces better results.

**As a user**, I want to see real-time processing progress showing which step and phonological rule is being applied so that I understand what the system is doing.

---

## 4. Functional Requirements

### 4.1 Processing Layer Visualization

**FR-1.1** System MUST accept Arabic text input (diacritized or undiacritized)

**FR-1.2** System MUST display processing results for all 6 layers:
1. Original text
2. Diacritization result
3. Syllabification result
4. Phonological rules applied
5. IPA generation
6. X-SAMPA conversion

**FR-1.3** System MUST show intermediate outputs AT EACH LAYER (not just final result)

**FR-1.4** System MUST maintain processing order: Diacritization → Syllabification → Gemination → Sun Letters → Allophones → Emphatic → IPA → X-SAMPA

### 4.2 Matrix Format Display

**FR-2.1** System MUST display a matrix table with:
- **Rows:** Each word/letter from input
- **Columns:** Each processing layer (6+ columns)
- **Cells:** Output of that processing layer for that word/letter

**FR-2.2** System MUST allow toggling between:
- Word-level matrix view (Type="WORD" rows only)
- Letter-level matrix view (Type="CHAR" rows only)
- Combined view (all rows, hierarchical)

**FR-2.3** System MUST color-code or highlight differences from expected IPA values when comparison is enabled

### 4.3 Hierarchical CSV Export (FINALIZED)

**FR-3.1** System MUST export a single hierarchical CSV file with the following structure:

```csv
Type,Word,Position,Original,Diacritized,Syllable_Pattern,Syllable_Index,Syllable_Role,Phonology_Rules,IPA,X-SAMPA
WORD,صباح,-,صباح,صَبَاح,"CV.CV","-","-","emphatic_spread",sˁɑbɑːħ,s_?Aba:X\
CHAR,صباح,1-initial,ص,صَ,"-",1,onset,"emphatic_spread",sˁ,s_?
CHAR,صباح,2-medial,ب,بَ,"-",1,nucleus,"-",ɑ,A
CHAR,صباح,3-medial,ا,َا,"-",1,nucleus,"-",ɑ,A
CHAR,صباح,4-final,ح,ح,"-",2,coda,"-",ħ,X\
WORD,الخير,-,الخير,الْخَيْرِ,"CVC.CVC.CV","-","-","none",al-xajr,al-xajr
CHAR,الخير,1-initial,ا,ا,"-",1,onset,"-",a,a
...
```

**FR-3.2** CSV Column Mapping by Level:

| Column | Word-Level (Type="WORD") | Char-Level (Type="CHAR") |
|--------|--------------------------|--------------------------|
| Type | "WORD" | "CHAR" |
| Word | The word itself | Parent word (for grouping) |
| Position | "-" (not applicable) | Position index + type (e.g., "1-initial", "2-medial", "3-final") |
| Original | Original word | Original character |
| Diacritized | Diacritized word | Diacritized character |
| Syllable_Pattern | CV.CVC.CV pattern string | "-" (not applicable) |
| Syllable_Index | "-" (not applicable) | Which syllable (1, 2, 3...) |
| Syllable_Role | "-" (not applicable) | onset/nucleus/coda |
| Phonology_Rules | All rules applied to word | Rules affecting this char |
| IPA | Full IPA for word | IPA for this char |
| X-SAMPA | Full X-SAMPA for word | X-SAMPA for this char |

**FR-3.3** System MUST include timestamp and metadata in export filename (e.g., `tts_matrix_20251214_143022.csv`)

**FR-3.4** CSV MUST be filterable in Excel by Type column for word-only or char-only views

### 4.4 Dual Audio Engine Support (FINALIZED)

**FR-4.1** System MUST generate audio via eSpeak NG by default (always available, free)

**FR-4.2** System MUST provide "Generate with Polly" button as separate action (not auto-generated)

**FR-4.3** System MUST display cost warning before Polly generation:
- Modal or inline warning: "Polly costs ~$0.016 per 1000 characters. This text has X characters. Proceed?"
- User must confirm before generation

**FR-4.4** After Polly generation, system MUST show "Download Audio (Polly)" button

**FR-4.5** System MUST display which engine was used for each audio file

**FR-4.6** Workflow MUST be:
1. User submits text → Matrix displayed + CSV downloadable
2. User clicks "Generate Audio (eSpeak)" → eSpeak audio available
3. User optionally clicks "Generate with Polly" → Warning shown → Polly audio available

### 4.5 Expected IPA Comparison (FINALIZED)

**FR-5.1** System MUST accept optional expected IPA input field

**FR-5.2** System MUST highlight discrepancies between expected and actual IPA:
- Green: Matches expected
- Red: Differs from expected
- No highlight: No expected value provided

**FR-5.3** System MUST allow dialect selection (EG, MSA, Gulf, Levantine, Maghrebi)

**FR-5.4** System MUST process multiple words/sentences in single request

### 4.6 Processing Progress UI (FINALIZED)

**FR-6.1** System MUST display real-time processing progress showing:
- Current processing step (1-6)
- Step name
- For phonological rules step, show individual rule progress

**FR-6.2** Progress display format:
```
Processing Progress:
[█████░░░░░] Step 3/6: Phonological Rules
  ├─ Gemination: ✓ Complete
  ├─ Sun Letters: ✓ Complete
  ├─ Allophones: ⏳ Processing...
  └─ Emphatic: ○ Pending
```

**FR-6.3** Progress MUST update in real-time as processing occurs

**FR-6.4** Progress MUST show completion status for each sub-step

### 4.7 Non-Functional Requirements

**FR-7.1** System MUST run on localhost (no external APIs except optional Polly)

**FR-7.2** System MUST complete processing in <2 seconds per sentence

**FR-7.3** System MUST support RTL (right-to-left) text display for Arabic

**FR-7.4** System MUST not require deployment or configuration beyond `python3 app.py`

---

## 5. Design: Matrix-Based Debugging Interface

### Finalized MVP Layout

```
┌──────────────────────────────────────────────────────────────────┐
│  Arabic TTS Debugging Tool                                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Input: [Arabic text box]                            [Process]    │
│  Dialect: [EG ▼]   Expected IPA: [optional field]                │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  PROCESSING PROGRESS                                              │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │ [██████████░░░░░░░░░░] Step 3/6: Phonological Rules         │ │
│  │   ├─ Gemination: ✓ Complete                                  │ │
│  │   ├─ Sun Letters: ✓ Complete                                 │ │
│  │   ├─ Allophones: ⏳ Processing...                            │ │
│  │   └─ Emphatic: ○ Pending                                     │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  MATRIX VIEW                                                      │
│                                                                    │
│  View: [● All] [○ Words Only] [○ Characters Only]                │
│                                                                    │
│  ┌──────┬────────┬────────┬───────────┬─────────┬──────────────┐ │
│  │ Type │ Word   │Position│ Original  │Diacrit  │Syll_Pattern  │ │
│  ├──────┼────────┼────────┼───────────┼─────────┼──────────────┤ │
│  │ WORD │ صباح   │ -      │ صباح      │ صَبَاح  │ CV.CV        │ │
│  │ CHAR │ صباح   │1-init  │ ص         │ صَ      │ -            │ │
│  │ CHAR │ صباح   │2-med   │ ب         │ بَ      │ -            │ │
│  │ CHAR │ صباح   │3-med   │ ا         │ َا      │ -            │ │
│  │ CHAR │ صباح   │4-final │ ح         │ ح       │ -            │ │
│  │ WORD │ الخير  │ -      │ الخير     │الْخَيْرِ│ CVC.CVC.CV   │ │
│  │ ...  │        │        │           │         │              │ │
│  └──────┴────────┴────────┴───────────┴─────────┴──────────────┘ │
│                                                                    │
│  (Table scrolls horizontally for: Syll_Index, Syll_Role,         │
│   Phonology_Rules, IPA, X-SAMPA)                                  │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  CONTROLS                                                         │
│                                                                    │
│  [📊 Download CSV (Hierarchical)]  [📋 Copy Table]               │
│                                                                    │
│  AUDIO                                                            │
│  [🔊 Generate Audio (eSpeak)]                                    │
│  [🎤 Download Audio (eSpeak)]  ← appears after generation        │
│                                                                    │
│  [💰 Generate with Polly]  ← shows cost warning first            │
│  [🎤 Download Audio (Polly)]   ← appears after generation        │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### Key Features

| Feature | Description |
|---------|-------------|
| **Hierarchical Matrix** | Single table with WORD and CHAR rows, filterable |
| **Processing Progress** | Real-time display of current step and rule |
| **Expected IPA Comparison** | Highlights differences in red/green |
| **Dual Audio** | eSpeak (free) + Polly (on-demand with warning) |
| **CSV Export** | Single hierarchical file, Excel-filterable |

---

## 6. Implementation Scope: Option B BALANCED MVP

### Timeline: 1-2 Weeks

### Included Features ✅

- ✅ Matrix table display (word + letter levels combined)
- ✅ Hierarchical CSV export (single file, filterable by Type)
- ✅ eSpeak audio generation (always available)
- ✅ Polly toggle with cost warning (on-demand)
- ✅ Expected IPA comparison with highlighting
- ✅ Processing progress UI (step + rule display)
- ✅ Letter-level matrix with syllable role
- ✅ View toggle (All / Words Only / Characters Only)

### Deferred to Phase 2 ❌

- ❌ Confidence scores
- ❌ Batch validation
- ❌ localStorage history
- ❌ Per-layer audio buttons

---

## 7. Implementation Strategy

### Core Components

**1. Backend Enhancement (app.py)**
- Add `/process` endpoint enhancement to return layer-by-layer data
- Add `/process_with_progress` endpoint for real-time progress updates (WebSocket or SSE)
- Modify response format to include hierarchical data:
  ```json
  {
    "original_text": "صباح الخير",
    "words": [
      {
        "type": "WORD",
        "word": "صباح",
        "position": "-",
        "original": "صباح",
        "diacritized": "صَبَاح",
        "syllable_pattern": "CV.CV",
        "syllable_index": "-",
        "syllable_role": "-",
        "phonology_rules": "emphatic_spread",
        "ipa": "sˁɑbɑːħ",
        "xsampa": "s_?Aba:X\\",
        "characters": [
          {
            "type": "CHAR",
            "word": "صباح",
            "position": "1-initial",
            "original": "ص",
            "diacritized": "صَ",
            "syllable_pattern": "-",
            "syllable_index": "1",
            "syllable_role": "onset",
            "phonology_rules": "emphatic_spread",
            "ipa": "sˁ",
            "xsampa": "s_?"
          },
          // ... more characters
        ]
      },
      // ... more words
    ]
  }
  ```

**2. Frontend Redesign (templates/demo.html or templates/advanced.html)**
- Replace collapsible sections with matrix table
- Add view toggle (All / Words Only / Characters Only)
- Add processing progress display with real-time updates
- Add expected IPA input field with comparison highlighting
- Add CSV export button (hierarchical format)
- Add separate Polly button with cost warning modal
- Keep existing audio generation for eSpeak

**3. CSV Export Generator**
- Generate hierarchical CSV from layer data
- Include all 11 columns as specified
- Add timestamp to filename
- Ensure Excel compatibility (proper escaping, UTF-8 BOM)

**4. Progress Tracking**
- Add WebSocket or Server-Sent Events for real-time progress
- Track step completion (1-6)
- Track phonological rule progress (Gemination, Sun Letters, Allophones, Emphatic)
- Update frontend progress display in real-time

**5. Polly Integration**
- Add Polly button (separate from eSpeak)
- Show cost warning modal with character count
- Require user confirmation before generation
- Show download button after generation completes

---

## 8. Success Criteria

### For MVP Completion

✅ User can input Arabic text and see it processed through all 6 layers in hierarchical matrix format
✅ User can toggle between All / Words Only / Characters Only views
✅ User can see real-time processing progress with step and rule details
✅ User can identify where pronunciation errors occur by examining the matrix
✅ User can input expected IPA and see differences highlighted
✅ User can export hierarchical CSV with WORD and CHAR rows
✅ User can generate audio with eSpeak (free) or Polly (on-demand with cost warning)
✅ System runs on localhost with `python3 app.py`
✅ Processing takes <2 seconds per sentence
✅ Works with all 5 dialects

### For Validation (You will measure these)

1. **Debugging Effectiveness:** Can you spot the last 15% pronunciation issues using the matrix?
2. **Export Usefulness:** Is the hierarchical CSV format helpful for Excel analysis?
3. **Engine Preference:** Does Polly significantly improve quality over eSpeak?
4. **Progress Clarity:** Is the processing progress display helpful?
5. **Usability:** Is the tool lightweight and effective without fancy UI?

---

## 9. Acceptance Criteria

### Must Have (Non-Negotiable)

- [ ] Hierarchical matrix table displays all 6 processing layers with WORD and CHAR rows
- [ ] View toggle works (All / Words Only / Characters Only)
- [ ] Processing progress displays step and phonological rule status
- [ ] Expected IPA comparison highlights differences
- [ ] CSV export works in hierarchical format (filterable in Excel)
- [ ] eSpeak audio generation works
- [ ] Polly button available with cost warning modal
- [ ] Runs on localhost
- [ ] <2 second processing time

### Should Have (Quality)

- [ ] Real-time progress updates (WebSocket/SSE)
- [ ] Clean, functional UI (no bugs)
- [ ] Works with all 5 dialects
- [ ] Proper CSV escaping and UTF-8 support

### Could Have (Nice-to-have)

- [ ] Copy table to clipboard
- [ ] Keyboard shortcuts

---

## 10. Example Outputs

### Example Matrix View (Input: "صباح الخير")

| Type | Word | Position | Original | Diacritized | Syllable_Pattern | Syllable_Index | Syllable_Role | Phonology_Rules | IPA | X-SAMPA |
|------|------|----------|----------|-------------|------------------|----------------|---------------|-----------------|-----|---------|
| WORD | صباح | - | صباح | صَبَاح | CV.CV | - | - | emphatic_spread | sˁɑbɑːħ | s_?Aba:X\ |
| CHAR | صباح | 1-initial | ص | صَ | - | 1 | onset | emphatic_spread | sˁ | s_? |
| CHAR | صباح | 2-medial | ب | بَ | - | 1 | nucleus | - | ɑ | A |
| CHAR | صباح | 3-medial | ا | َا | - | 1 | nucleus | - | ɑ | A |
| CHAR | صباح | 4-final | ح | ح | - | 2 | coda | - | ħ | X\ |
| WORD | الخير | - | الخير | الْخَيْرِ | CVC.CVC.CV | - | - | none | al-xajr | al-xajr |
| CHAR | الخير | 1-initial | ا | ا | - | 1 | onset | - | a | a |
| CHAR | الخير | 2-medial | ل | لْ | - | 1 | coda | - | l | l |
| CHAR | الخير | 3-medial | خ | خَ | - | 2 | onset | - | x | x |
| CHAR | الخير | 4-medial | ي | يْ | - | 2 | nucleus | - | aj | aj |
| CHAR | الخير | 5-final | ر | رِ | - | 3 | coda | - | r | r |

### Example CSV Output

```csv
Type,Word,Position,Original,Diacritized,Syllable_Pattern,Syllable_Index,Syllable_Role,Phonology_Rules,IPA,X-SAMPA
WORD,صباح,-,صباح,صَبَاح,"CV.CV","-","-","emphatic_spread",sˁɑbɑːħ,s_?Aba:X\
CHAR,صباح,1-initial,ص,صَ,"-",1,onset,"emphatic_spread",sˁ,s_?
CHAR,صباح,2-medial,ب,بَ,"-",1,nucleus,"-",ɑ,A
CHAR,صباح,3-medial,ا,َا,"-",1,nucleus,"-",ɑ,A
CHAR,صباح,4-final,ح,ح,"-",2,coda,"-",ħ,X\
WORD,الخير,-,الخير,الْخَيْرِ,"CVC.CVC.CV","-","-","none",al-xajr,al-xajr
CHAR,الخير,1-initial,ا,ا,"-",1,onset,"-",a,a
CHAR,الخير,2-medial,ل,لْ,"-",1,coda,"-",l,l
CHAR,الخير,3-medial,خ,خَ,"-",2,onset,"-",x,x
CHAR,الخير,4-medial,ي,يْ,"-",2,nucleus,"-",aj,aj
CHAR,الخير,5-final,ر,رِ,"-",3,coda,"-",r,r
```

### Example Processing Progress Display

```
Processing Progress:
[████████████████░░░░] Step 5/6: IPA Generation

  Step 1: Diacritization      ✓ Complete
  Step 2: Syllabification     ✓ Complete
  Step 3: Phonological Rules  ✓ Complete
    ├─ Gemination:    ✓ Complete
    ├─ Sun Letters:   ✓ Complete
    ├─ Allophones:    ✓ Complete
    └─ Emphatic:      ✓ Complete
  Step 4: Context Rules       ✓ Complete
  Step 5: IPA Generation      ⏳ Processing...
  Step 6: X-SAMPA Conversion  ○ Pending
```

---

## 11. Next Steps (Implementation Sequence)

### Week 1: Core Implementation

**Day 1-2: Backend Enhancement**
1. Modify `/process` endpoint to return hierarchical data structure
2. Add character-level analysis with syllable role detection
3. Add phonology rules tracking per character

**Day 3-4: Frontend Matrix Display**
1. Create new matrix table component
2. Implement view toggle (All / Words / Characters)
3. Add expected IPA input and comparison highlighting

**Day 5: CSV Export**
1. Implement hierarchical CSV generator
2. Add proper escaping and UTF-8 support
3. Test Excel compatibility

### Week 2: Polish & Audio

**Day 1-2: Processing Progress**
1. Add WebSocket/SSE for real-time updates
2. Implement progress display component
3. Track individual phonological rules

**Day 3-4: Polly Integration**
1. Add Polly button with cost warning modal
2. Implement character count calculation
3. Add download button after generation

**Day 5: Testing & Refinement**
1. Test with all 5 dialects
2. Fix any bugs
3. Validate with sample texts

---

## Summary

**This PRD is now FINALIZED with the following confirmed decisions:**

1. **CSV Format:** Single hierarchical CSV with Type column (WORD/CHAR) for Excel filtering
2. **MVP Scope:** Option B - Balanced MVP with matrix display, hierarchical CSV, dual audio engines, expected IPA comparison, and processing progress
3. **Audio Strategy:** eSpeak (default/free) + Polly (on-demand with cost warning)
4. **Processing Progress:** Real-time display showing step and phonological rule status
5. **Timeline:** 1-2 weeks

**Implementation can begin immediately.**

---

**Document Version:** 3.0 (FINALIZED)
**Status:** FINALIZED - Ready for Implementation
**Date:** December 14, 2025
