---
name: Interactive TTS Processing Demo Page
version: 1.0
date: 2025-01-14
status: Draft
priority: High
---

# PRD: Interactive Arabic TTS Processing Demo Page

## 1. Introduction/Overview

### Problem Statement
The Arabic TTS system currently lacks a visual, step-by-step interface for observing the complete processing pipeline in action. Developers and quality testers need an easy way to:
- Identify mistakes in diacritization and X-SAMPA conversion
- Validate each processing step independently
- Compare before/after states at each stage
- Test audio output from both eSpeak NG and Amazon Polly

### Solution
Create an interactive HTML page that visualizes the entire TTS processing pipeline with downloadable outputs at each step, enabling efficient debugging and quality testing.

### High-Level Goal
Build an internal debugging and quality testing tool that makes it easy to spot processing errors in diacritization or X-SAMPA conversion, with full transparency into each pipeline stage.

---

## 2. Goals

### Primary Goals
1. **Quality Testing Tool** - Provide an easy way to spot code mistakes in diacritization and X-SAMPA conversion
2. **Pipeline Transparency** - Visualize all processing steps: Diacritization → Syllabification → 4 Phonological Processors → IPA → X-SAMPA → Audio
3. **Step-by-Step Validation** - Allow downloading outputs at each stage for detailed review
4. **Audio Testing** - Enable testing with both eSpeak NG (default) and Amazon Polly (optional)

### Secondary Goals
1. Support multiple input methods (paste text, upload file)
2. Enable native Arabic speakers to validate pronunciation accuracy
3. Provide side-by-side before/after comparison for diacritization
4. Support all 5 dialects (MSA, Egyptian, Gulf, Levantine, Maghrebi)

### Success Criteria
- Developers can identify processing errors within 5 minutes of testing
- All pipeline steps are visible with downloadable outputs
- Audio playback works inline with download option
- Native speakers can validate outputs easily

---

## 3. User Stories

### As a Developer (Primary User)
1. **As a developer**, I want to paste Arabic text and see step-by-step processing so that I can identify where errors occur
2. **As a developer**, I want to download outputs at each stage so that I can analyze them in detail
3. **As a developer**, I want to see before/after diacritization side-by-side so that I can validate mishkal's output
4. **As a developer**, I want to spot X-SAMPA conversion mistakes easily so that I can fix phonological rules
5. **As a developer**, I want to test with both eSpeak and Polly so that I can compare audio quality
6. **As a developer**, I want to see partial results if processing fails so that I can debug the specific failing step

### As a Native Arabic Speaker (Validator)
1. **As a native speaker**, I want to listen to generated audio inline so that I can validate pronunciation
2. **As a native speaker**, I want to see the IPA representation so that I can understand how sounds are mapped
3. **As a native speaker**, I want to test different dialects so that I can validate dialect-specific rules
4. **As a native speaker**, I want to download word-by-word CSV so that I can review systematically

### As a Technical Team Member
1. **As a team member**, I want to upload text files for batch testing so that I can test multiple examples
2. **As a team member**, I want clear error messages so that I can understand what went wrong
3. **As a team member**, I want retry/fallback options so that I can continue testing after errors
4. **As a team member**, I want progress indicators so that I know which step is running

---

## 4. Functional Requirements

### 4.1 Input Methods
**FR-1.1** The system MUST accept Arabic text via paste (textarea)
**FR-1.2** The system MUST accept Arabic text via file upload (.txt)
**FR-1.3** The system MUST provide dialect selection dropdown with options: MSA, EG, Gulf, Levant, Maghrebi
**FR-1.4** The system MUST default to MSA dialect if none selected
**FR-1.5** The system MUST provide clear "Process" button to trigger on-demand processing

### 4.2 Processing Pipeline Visualization
**FR-2.1** The system MUST display progress bar showing: "Diacritization → Syllabification → 4 Phonological Processors → IPA → X-SAMPA → Audio"
**FR-2.2** The system MUST highlight the current processing step in the progress bar
**FR-2.3** The system MUST show completion status (✓) for completed steps
**FR-2.4** The system MUST display processing time for each step
**FR-2.5** The system MUST show visual indicators (spinner/loading) during processing

### 4.3 Step-by-Step Output Display
**FR-3.1** The system MUST display outputs in collapsible details sections for each step:
- Diacritization output
- Syllabification output
- Phonological processing output (4 processors)
- IPA generation output
- X-SAMPA conversion output
- Audio generation output

**FR-3.2** The system MUST show JSON data in formatted, readable view
**FR-3.3** The system MUST provide "Download" button for each step's output
**FR-3.4** The system MUST enable syntax highlighting for JSON outputs
**FR-3.5** The system MUST show input/output comparison in each collapsible section

### 4.4 Diacritization Visualization
**FR-4.1** The system MUST show before/after diacritization side-by-side in a table
**FR-4.2** The system MUST display word-by-word comparison (original → diacritized → X-SAMPA)
**FR-4.3** The system MUST provide downloadable CSV with columns: Original, Diacritized, X-SAMPA
**FR-4.4** The system MUST highlight differences between before/after text
**FR-4.5** The system MUST show diacritization confidence scores if available

### 4.5 Audio Generation & Playback
**FR-5.1** The system MUST default to eSpeak NG for audio generation
**FR-5.2** The system MUST provide checkbox/toggle to enable Amazon Polly
**FR-5.3** The system MUST play audio inline with HTML5 audio player
**FR-5.4** The system MUST provide "Download WAV" button for eSpeak output
**FR-5.5** The system MUST provide "Download MP3" button for Polly output
**FR-5.6** The system MUST show audio duration and file size
**FR-5.7** The system MUST display audio generation status (generating/ready/failed)

### 4.6 Error Handling & Debugging
**FR-6.1** The system MUST show partial results if processing fails at any step
**FR-6.2** The system MUST display clear error messages for each failed step
**FR-6.3** The system MUST provide "Retry" button for failed steps
**FR-6.4** The system MUST offer fallback to eSpeak if Polly fails
**FR-6.5** The system MUST log errors to browser console for debugging
**FR-6.6** The system MUST highlight problematic text segments when errors occur
**FR-6.7** The system MUST suggest fixes for common errors (e.g., missing diacritics)

### 4.7 Quality Testing Features
**FR-7.1** The system MUST highlight potential diacritization errors (low confidence)
**FR-7.2** The system MUST highlight potential X-SAMPA conversion issues
**FR-7.3** The system MUST show phonological rule application details
**FR-7.4** The system MUST provide comparison view between expected and actual IPA
**FR-7.5** The system MUST enable copying outputs for external validation tools

### 4.8 Testing & Validation Support
**FR-8.1** The system MUST support processing multiple test sentences in sequence
**FR-8.2** The system MUST save processing history in browser (localStorage)
**FR-8.3** The system MUST provide "Clear All" button to reset interface
**FR-8.4** The system MUST show processing statistics (success rate, errors)
**FR-8.5** The system MUST export full test results as JSON

---

## 5. Non-Goals (Out of Scope)

### Explicitly Out of Scope
**NG-1** Real-time processing (on keystroke) - Only on-demand via button
**NG-2** Multi-user authentication - Internal tool, single-user session
**NG-3** Cloud storage of results - All processing is local/session-based
**NG-4** Advanced audio editing features - Only playback and download
**NG-5** Production audiobook generation - This is a testing/debugging tool
**NG-6** Batch processing of large corpora - Focus on single text/file testing
**NG-7** API rate limiting - Not needed for internal tool
**NG-8** Mobile-responsive design - Desktop-first for development use
**NG-9** Prosody visualization - Post-MVP enhancement
**NG-10** Custom voice training - Use existing eSpeak/Polly voices

---

## 6. Design Considerations

### 6.1 User Interface Layout

**Page Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│ Header: "Arabic TTS Interactive Processing Demo"           │
├─────────────────────────────────────────────────────────────┤
│ Input Section:                                              │
│  - Textarea (Arabic text) OR File upload                   │
│  - Dialect dropdown: [MSA|EG|Gulf|Levant|Maghrebi]        │
│  - Audio engine: [✓ eSpeak NG] [☐ Amazon Polly]          │
│  - [Process] button                                         │
├─────────────────────────────────────────────────────────────┤
│ Progress Bar:                                               │
│  Diacritization → Syllabification → Processors → IPA       │
│       ↓               ↓                ↓           ↓        │
│      ✓               ⏳               ○           ○         │
├─────────────────────────────────────────────────────────────┤
│ Output Section (Collapsible Details):                      │
│                                                             │
│  ▼ 1. Diacritization Output                               │
│     Before/After Table | Download CSV                      │
│                                                             │
│  ▼ 2. Syllabification Output                              │
│     JSON View | Download JSON                              │
│                                                             │
│  ▼ 3. Phonological Processing (4 steps)                   │
│     Gemination → Sun Letters → Allophones → Emphatic      │
│     JSON View | Download JSON                              │
│                                                             │
│  ▼ 4. IPA Generation                                       │
│     IPA Text | Download JSON                               │
│                                                             │
│  ▼ 5. X-SAMPA Conversion                                   │
│     X-SAMPA Text | Download JSON                           │
│                                                             │
│  ▼ 6. Audio Generation                                     │
│     [▶ Play] | Download WAV/MP3                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Visual Design Principles
- **Clarity First** - Each step clearly labeled and separated
- **Progressive Disclosure** - Collapsible sections to reduce clutter
- **Error Highlighting** - Red borders/text for errors, yellow for warnings
- **Success Indicators** - Green checkmarks for completed steps
- **Diff Highlighting** - Color-coded before/after comparisons

### 6.3 Interaction Patterns
- Click collapsible headers to expand/collapse sections
- Hover tooltips for technical terms (IPA, X-SAMPA, etc.)
- Copy-to-clipboard buttons for outputs
- Drag-and-drop for file upload
- Keyboard shortcuts: Ctrl+Enter to process

---

## 7. Technical Considerations

### 7.1 Frontend Technology Stack

| Component | Technology | Rationale |
|-----------|------------|-----------|
| **HTML** | HTML5 | Modern features (audio, details tags) |
| **CSS** | CSS3 with Flexbox/Grid | Responsive layout |
| **JavaScript** | Vanilla JS | No framework needed for this scope |
| **Icons** | Unicode/Emoji or simple SVG | Lightweight, no external deps |
| **Audio** | HTML5 `<audio>` element | Native browser support |

### 7.2 Backend Integration

**Existing Flask Endpoints:**
- `POST /parse` - Returns JSON with syllabification + IPA
- `POST /generate_audio` - Generates audio (eSpeak or Polly)
- `GET /download/audio/<filename>` - Downloads WAV/MP3

**New Endpoints Needed:**
- `POST /process_with_steps` - Returns step-by-step outputs
- `POST /validate_diacritization` - Returns diacritization confidence scores
- `POST /process_polly` - Separate endpoint for Polly to avoid breaking eSpeak

### 7.3 Data Flow

```
User Input (Text/File + Dialect)
    ↓
JavaScript: Send to /process_with_steps
    ↓
Backend: Process step-by-step
    ├─ Step 1: Diacritization (mishkal)
    ├─ Step 2: Syllabification
    ├─ Step 3: Phonological rules (4 processors)
    ├─ Step 4: IPA generation
    ├─ Step 5: X-SAMPA conversion
    └─ Step 6: Audio generation (eSpeak/Polly)
    ↓
Backend: Return JSON with all step outputs
    ↓
JavaScript: Populate UI step-by-step
    ↓
User: Review, download, validate
```

### 7.4 File Format Specifications

**CSV Format (Diacritization):**
```csv
Original,Diacritized,X-SAMPA
مرحبا,مَرْحَبًا,marHaban
بك,بِكَ,bika
```

**JSON Format (Step Outputs):**
```json
{
  "step": "diacritization",
  "input": "مرحبا",
  "output": "مَرْحَبًا",
  "metadata": {
    "confidence": 0.95,
    "processing_time_ms": 150
  }
}
```

### 7.5 Error Handling Strategy

| Error Type | Detection | UI Response | Recovery |
|------------|-----------|-------------|----------|
| **Invalid input** | Backend validation | Red border + message | Clear, retry |
| **Diacritization failure** | mishkal error | Show partial + error | Skip, continue |
| **Syllabification error** | Pattern not found | Highlight word + error | Show raw, continue |
| **Polly API failure** | HTTP error | Fallback to eSpeak | Auto-retry once |
| **Network timeout** | Frontend timeout | Spinner + retry button | Manual retry |

### 7.6 Performance Considerations

| Aspect | Target | Optimization |
|--------|--------|-------------|
| **Processing Time** | <3 sec per sentence | Backend caching |
| **UI Responsiveness** | <100ms to first paint | Lazy-load collapsible sections |
| **Audio Generation** | <5 sec | Stream audio if possible |
| **File Upload** | <1 sec for 1KB file | Client-side validation first |

### 7.7 Browser Compatibility

**Minimum Requirements:**
- Chrome 90+ (primary)
- Firefox 88+ (secondary)
- Safari 14+ (if needed)
- No IE support

**Required Features:**
- `<details>` tag (collapsible sections)
- `<audio>` tag (inline playback)
- CSS Grid/Flexbox
- `fetch` API
- LocalStorage

---

## 8. Success Metrics

### 8.1 Usability Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Time to Identify Error** | <5 min | Developer testing |
| **Steps to Download Output** | ≤2 clicks | UI interaction count |
| **Processing Success Rate** | >95% | Backend logs |
| **Audio Playback Success** | >98% | Frontend logs |
| **Error Message Clarity** | >80% understood | User feedback |

### 8.2 Technical Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Page Load Time** | <2 sec | Browser DevTools |
| **Processing Latency** | <3 sec/sentence | Backend timing |
| **Audio Generation Time** | <5 sec | Backend timing |
| **CSV Download Size** | <100KB | File size check |
| **JSON Output Size** | <500KB | Response size |

### 8.3 Quality Testing Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Diacritization Errors Spotted** | >90% detection | Manual validation |
| **X-SAMPA Errors Spotted** | >90% detection | Manual validation |
| **False Positive Error Highlights** | <10% | Developer feedback |
| **Native Speaker Validation Time** | <10 min per test | User timing |

### 8.4 Developer Satisfaction

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Tool Usage Frequency** | Daily | Usage logs |
| **Would Recommend** | >80% | Survey |
| **Time Saved vs Manual Testing** | >50% | Comparison study |
| **Bug Discovery Rate** | +30% | Issue tracker |

---

## 9. Open Questions

### 9.1 Technical Questions

**Q1:** Should we implement WebSockets for real-time progress updates or is HTTP polling sufficient?
**Status:** Open - HTTP polling simpler for MVP, WebSockets if latency issues

**Q2:** How should we handle very long texts (>1000 words)?
**Status:** Open - Define max length, paginate results, or warn user

**Q3:** Should audio files be cached server-side or generated on-demand every time?
**Status:** Open - Caching could improve performance but needs storage strategy

**Q4:** What's the fallback behavior if both eSpeak AND Polly fail?
**Status:** Open - Show error but allow downloading IPA/X-SAMPA for manual testing?

**Q5:** Should we support exporting the entire processing report as PDF?
**Status:** Open - Nice-to-have, defer to Phase 2

### 9.2 UX Questions

**Q6:** Should collapsible sections be expanded by default or collapsed?
**Status:** Open - Collapsed for cleaner initial view, but configurable?

**Q7:** How should we indicate "low confidence" diacritization (color, icon, tooltip)?
**Status:** Open - Yellow highlight + tooltip with confidence score?

**Q8:** Should we provide sample texts for quick testing?
**Status:** Open - Yes, add "Load Example" button with 5 sample sentences

**Q9:** How granular should the progress bar be (6 steps vs 10+ sub-steps)?
**Status:** Open - Start with 6 main steps, expand if users want more detail

### 9.3 Quality Testing Questions

**Q10:** What constitutes a "mistake" in diacritization that should be highlighted?
**Status:** Open - Define threshold (confidence <80%? Ambiguous cases?)

**Q11:** Should we compare against known-good reference outputs?
**Status:** Open - Good idea, need to create reference dataset first

**Q12:** How should we handle dialect-specific validation (different rules for MSA vs EG)?
**Status:** Open - Separate validation rules per dialect, or unified?

### 9.4 Integration Questions

**Q13:** Do we need to update the backend `/parse` endpoint or create a new one?
**Status:** Open - Recommend new `/process_with_steps` endpoint to preserve existing API

**Q14:** Should this page replace the existing `index.html` or be a separate `/demo` route?
**Status:** Open - Separate route (`/demo` or `/testing`) to keep simple UI for users

**Q15:** How do we handle Polly AWS credentials in the frontend (don't expose)?
**Status:** Open - Backend-only, frontend just toggles Polly on/off, backend handles auth

---

## 10. Implementation Phases

### Phase 1: Core Functionality (Week 1)
- Basic HTML page with input (paste + file upload)
- Dialect selection dropdown
- Processing button + progress bar
- Display JSON outputs in collapsible sections
- Download JSON buttons
- eSpeak audio playback + download

**Deliverable:** Working demo with eSpeak, all steps visible

### Phase 2: Diacritization Features (Week 2)
- Before/after diacritization table
- Word-by-word comparison
- Downloadable CSV export
- Highlight differences
- Show confidence scores

**Deliverable:** Full diacritization transparency

### Phase 3: Polly Integration (Week 3)
- Add Polly toggle option
- Create `/process_polly` endpoint
- MP3 playback + download
- Fallback to eSpeak on error
- Compare eSpeak vs Polly

**Deliverable:** Dual audio engine support

### Phase 4: Quality Testing Features (Week 4)
- Error highlighting (diacritization, X-SAMPA)
- Validation indicators
- Sample text loader
- Processing history (localStorage)
- Export full report

**Deliverable:** Complete quality testing tool

---

## 11. Acceptance Criteria

### Must Have (MVP)
- [ ] User can paste Arabic text and select dialect
- [ ] User can upload .txt file
- [ ] Progress bar shows all 6 steps
- [ ] Each step displays output in collapsible section
- [ ] User can download JSON at each step
- [ ] Diacritization shows before/after table
- [ ] User can download word-by-word CSV
- [ ] eSpeak audio plays inline
- [ ] User can download WAV file
- [ ] Errors show partial results with clear messages
- [ ] All 5 dialects supported (MSA, EG, Gulf, Levant, Maghrebi)

### Should Have (Phase 2)
- [ ] Polly audio generation works
- [ ] Polly MP3 download available
- [ ] Fallback to eSpeak if Polly fails
- [ ] Confidence scores shown for diacritization
- [ ] X-SAMPA errors highlighted
- [ ] Sample texts available ("Load Example")
- [ ] Processing history saved in browser

### Could Have (Future)
- [ ] WebSocket real-time updates
- [ ] PDF export of full report
- [ ] Reference output comparison
- [ ] Dialect-specific validation rules
- [ ] Batch processing multiple files

---

## 12. Dependencies

### External Dependencies
- Flask backend (existing)
- mishkal v0.4.1 (existing)
- eSpeak NG v1.50 (existing)
- Amazon Polly via boto3 (existing)
- ArabicTTS processing pipeline (existing)

### New Dependencies
- None required for frontend (vanilla JS)
- May need `python-csv` for CSV generation (check if included)

### Blockers
- Amazon Polly integration must be stable before Phase 3
- Backend `/process_with_steps` endpoint must be created
- Sample text dataset should be prepared

---

## 13. Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Polly API failures** | Medium | High | Fallback to eSpeak, retry logic |
| **Large file crashes browser** | Low | Medium | Limit file size to 100KB, validate upfront |
| **Processing timeout** | Low | Medium | Set 30s timeout, show partial results |
| **Diacritization errors mislead** | Medium | Low | Show confidence scores, allow manual review |
| **Cross-browser compatibility** | Low | Low | Test in Chrome first, Firefox second |
| **Security: XSS in Arabic text** | Low | High | Sanitize all text inputs, use textContent not innerHTML |

---

## Appendix A: User Feedback from Discovery

**Key Insights:**
1. **Critical:** "This needs to be an easy place for quality testing and to spot where the code has made mistakes, which can be spotted in diacritization or x-sampa"
2. User wants downloadable outputs at each step for offline review
3. Progress bar with named steps is important (not just generic "processing...")
4. Side-by-side before/after diacritization table is critical for validation
5. Both eSpeak (default) and Polly (optional) needed for comparison
6. Error handling should show partial results (don't fail entirely)

---

## Appendix B: Technical Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (HTML/JS)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Input → Process Button → Fetch /process_with_steps        │
│                                                             │
│  Progress Bar (live updates)                                │
│                                                             │
│  Output Sections:                                           │
│   ├─ Diacritization (before/after table, CSV download)     │
│   ├─ Syllabification (JSON view, download)                 │
│   ├─ Phonological (4 steps, JSON view, download)           │
│   ├─ IPA (text view, download)                             │
│   ├─ X-SAMPA (text view, download)                         │
│   └─ Audio (play, download WAV/MP3)                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
                      HTTP POST
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Backend (Flask + Python)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /process_with_steps endpoint:                             │
│                                                             │
│  1. Receive: { text, dialect, use_polly }                  │
│  2. Process:                                                │
│     ├─ Diacritization (mishkal)                            │
│     ├─ Syllabification (ArabicTTS)                         │
│     ├─ Phonological rules (4 processors)                   │
│     ├─ IPA generation                                       │
│     ├─ X-SAMPA conversion                                   │
│     └─ Audio (eSpeak or Polly)                             │
│  3. Return: { step1: {...}, step2: {...}, ..., audio_url } │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
                      Response JSON
                           ↓
                 Frontend displays results
```

---

**END OF PRD**

**Next Steps:**
1. Review and approve PRD
2. Create implementation tasks (invoke `2-generate-tasks` agent)
3. Develop backend `/process_with_steps` endpoint
4. Build frontend HTML page
5. Test with sample Arabic texts
6. Iterate based on developer feedback
