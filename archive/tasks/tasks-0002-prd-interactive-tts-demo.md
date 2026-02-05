# Implementation Task List: Interactive TTS Demo
## Matrix-Based Debugging & Validation Tool for Arabic TTS

**PRD:** `/home/hamr/PycharmProjects/ArabicTTS/tasks/0002-prd-interactive-tts-demo-REFINED.md`
**Timeline:** 1-2 weeks (Option B: Balanced MVP)
**Status:** Ready for Implementation
**Date Generated:** December 14, 2025

---

## Project Overview

A **matrix-based debugging tool** that shows how each word/letter progresses through all 6 TTS processing layers. Enables developers and native speakers to identify where pronunciation errors occur.

**Key Deliverables:**
- Hierarchical matrix table (WORD + CHAR rows)
- Single CSV export with Type column (filterable in Excel)
- Dual audio engines (eSpeak default + Polly on-demand)
- Processing progress UI (real-time step/rule display)
- Expected IPA comparison with highlighting

---

## Relevant Files

### Backend Files (To Modify/Create)
- `app.py` - Flask REST API (modify `/process` endpoint)
- `src/main.py` - Core TTS pipeline (add progress tracking)
- `src/integrations/espeak.py` - eSpeak wrapper (existing)
- `src/integrations/polly.py` - Polly wrapper (may need enhancement)
- `src/core/syllabifier.py` - Syllabifier (enhance for character-level data)

### Frontend Files (To Modify/Create)
- `templates/advanced.html` - Main demo page (MODIFY for matrix view)
- `static/css/style.css` - Styling (new styles for matrix, progress, etc.)
- `static/js/matrix.js` - NEW matrix interaction logic
- `static/js/progress.js` - NEW progress tracking display

### New Utility Files
- `src/utils/csv_export.py` - NEW hierarchical CSV export utility

### Test Files
- `tests/integration/test_matrix_generation.py` - NEW tests for hierarchical data
- `tests/integration/test_csv_export.py` - NEW tests for CSV format

### Documentation
- `docs/MATRIX_DEBUG_GUIDE.md` - User guide for matrix debugger (NEW)

---

## Implementation Notes

### Architecture Decisions

1. **Hierarchical Data Structure:** JSON with WORD and CHAR level data for flexible rendering
2. **Progress Tracking:** AJAX polling every 500ms (simpler than WebSocket)
3. **Character-Level Analysis:** Enhance syllabifier to return character roles (onset/nucleus/coda)
4. **CSV Format:** Single file with Type column for Excel filtering
5. **Audio Engines:** eSpeak always available, Polly optional with cost warning

### Potential Challenges & Mitigations

| Challenge | Complexity | Mitigation |
|-----------|-----------|-----------|
| Character syllable roles | Medium | Enhance syllabifier with role detection |
| Progress tracking per rule | Medium | Add callbacks to each processor |
| CSV UTF-8 with IPA | Low | Use csv module + BOM marker |
| IPA comparison logic | Low | Simple string matching in frontend |
| Polly cost calculation | Low | Character count × $0.016/1000 |

---

# Tasks

## 1.0 Backend Enhancement & Hierarchical Data Structure
**Estimated Effort:** 6-8 hours | **Priority:** CRITICAL | **Dependencies:** None

Modifies Flask backend to return layer-by-layer processing data.

### 1.1 Enhance `/process` Endpoint to Return Hierarchical Data
**Estimated Effort:** 4 hours | **Priority:** CRITICAL | **Task Type:** Backend API

**Acceptance Criteria:**
- [ ] `/process` endpoint returns hierarchical JSON with WORD and CHAR level data
- [ ] JSON includes all 11 data fields as specified in PRD section 7
- [ ] WORD level includes: original word, diacritized, syllable pattern, IPA, X-SAMPA, rules
- [ ] CHAR level includes: position (1-initial/2-medial/N-final), syllable index, role (onset/nucleus/coda), IPA/X-SAMPA
- [ ] Maintains backward compatibility with existing endpoints
- [ ] Response matches example JSON in PRD section 7

**Files to Modify:**
- `src/main.py` - Add `process_text_hierarchical(text, dialect)` method
- `app.py` - Update `/process` endpoint

**Implementation Pattern:**
```python
# In src/main.py
def process_text_hierarchical(self, text):
    # Return structure with words array containing:
    # - WORD row: type="WORD", word, original, diacritized, syllable_pattern, ipa, xsampa, phonology_rules
    # - CHAR rows: type="CHAR", word, position, original, diacritized, syllable_index, syllable_role, ipa, xsampa, phonology_rules
```

**Testing Requirements:**
- [ ] Unit test: `test_process_hierarchical_returns_word_and_char_data()`
- [ ] Unit test: `test_character_level_data_includes_syllable_info()`
- [ ] Integration test: `test_hierarchical_response_matches_example()`

**Estimated Effort:** 4 hours
**Notes:** This is the foundation for all frontend features

---

### 1.2 Add Character-Level Analysis with Syllable Role Detection
**Estimated Effort:** 3 hours | **Priority:** HIGH | **Task Type:** Core Engine

**Acceptance Criteria:**
- [ ] Each character assigned syllable index (1, 2, 3, etc.)
- [ ] Each character assigned syllable role (onset/nucleus/coda)
- [ ] Character position determined (1-initial, 2-medial, 3-medial, N-final)
- [ ] Accuracy >95% on 25 test sentences
- [ ] No breaking changes to existing syllabifier

**Files to Modify:**
- `src/core/syllabifier.py` - Add `get_character_roles(word, syllables)` method

**Implementation Pattern:**
```python
# In src/core/syllabifier.py
def get_character_roles(word, syllables):
    # For each character in word:
    # - Determine which syllable it belongs to
    # - Determine role: onset (first consonant), nucleus (vowel), coda (final consonant)
    # - Determine position: 1-initial, 2-medial, N-final
    # Return list of character dicts with these properties
```

**Testing Requirements:**
- [ ] Unit test: `test_character_syllable_role_assignment_cv_pattern()`
- [ ] Unit test: `test_character_position_detection_initial_medial_final()`
- [ ] Integration test: `test_character_role_accuracy_25_test_sentences()`

**Estimated Effort:** 3 hours

---

### 1.3 Add Progress Tracking Infrastructure to Processing Pipeline
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Core Engine

**Acceptance Criteria:**
- [ ] Processing pipeline supports progress callbacks
- [ ] Progress tracks 6 major steps + 4 phonological sub-steps
- [ ] Progress data accessible via `/progress` endpoint
- [ ] No performance degradation (<2 sec processing maintained)

**Files to Modify:**
- `src/main.py` - Add progress tracking to ArabicTTS class
- `app.py` - Add `/progress` endpoint

**Implementation Pattern:**
```python
# In src/main.py
class ArabicTTS:
    def __init__(self):
        self.progress = {}

    def _update_progress(self, step, substep=None, status="processing"):
        # Track step completion
        # Called at key processing points
```

**Testing Requirements:**
- [ ] Unit test: `test_progress_tracking_updated_at_each_step()`
- [ ] Integration test: `test_progress_endpoint_returns_valid_status()`

**Estimated Effort:** 2 hours

---

## 2.0 Hierarchical CSV Export Generator
**Estimated Effort:** 3-4 hours | **Priority:** HIGH | **Dependencies:** Task 1.1

Creates CSV export functionality for Excel analysis.

### 2.1 Implement Hierarchical CSV Generation Utility
**Estimated Effort:** 2.5 hours | **Priority:** HIGH | **Task Type:** Backend Utility

**Acceptance Criteria:**
- [ ] CSV generator accepts hierarchical JSON from 1.1
- [ ] Outputs 11-column CSV (Type, Word, Position, Original, Diacritized, Syllable_Pattern, Syllable_Index, Syllable_Role, Phonology_Rules, IPA, X-SAMPA)
- [ ] UTF-8 encoded with BOM for Excel compatibility
- [ ] IPA and special characters properly escaped
- [ ] Filename includes timestamp (tts_matrix_YYYYMMDD_HHMMSS.csv)

**Files to Create:**
- `src/utils/csv_export.py` - HierarchicalCSVExporter class

**Files to Modify:**
- `app.py` - Add `/export-csv` endpoint

**Implementation Pattern:**
```python
# In src/utils/csv_export.py
class HierarchicalCSVExporter:
    def generate_csv(self):
        # Return CSV string with proper escaping

    def get_filename(self):
        # Return timestamped filename
```

**Testing Requirements:**
- [ ] Unit test: `test_csv_generation_includes_all_11_columns()`
- [ ] Unit test: `test_csv_utf8_encoding_with_ipa_characters()`
- [ ] Integration test: `test_csv_export_endpoint_returns_valid_csv()`

**Estimated Effort:** 2.5 hours

---

### 2.2 Test CSV Format and Excel Compatibility
**Estimated Effort:** 1 hour | **Priority:** HIGH | **Task Type:** Testing/QA

**Acceptance Criteria:**
- [ ] CSV opens correctly in Excel (Windows/Mac)
- [ ] Characters display correctly (no encoding issues)
- [ ] Type column can be filtered in Excel
- [ ] All 11 columns visible and readable
- [ ] Can be opened in Google Sheets

**Testing Procedure:**
1. Generate CSV for test phrase "صباح الخير"
2. Open in Excel (Windows and Mac)
3. Open in Google Sheets
4. Test filter on Type column
5. Verify special characters display correctly

**Testing Requirements:**
- [ ] Manual test: Excel opening and filtering
- [ ] Unit test: `test_csv_can_be_parsed_as_valid_csv()`
- [ ] Unit test: `test_csv_special_characters_escaped_correctly()`

**Estimated Effort:** 1 hour

---

## 3.0 Frontend Matrix Display & Interaction
**Estimated Effort:** 8-10 hours | **Priority:** CRITICAL | **Dependencies:** Task 1.1

Main UI component that shows processing matrix.

### 3.1 Create Matrix Table Component with Hierarchical Rows
**Estimated Effort:** 4 hours | **Priority:** CRITICAL | **Task Type:** Frontend

**Acceptance Criteria:**
- [ ] Matrix displays with 11 columns (Type, Word, Position, Original, Diacritized, Syllable_Pattern, Syllable_Index, Syllable_Role, Phonology_Rules, IPA, X-SAMPA)
- [ ] WORD rows show word-level data with bold styling
- [ ] CHAR rows indented under parent WORD row
- [ ] Table scrollable horizontally for wider columns
- [ ] RTL text displays correctly
- [ ] Works with varying text lengths

**Files to Create:**
- `static/js/matrix.js` - Matrix rendering logic
- `static/css/matrix.css` - Matrix styling

**Files to Modify:**
- `templates/advanced.html` - Add matrix table HTML

**Implementation Pattern:**
```javascript
// In static/js/matrix.js
function renderMatrix(hierarchicalData) {
    // For each word:
    //   - Create WORD row
    //   - Create CHAR rows as children
    // Append to #matrixBody
}
```

**Testing Requirements:**
- [ ] Unit test: `test_matrix_renders_with_all_11_columns()`
- [ ] Unit test: `test_matrix_displays_word_rows_correctly()`
- [ ] Integration test: `test_matrix_displayed_after_process_endpoint_call()`

**Estimated Effort:** 4 hours

---

### 3.2 Implement View Toggle (All / Words Only / Characters Only)
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Frontend

**Acceptance Criteria:**
- [ ] Three radio buttons for view selection
- [ ] "All" shows WORD and CHAR rows (default)
- [ ] "Words Only" shows only TYPE="WORD" rows
- [ ] "Characters Only" shows only TYPE="CHAR" rows
- [ ] Toggle updates table in real-time without re-fetch
- [ ] Current selection remembered (localStorage)

**Files to Modify:**
- `static/js/matrix.js` - Add filter function
- `static/css/matrix.css` - Toggle styling
- `templates/advanced.html` - Add radio buttons

**Implementation Pattern:**
```javascript
function filterMatrix(viewType) {
    // Show/hide rows based on viewType
    // Save preference to localStorage
}
```

**Testing Requirements:**
- [ ] Unit test: `test_view_toggle_filters_to_words_only()`
- [ ] Unit test: `test_view_toggle_shows_all_rows()`
- [ ] Unit test: `test_view_preference_persists_in_localstorage()`

**Estimated Effort:** 2 hours

---

### 3.3 Add Expected IPA Comparison with Highlighting
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Frontend

**Acceptance Criteria:**
- [ ] Optional "Expected IPA" input field
- [ ] When provided, compare with actual IPA from processing
- [ ] Matching IPA highlighted in green
- [ ] Mismatching IPA highlighted in red
- [ ] No highlight if expected IPA not provided
- [ ] Works for both WORD and CHAR level

**Files to Modify:**
- `static/js/matrix.js` - Add comparison logic
- `static/css/matrix.css` - Add highlighting styles
- `templates/advanced.html` - Add expected IPA input

**Implementation Pattern:**
```javascript
function updateComparison() {
    // Compare actual vs expected IPA
    // Apply green/red highlighting
}
```

**Testing Requirements:**
- [ ] Unit test: `test_matching_ipa_highlighted_in_green()`
- [ ] Unit test: `test_mismatching_ipa_highlighted_in_red()`
- [ ] Integration test: `test_comparison_updates_on_new_matrix_render()`

**Estimated Effort:** 2 hours

---

## 4.0 Processing Progress UI
**Estimated Effort:** 4-5 hours | **Priority:** HIGH | **Dependencies:** Task 1.3

Real-time progress display during processing.

### 4.1 Create Progress Display Component
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Frontend

**Acceptance Criteria:**
- [ ] Displays current step (1-6) and step name
- [ ] Shows progress bar with current step highlighted
- [ ] For phonological rules step, shows sub-steps (Gemination, Sun Letters, Allophones, Emphatic)
- [ ] Uses symbols: ✓ complete, ⏳ processing, ○ pending
- [ ] Updates in real-time as processing occurs
- [ ] Hides when processing complete

**Files to Create:**
- `static/js/progress.js` - Progress component logic
- `static/css/progress.css` - Progress styling

**Files to Modify:**
- `templates/advanced.html` - Add progress container HTML

**Implementation Pattern:**
```javascript
// In static/js/progress.js
function updateProgress(progressData) {
    // Update progress bar percentage
    // Update step status indicators
    // Update phonology substeps
}
```

**Testing Requirements:**
- [ ] Unit test: `test_progress_display_shows_all_6_steps()`
- [ ] Unit test: `test_progress_bar_percentage_calculated_correctly()`
- [ ] Integration test: `test_progress_updates_in_real_time()`

**Estimated Effort:** 2 hours

---

### 4.2 Implement Real-Time Progress Polling (AJAX)
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Frontend/Backend

**Acceptance Criteria:**
- [ ] Progress endpoint `/progress` returns current progress status
- [ ] Frontend polls `/progress` every 500ms during processing
- [ ] Progress display updates in real-time
- [ ] Polling stops when processing completes
- [ ] No errors if progress called between requests
- [ ] Works for texts up to 100 words

**Files to Modify:**
- `app.py` - Ensure `/progress` endpoint available
- `static/js/matrix.js` - Add polling functions

**Implementation Pattern:**
```javascript
function startProgressPolling() {
    // Poll /progress every 500ms
    // Update display with updateProgress()
}

function stopProgressPolling() {
    // Clear polling interval
}
```

**Testing Requirements:**
- [ ] Unit test: `test_progress_endpoint_returns_valid_json()`
- [ ] Integration test: `test_progress_polling_starts_on_process()`
- [ ] Integration test: `test_progress_polling_stops_after_completion()`

**Estimated Effort:** 2 hours

---

## 5.0 Dual Audio Engine Support
**Estimated Effort:** 4-5 hours | **Priority:** HIGH | **Dependencies:** Task 1.1

eSpeak (always) and Polly (on-demand with warning).

### 5.1 Verify eSpeak Audio Generation Functionality
**Estimated Effort:** 1 hour | **Priority:** HIGH | **Task Type:** Integration

**Acceptance Criteria:**
- [ ] eSpeak audio generation works with current backend
- [ ] Audio files generated correctly (WAV format, 22050 Hz, mono)
- [ ] Processing time <2 seconds per sentence
- [ ] Works with all 5 dialects
- [ ] No breaking changes

**Files to Test:**
- `src/integrations/espeak.py`
- `app.py` audio endpoints

**Testing Procedure:**
1. Test audio generation with test text
2. Verify WAV file returned
3. Play audio and verify quality
4. Test all 5 dialects
5. Measure generation time

**Estimated Effort:** 1 hour

---

### 5.2 Implement Polly Button with Cost Warning Modal
**Estimated Effort:** 2.5 hours | **Priority:** HIGH | **Task Type:** Frontend/Backend

**Acceptance Criteria:**
- [ ] Separate "Generate with Polly" button (distinct from eSpeak)
- [ ] Shows cost warning modal before generation
- [ ] Modal displays character count and estimated cost
- [ ] User must click "Confirm" to proceed
- [ ] Cancel button allows skipping Polly generation
- [ ] After generation, "Download Audio (Polly)" button appears
- [ ] Audio generation happens in background

**Files to Modify:**
- `templates/advanced.html` - Add Polly button and modal
- `static/css/style.css` - Add modal styles
- `static/js/matrix.js` - Add Polly functions
- `app.py` - Add Polly generation endpoints

**Implementation Pattern:**
```javascript
function showPollyWarning() {
    // Calculate character count
    // Calculate estimated cost ($0.016 per 1000 chars)
    // Show modal with details
}

function confirmPollyGeneration() {
    // Call /generate-polly-audio endpoint
    // Show download button when complete
}
```

**Testing Requirements:**
- [ ] Unit test: `test_polly_button_opens_warning_modal()`
- [ ] Unit test: `test_cost_calculation_is_accurate()`
- [ ] Integration test: `test_polly_modal_confirms_and_generates_audio()`

**Estimated Effort:** 2.5 hours

---

### 5.3 Add Audio Download Buttons and Engine Display
**Estimated Effort:** 1 hour | **Priority:** MEDIUM | **Task Type:** Frontend

**Acceptance Criteria:**
- [ ] Download buttons appear after audio generation (not before)
- [ ] Audio files downloadable with meaningful names
- [ ] Button labels indicate which engine used
- [ ] UI clearly shows which audio from which engine
- [ ] Works on different browsers
- [ ] Downloaded files play correctly

**Files to Modify:**
- `static/js/matrix.js` - Download functions
- `templates/advanced.html` - Button display logic

**Implementation Pattern:**
```javascript
async function downloadAudio(engine) {
    // Fetch audio from appropriate endpoint
    // Trigger download with filename: audio_{engine}_{timestamp}.wav
}
```

**Testing Requirements:**
- [ ] Unit test: `test_espeak_download_button_appears_after_generation()`
- [ ] Integration test: `test_downloaded_audio_files_play_correctly()`

**Estimated Effort:** 1 hour

---

## 6.0 Integration, Testing & Polish
**Estimated Effort:** 6-8 hours | **Priority:** CRITICAL | **Dependencies:** Tasks 1.0-5.0

Final integration and quality assurance.

### 6.1 End-to-End Testing of Complete Feature Set
**Estimated Effort:** 3 hours | **Priority:** CRITICAL | **Task Type:** Testing

**Acceptance Criteria:**
- [ ] User can input text and see matrix with all 6 layers
- [ ] View toggle works (All / Words / Characters)
- [ ] Expected IPA comparison works with highlighting
- [ ] CSV export downloads valid hierarchical CSV
- [ ] eSpeak audio generation works
- [ ] Polly warning shows correctly
- [ ] Polly audio generation works (if AWS configured)
- [ ] Processing progress displays accurately
- [ ] No console errors during normal operation
- [ ] No UI crashes or frozen buttons

**Test Procedures:**
1. **Matrix display test:** Input "صباح الخير" → verify all columns, WORD rows, CHAR rows
2. **View toggle test:** Test All/Words/Characters views
3. **Expected IPA test:** Test highlighting with correct and incorrect IPA
4. **CSV export test:** Download and open in Excel → verify filtering
5. **Audio generation test:** Generate eSpeak and Polly audio
6. **Progress test:** Watch progress display during processing

**Testing Requirements:**
- [ ] Integration test: `test_complete_workflow_matrix_to_download()`
- [ ] Integration test: `test_all_5_dialects_produce_valid_output()`
- [ ] Integration test: `test_ui_remains_responsive_during_processing()`

**Estimated Effort:** 3 hours

---

### 6.2 Test with All 5 Dialects
**Estimated Effort:** 2 hours | **Priority:** HIGH | **Task Type:** Testing

**Acceptance Criteria:**
- [ ] System processes text in all 5 dialects (EG, MSA, Gulf, Levantine, Maghrebi)
- [ ] Dialect selector works correctly
- [ ] Matrix displays correctly for each dialect
- [ ] Expected IPA comparison works for each dialect
- [ ] Audio generation works for each dialect

**Test Dialects:**
1. EG: "صباح الخير"
2. MSA: "الحمد لله"
3. GULF: Gulf-specific test phrase
4. LEV: Levantine-specific test phrase
5. MAG: Maghrebi-specific test phrase

**Testing Requirements:**
- [ ] Integration test: `test_egyptian_dialect_processing()`
- [ ] Integration test: `test_msa_dialect_processing()`
- [ ] Integration test: `test_all_dialects_produce_valid_output()`

**Estimated Effort:** 2 hours

---

### 6.3 Performance Validation
**Estimated Effort:** 1 hour | **Priority:** HIGH | **Task Type:** Testing/QA

**Acceptance Criteria:**
- [ ] Processing time <2 seconds per sentence
- [ ] CSV export completes in <1 second
- [ ] Progress polling doesn't degrade performance
- [ ] No memory leaks after 10+ requests
- [ ] UI remains responsive during processing
- [ ] Works with text up to 500 words

**Performance Benchmarks:**

| Operation | Target | Method |
|-----------|--------|--------|
| Process single word | <500ms | Browser dev tools timing |
| Process sentence (10 words) | <1s | Clock from button click |
| Process paragraph (50 words) | <2s | Clock from button click |
| CSV export | <1s | Clock from download |
| Progress polling | <50ms per poll | Network tab monitoring |

**Testing Requirements:**
- [ ] Performance test: `test_processing_time_less_than_2_seconds()`
- [ ] Performance test: `test_no_memory_leaks_after_multiple_requests()`

**Estimated Effort:** 1 hour

---

### 6.4 Bug Fixes & Polish
**Estimated Effort:** 1-2 hours | **Priority:** MEDIUM | **Task Type:** QA/Polish

**Acceptance Criteria:**
- [ ] All known bugs fixed
- [ ] No console errors
- [ ] UI consistent across browsers
- [ ] RTL text displays correctly throughout
- [ ] Error messages are clear and helpful
- [ ] All buttons clickable and responsive
- [ ] Code is clean and well-commented

**Bug Categories to Test:**
1. **Text Input:** Empty, very long, mixed Arabic/English
2. **Display:** Table wrapping, modal sizing, color contrast
3. **Interaction:** Unresponsive buttons, modal closing, downloads
4. **Data:** IPA display, X-SAMPA escaping, UTF-8 encoding

**Testing Requirements:**
- [ ] Cross-browser test: Chrome, Firefox, Safari, Edge
- [ ] Mobile responsiveness test
- [ ] Accessibility test
- [ ] Manual QA pass of all features

**Estimated Effort:** 1-2 hours

---

## Summary of Files

### Files to Create (8 total)
1. `src/utils/csv_export.py` - CSV export utility
2. `static/js/matrix.js` - Matrix rendering and interaction
3. `static/js/progress.js` - Progress tracking display
4. `static/css/matrix.css` - Matrix table styling
5. `static/css/progress.css` - Progress display styling
6. `tests/integration/test_matrix_generation.py` - Matrix tests
7. `tests/integration/test_csv_export.py` - CSV export tests
8. `docs/MATRIX_DEBUG_GUIDE.md` - User documentation

### Files to Modify (5 total)
1. `src/main.py` - Add hierarchical processing, progress tracking, character-level analysis
2. `src/core/syllabifier.py` - Add character role detection
3. `app.py` - Update `/process` endpoint, add `/progress`, `/export-csv`, audio endpoints
4. `templates/advanced.html` - Add matrix display, progress, controls
5. `static/css/style.css` - General styling updates

---

## Effort Estimation Summary

| Parent Task | Estimated Hours | Priority |
|-----------|-------------------|----------|
| 1.0 Backend Enhancement | 6-8 | CRITICAL |
| 2.0 CSV Export | 3-4 | HIGH |
| 3.0 Matrix Display | 8-10 | CRITICAL |
| 4.0 Processing Progress | 4-5 | HIGH |
| 5.0 Dual Audio Engines | 4-5 | HIGH |
| 6.0 Integration & Testing | 6-8 | CRITICAL |
| **TOTAL** | **31-40 hours** | - |

**Timeline:** 1-2 weeks (assumes 20-25 hours/week development)

---

## Dependencies & Execution Order

**Critical Path:**
1. Task 1.0 (Backend Enhancement) - Must complete first
2. Task 2.0 (CSV Export) - Depends on 1.0
3. Task 3.0 (Matrix Display) - Depends on 1.0
4. Task 4.0 (Progress UI) - Depends on 1.3
5. Task 5.0 (Audio Engines) - Mostly independent
6. Task 6.0 (Testing) - Last, integrates everything

**Parallel Work Possible:**
- Tasks 2.0, 3.0, 5.0 can proceed in parallel after 1.0 completes
- Task 4.0 can proceed after 1.3 completes
- Task 6.0 should be last

---

## Definition of Done

A task is complete when:
1. All acceptance criteria are met
2. All testing requirements pass
3. Code is reviewed and cleaned
4. Documentation is updated
5. No known bugs exist
6. Related code doesn't break existing functionality

---

**Document Version:** 2.0 (Comprehensive Implementation Breakdown)
**Status:** Ready for Implementation
**Date Generated:** December 14, 2025

